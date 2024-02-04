
# Import required modules
from eyecite import get_citations, resolve_citations
from eyecite.clean import clean_text
from openai import OpenAI
import requests
import threading
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Initialize the OpenAI client
client = OpenAI(api_key="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")

def gpt4_parse_citations(citations):
    """
    Parses the provided legal citations for factual accuracy and Legal Bluebook compliance.

    Args:
        citations (list): A list of legal citations to be parsed.

    Returns:
        str: The parsed content of the first completion choice from the GPT-4 API, or None if the API request fails.
    """
    messages = [
        {"role": "system", "content": "You are a helpful, fact-checking, legal assistant. Your task is to check the provided legal citations for factual accuracy (e.g.,  does the the citation contain the correct <year> of case, the correct <court>, <parties>, <reporter>, <volume>, <pages>, etc.) and for 21 edition Legal Bluebook compliance. If you do not know the correct information, tell the user you are not sure."}
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
    """
    Fetches case data from the Court Listener API for a given citation.

    Args:
        citation (str): The legal citation to fetch case data for.

    Returns:
        dict: The case data retrieved from the Court Listener API, or None if the API request fails.
    """
    url = f"https://www.courtlistener.com/api/rest/v3/search/?type=o&q={citation}"
    headers = {'Authorization': 'Token 974993b55ad4144adf83d3fe942abc7210e6e10a'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Function to handle each citation batch
def process_citations_batch(citations_batch, results):
    """
    Process a batch of citations.

    Args:
        citations_batch (list): A list of citations to process.
        results (list): A list to store the results of processing.

    Returns:
        None
    """
    for citation in citations_batch:
        court_listener_data = fetch_case_data_from_court_listener(str(citation))
        gpt4_feedback = gpt4_parse_citations([str(citation)])
        results.append((str(citation), gpt4_feedback, court_listener_data))

# Citation checker function that uses both Eyecite, GPT-4, and Court Listener API
def check_citations(text):
    """
    Check citations in the given text.

    Args:
        text (str): The text to check for citations.

    Returns:
        list: A list of results from processing the citations. Each result is a tuple containing the citation text, GPT-4 feedback, and Court Listener data.
    """
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
