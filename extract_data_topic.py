import os
import requests
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define your API configuration
OPENAI_BASE_URL = "https://genv3.uwc.world/v1"
DEFAULT_MODEL = "meta-llama/Meta-Llama-3.1-8B-Instruct"
OPENAI_API_KEY = "EMPTY" 

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
    logging.info("Preparing the request payload.")

    # prompt = """<|eot_id|><|start_header_id|>system<|end_header_id|>
    # # Objective:
    # 1. Extract topics and all the related text for each topic and create a structure from the Input text.
    # 2. Ensure that there is no loss of information while extracting topics and their related information.

    # # Output Format:
    #     Topic_1 : name of topic 1
    #     All information regarding topic 1

    #     Topic_2 : name of topic 2
    #     All information regarding topic 2
        
    # <|eot_id|><|start_header_id|>user<|end_header_id|>"""

    # prompt_2="""<|eot_id|><|start_header_id|>system<|end_header_id|>
    # You are an AI language model tasked with extracting topics and their related text from a given document. Do not summarize the data.
    
    # The output should be formatted as follows:
    
    # Topic_1: [Name of Topic 1]
    # [All information related to Topic 1]
    
    # Topic_2: [Name of Topic 2]
    # [All information related to Topic 2]
    
    # # Note
    # - Ensure that no information is lost in the extraction process. The text should be extracted as is from the document and just placed a Topic heading by the AI language Model.
    # <|eot_id|><|start_header_id|>user<|end_header_id|>"""

    prompt_3= """ <|eot_id|><|start_header_id|>system<|end_header_id|>
# Objective:
You are an AI language model tasked with extracting topics and their related text from a given document. 

Your task is to identify distinct topics based on the content of the document. For each identified topic, extract **all** relevant information exactly as it appears in the document, without summarizing or altering the text. Each piece of information should be placed under the appropriate topic header.

# Output Format:
The output should be structured in the following format:

Topic_1: [Name of Topic_1]
[All information related to this topic, including any subtopics or examples, exactly as they appear in the document.]

If there are multiple topics, the output should continue with:

Topic_2: [Name of Another Topic_2]
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
        headers={"Authorization": f"Bearer {OPENAI_API_KEY}"}
    )

    logging.info("Sending request to the API.")
    response.raise_for_status()
    print(response.json()["choices"][0]["message"]["content"])

    if response.status_code == 200:
        logging.info("API request successful.")
        logging.info(f"API Response: {response.json()}")  # Log the full response
        return response.json()
    else:
        logging.error(f"Error: {response.status_code}")
        logging.error(response.text)
        return None

# Function to save extracted information into topic-based text files
def save_topics_to_files(topics, output_directory):
    logging.info(f"Saving extracted topics to files in directory: {output_directory}")
    for topic, content in topics.items():
        # Clean the topic name to be a valid filename
        filename = f"{topic.replace(' ', '_').replace(':', '').replace('/', '_')}.txt"
        filepath = os.path.join(output_directory, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(f"{topic}\n\n{content}")
        logging.info(f"Saved {filepath}")

# Main function to process all text files in a directory
def process_text_files(directory, output_directory):
    logging.info(f"Ensuring output directory exists: {output_directory}")
    os.makedirs(output_directory, exist_ok=True)

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
                        save_topics_to_files(topics, output_directory)
                    else:
                        logging.warning(f"No topics found in {filename}.")
                else:
                    logging.error(f"Failed to extract information from {filename}.")

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

directory = "input_data"  
output_directory = "extracted_topics"   

logging.info(f"Starting processing of text files in directory: {directory}")
process_text_files(directory, output_directory)
logging.info("Processing complete.")

