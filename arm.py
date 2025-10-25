"""The Python script provided performs the following tasks:

1. **Module Imports**: It imports necessary modules such as `eyecite`, `openai`, `requests`, `threading`, and `logging` for processing legal citations, interacting with the OpenAI GPT-4 API, making HTTP requests, running concurrent operations, and logging information, respectively.

2. **Logging Setup**: It configures the logging to report at the INFO level, which will include informational messages about the program's execution (e.g., when handling citations).

3. **OpenAI Client Initialization**: It creates an instance of the OpenAI client to interact with the OpenAI API (presumably GPT-4).

4. **GPT-4 Interaction Function**: The `gpt4_parse_citations` function calls the OpenAI API to verify legal citations for accuracy and compliance with the Legal Bluebook standards. It prepares a list of messages, including the instructions for the system, and citation texts that need to be checked for accuracy.

5. **Fetching Case Data**: The `fetch_case_data_from_court_listener` function retrieves case data associated with a citation from the Court Listener API using HTTP requests. Authentication is performed using a provided API token.

6. **Citation Batch Processing**: The `process_citations_batch` function takes a batch of citations, fetches data for each from Court Listener, and uses GPT-4 to parse and provide feedback on each citation. It appends the results to a shared list.

7. **Citation Checker**: The `check_citations` function is the main function that performs the citation checking. It first cleans the input text and discovers citations using `eyecite`. Each found citation is normalized using `resolve_citations`. These normalized citations are processed in batches by spawning threads using the `threading` module. Each batch is processed through the `process_citations_batch` function. Multiple threads are used to process the batches concurrently for efficiency.

8. **Example Usage**: The script provides an example usage of the citation checking process. It defines an example legal text with citations, invokes the `check_citations` function with this text, and stores the results.

9. **Results Display**: After processing the citations, the script prints out the parsed citations, feedback from GPT-4, and case data from the Court Listener API for each citation.

In summary, this script is designed to clean and extract legal citations from a given text, validate their accuracy and compliance with standards via GPT-4, enrich them with external case data from the Court Listener API, and then display these details concurrently using multi-threading for efficiency."""

 # Import required modules
from eyecite import get_citations, resolve_citations
from eyecite.clean import clean_text
from openai import OpenAI
import requests
import threading
import logging
import os

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Function to interact with the GPT-4 API for enhanced parsing
def gpt4_parse_citations(citations):
    """
    Parses the provided legal citations for factual accuracy and Legal Bluebook compliance.

    Args:
        citations (list): A list of legal citations to be parsed.

    Returns:
        str: The parsed content of the first completion choice from the GPT-4 API, or None if the API request fails.
    """
    messages = [
        {"role": "system", "content": "You are a helpful, fact-checking, legal assistant. Your task is to check the provided legal citations for factual accuracy (e.g.,  does the the citation contain the correct year of case, the correct court, parties, reporter, volume, pages, etc.) and for 21 edition Legal Bluebook compliance. If you do not know the correct information, tell the user you are not sure."}
    ] + [{"role": "user", "content": citation} for citation in citations]

    try:
        completion = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages
        )
        return completion.choices[0].message.content
    except Exception as e:
        logging.error(f"GPT-4 API request failed: {e}")
        return None

# Function to fetch case data from the Court Listener API
def fetch_case_data_from_court_listener(citation):
    url = f"https://www.courtlistener.com/api/rest/v3/search/?type=o&q={citation}"
    headers = {'Authorization': f"Token {os.getenv('COURT_LISTENER_TOKEN')}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Court Listener API request failed with status {response.status_code}")
        return None

# Function to handle each citation batch
def process_citations_batch(citations_batch, results):
    for citation in citations_batch:
        court_listener_data = fetch_case_data_from_court_listener(str(citation))
        gpt4_feedback = gpt4_parse_citations([str(citation)])
        results.append((str(citation), gpt4_feedback, court_listener_data))

# Citation checker function that uses both Eyecite, GPT-4, and Court Listener API
def check_citations(text):
    cleaning_steps = []
    cleaned_text = clean_text(text, steps=cleaning_steps)
    citations = get_citations(cleaned_text)
    normalized_citations = resolve_citations(citations)

    if not isinstance(normalized_citations, list):
        normalized_citations = list(normalized_citations)

    results = []
    threads = []

    batch_size = 5
    for i in range(0, len(normalized_citations), batch_size):
        batch = normalized_citations[i:i + batch_size]
        thread = threading.Thread(target=process_citations_batch, args=(batch, results))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return results

# Example usage
example_text = "As held in Roe v. Wade, 410 U.S. 113 (1973), privacy rights are fundamental. See also Planned Parenthood v. Casey, 505 U.S. 833 (1993)."
citation_results = check_citations(example_text)

# Display the results
for citation_text, gpt4_feedback, court_listener_data in citation_results:
    print(f"Citation: {citation_text}\nGPT-4 Feedback: {gpt4_feedback}\nCourt Listener Data: {court_listener_data}\n")
