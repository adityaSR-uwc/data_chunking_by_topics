import os
import requests
import json
import logging
import shutil
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

total_tokens_sent = 0
total_tokens_received = 0

MAX_FILENAME_LENGTH = 255
CHUNK_SIZE = 2000  # Define the chunk size
OVERLAP_SIZE = 200  # Define the overlap size

load_dotenv()

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_API_KEY}"
}

def create_messages(system_url, user_url, input_data):
    """Create messages for API request."""
    system_content = system_url
    user_file_content = user_url

    system_message = {"role": "system", "content": system_content}
    user_message = {"role": "user", "content": user_file_content + "\n" + input_data}
    return [system_message, user_message]

def get_unique_filename(directory, base_filename):
    """Generate a unique filename by appending a counter if the file already exists."""
    counter = 1
    filename = base_filename
    filepath = os.path.join(directory, filename)
    
    # Increment the counter until a unique filename is found
    while os.path.exists(filepath):
        filename = f"{os.path.splitext(base_filename)[0]}_{counter}{os.path.splitext(base_filename)[1]}"
        filepath = os.path.join(directory, filename)
        counter += 1
    
    return filename

def extract_information_from_text(text):
    global total_tokens_sent, total_tokens_received

    logging.info("Preparing the request payload.")

    prompt_3 = """ system
    # Objective:
    You are an AI language model tasked with extracting topics and their related text from a given document. 

    Your task is to identify distinct topics based on the content of the document. For each identified topic, extract **all** relevant information exactly as it appears in the document, without summarizing or altering the text. Each piece of information should be placed under the appropriate topic header.

    # Output Format:
    The output should be structured in the following format:

    Topic_[Name of Topic_1]
    [All information related to this topic, including any subtopics or examples, exactly as they appear in the document.]

    If there are multiple topics, the output should continue with:

    Topic_[Name of Another Topic_2]
    [All information related to this second topic, exactly as it appears in the document.]

    Ensure that:
    1. **No information is summarized or omitted** during extraction.
    2. Each topic is distinct and clearly separated.
    3. Subtopics or examples are grouped under the relevant main topic.
    4. The information is copied verbatim from the document, retaining the original wording, structure, and details.
    5. Every topic starts with "Topic_"

    Output only the extracted topics and their full content. Do not include any code, explanations, or implementation details. Please ensure the output is clear, well-organized, and strictly follows the specified format.

    user
    """

    user_url = ""
    
    messages = create_messages(prompt_3, user_url, text)

    response = requests.post(
        f"{OPENAI_BASE_URL}/chat/completions",
        json={
            "model": DEFAULT_MODEL,
            "messages": messages,
            "temperature": 0.0,
            "top_p": 1,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
        },
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
        timeout=150
    )

    logging.info("Sending request to the API.")
    response.raise_for_status()
    print(response.json()["choices"][0]["message"]["content"])

    if response.status_code == 200:
        logging.info("API request successful.")
        logging.info(f"API Response: {response.json()}")  # Log the full response

        token_usage = response.json().get("usage", {})
        total_tokens_sent += token_usage.get("prompt_tokens", 0)
        total_tokens_received += token_usage.get("completion_tokens", 0)

        return response.json()
    else:
        logging.error(f"Error: {response.status_code}")
        logging.error(response.text)
        return None

def chunk_text(text, chunk_size, overlap_size):
    """Splits the text into chunks with optional overlap."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        if end >= text_length:
            break

        # Move the start back by the overlap size
        start = end - overlap_size

    return chunks

def save_topics_to_files(topics, output_directory, original_filename):
    logging.info(f"Saving extracted topics to files in directory: {output_directory}")
    
    # Join all the content together to check the total length
    total_content = ""
    first_topic = None
    for topic, content in topics.items():
        if not first_topic:
            first_topic = topic.replace(' ', '_').replace(':', '').replace('/', '_')
        total_content += f"{topic}\n\n{content}\n"

    if len(total_content) < 1800:
        # If total content is less than 1800 characters, save it all in one file
        base_filename = f"Topic_{original_filename}_{first_topic}.txt"
        
        # Ensure unique filename
        filename = get_unique_filename(output_directory, base_filename)
        
        # Check if the filename exceeds the maximum length
        if len(filename) > MAX_FILENAME_LENGTH:
            logging.warning(f"Filename '{filename}' exceeds the maximum length of {MAX_FILENAME_LENGTH} characters. Skipping file creation.")
            return
        
        filepath = os.path.join(output_directory, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(total_content)
        logging.info(f"Saved {filepath}")
    else:
        # If total content is 1800 characters or more, save each topic in a separate file
        for topic, content in topics.items():
            base_filename = f"{topic.replace(' ', '_').replace(':', '').replace('/', '_')}.txt"
            
            # Ensure unique filename
            filename = get_unique_filename(output_directory, base_filename)
            
            # Check if the filename exceeds the maximum length
            if len(filename) > MAX_FILENAME_LENGTH:
                logging.warning(f"Filename '{filename}' exceeds the maximum length of {MAX_FILENAME_LENGTH} characters. Skipping file creation.")
                continue
            
            filepath = os.path.join(output_directory, filename)
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(f"{topic}\n\n{content}")
            logging.info(f"Saved {filepath}")

def process_text_files(directory, output_directory):
    logging.info(f"Ensuring output directory exists: {output_directory}")
    os.makedirs(output_directory, exist_ok=True)

    done_directory = os.path.join(directory, "done")
    os.makedirs(done_directory, exist_ok=True)

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            logging.info(f"Processing file: {filename}")
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
                logging.info(f"Chunking text from {filename}.")
                
                chunks = chunk_text(text, CHUNK_SIZE, OVERLAP_SIZE)

                all_topics = {}
                for i, chunk in enumerate(chunks):
                    logging.info(f"Processing chunk {i+1}/{len(chunks)} for file: {filename}")
                    # Extract topics and related text using the API
                    result = extract_information_from_text(chunk)
                    
                    if result:
                        content = result.get("choices", [])[0].get("message", {}).get("content", "")
                        if content:
                            logging.info(f"Parsing extracted content from chunk {i+1}/{len(chunks)}.")
                            topics = parse_extracted_content(content)
                            all_topics.update(topics)  # Combine all topics from chunks
                        else:
                            logging.warning(f"No topics found in chunk {i+1}/{len(chunks)}.")
                    else:
                        logging.error(f"Failed to extract information from chunk {i+1}/{len(chunks)}.")
                
                if all_topics:
                    save_topics_to_files(all_topics, output_directory, filename.replace('.txt', ''))

            shutil.move(filepath, os.path.join(done_directory, filename))
            logging.info(f"Moved processed file '{filename}' to 'done' folder.")

def parse_extracted_content(content):
    logging.info("Parsing extracted content into topics.")
    topics = {}
    current_topic = None
    lines = content.splitlines()

    for line in lines:
        line = line.strip()
        if line.startswith("Topic_"):
            current_topic = line
            topics[current_topic] = ""
        elif current_topic:
            topics[current_topic] += line + "\n"

    return topics

def log_token_usage():
    logging.info(f"Total tokens sent: {total_tokens_sent}")
    logging.info(f"Total tokens received: {total_tokens_received}")
    logging.info(f"Total tokens used: {total_tokens_sent + total_tokens_received}")

directory = "input_data"  
output_directory = "extracted_topics"   

logging.info(f"Starting processing of text files in directory: {directory}")
try:
    process_text_files(directory, output_directory)
except Exception as e:
    logging.error(f"Processing interrupted due to error: {e}")
finally:
    log_token_usage()
    logging.info("Processing complete.")
