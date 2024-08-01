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

def extract_information_from_text(text):

    global total_tokens_sent, total_tokens_received

    logging.info("Preparing the request payload.")

    prompt_3= """ <|eot_id|><|start_header_id|>system<|end_header_id|>
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

    <|eot_id|><|start_header_id|>user<|end_header_id|>
    """

    prompt_4 = """The following document contains legal information regarding medical cannabis in Australia. Remove all unneccessary information that may have been extracted in the scraping process. Keep the information as it is. There should be no information lost from the document. Start a new topic with "Topic_"."""  
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

# Function to save extracted information into topic-based text files
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
        filename = f"Topic_{original_filename}_{first_topic}.txt"
        
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
            filename = f"{topic.replace(' ', '_').replace(':', '').replace('/', '_')}.txt"
            
            if len(filename) > MAX_FILENAME_LENGTH:
                logging.warning(f"Filename '{filename}' exceeds the maximum length of {MAX_FILENAME_LENGTH} characters. Skipping file creation.")
                continue
            
            filepath = os.path.join(output_directory, filename)
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(f"{topic}\n\n{content}")
            logging.info(f"Saved {filepath}")

# Main function to process all text files in a directory
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
                logging.info(f"Extracting information from {filename} using the API.")

                # Extract topics and related text using the API
                result = extract_information_from_text(text)
                
                if result:
                    # Assuming the model returns a structured JSON with topics and content
                    content = result.get("choices", [])[0].get("message", {}).get("content", "")
                    if content:
                        logging.info(f"Parsing extracted content from {filename}.")
                        topics = parse_extracted_content(content)  # Parse the content into a dictionary
                        save_topics_to_files(topics, output_directory, filename.replace('.txt', ''))
                    else:
                        logging.warning(f"No topics found in {filename}.")
                else:
                    logging.error(f"Failed to extract information from {filename}.")

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
