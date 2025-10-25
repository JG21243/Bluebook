"""
Core functionality for the Bluebook Legal Citation Processor.

This module provides shared utilities for citation extraction, validation,
and enrichment with proper error handling, type hints, and thread safety.
"""

from typing import List, Dict, Optional, Tuple, Any
from eyecite import get_citations, resolve_citations
from eyecite.clean import clean_text
from openai import OpenAI
import requests
import logging
import os
import time
from queue import Queue
import threading

# Configure module logger
logger = logging.getLogger(__name__)


class Config:
    """Application configuration from environment variables."""

    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.court_listener_token = os.getenv('COURT_LISTENER_TOKEN', '')
        self.congress_api_key = os.getenv('CONGRESS_API_KEY', '')
        self.batch_size = int(os.getenv('BATCH_SIZE', '5'))
        self.max_workers = int(os.getenv('MAX_WORKERS', '10'))
        self.gpt4_model = os.getenv('GPT4_MODEL', 'gpt-4-1106-preview')
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))

    def validate(self) -> None:
        """Validate that required configuration is present."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        if not self.court_listener_token:
            raise ValueError("COURT_LISTENER_TOKEN environment variable is required")


# Global configuration instance
config = Config()


def get_openai_client() -> OpenAI:
    """
    Get configured OpenAI client.

    Returns:
        Configured OpenAI client instance.

    Raises:
        ValueError: If OPENAI_API_KEY is not set.
    """
    if not config.openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    return OpenAI(api_key=config.openai_api_key)


def gpt4_parse_citations(
    citations: List[str],
    client: Optional[OpenAI] = None
) -> Optional[str]:
    """
    Parse legal citations for factual accuracy and Legal Bluebook compliance using GPT-4.

    Args:
        citations: A list of legal citation strings to be parsed.
        client: Optional OpenAI client instance. If None, a new client is created.

    Returns:
        The parsed content from GPT-4, or None if the API request fails.

    Raises:
        TypeError: If citations is not a list.
        ValueError: If citations list is empty.
    """
    if not isinstance(citations, list):
        raise TypeError(f"citations must be a list, got {type(citations).__name__}")

    if not citations:
        raise ValueError("citations list cannot be empty")

    if client is None:
        client = get_openai_client()

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful, fact-checking, legal assistant. Your task is to check "
                "the provided legal citations for factual accuracy (e.g., does the citation "
                "contain the correct year of case, the correct court, parties, reporter, "
                "volume, pages, etc.) and for 21st edition Legal Bluebook compliance. "
                "If you do not know the correct information, tell the user you are not sure."
            )
        }
    ] + [{"role": "user", "content": citation} for citation in citations]

    try:
        completion = client.chat.completions.create(
            model=config.gpt4_model,
            messages=messages,
            timeout=config.request_timeout
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"GPT-4 API request failed: {e}", exc_info=True)
        return None


def fetch_case_data_from_court_listener(
    citation: str,
    max_retries: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Fetch case data from the Court Listener API with retry logic.

    Args:
        citation: The legal citation to fetch case data for.
        max_retries: Maximum number of retry attempts. Defaults to config value.

    Returns:
        The case data retrieved from the API, or None if all retries fail.

    Raises:
        TypeError: If citation is not a string.
        ValueError: If citation is empty.
    """
    if not isinstance(citation, str):
        raise TypeError(f"citation must be a string, got {type(citation).__name__}")

    if not citation.strip():
        raise ValueError("citation cannot be empty")

    if max_retries is None:
        max_retries = config.max_retries

    url = f"https://www.courtlistener.com/api/rest/v3/search/?type=o&q={citation}"
    headers = {'Authorization': f"Token {config.court_listener_token}"}

    for attempt in range(max_retries):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=config.request_timeout
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:  # Rate limit
                wait_time = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited. Waiting {wait_time} seconds.")
                time.sleep(wait_time)
            elif response.status_code >= 500:  # Server error
                logger.error(
                    f"Server error {response.status_code}. "
                    f"Retry {attempt + 1}/{max_retries}"
                )
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(
                    f"Court Listener API request failed with status {response.status_code}: "
                    f"{response.text}"
                )
                return None

        except requests.exceptions.RequestException as e:
            logger.error(
                f"Request exception on attempt {attempt + 1}/{max_retries}: {e}",
                exc_info=True
            )
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff

    logger.error(f"Failed to fetch data after {max_retries} attempts for citation: {citation}")
    return None


def process_citations_batch(
    citations_batch: List[Any],
    results_queue: Queue,
    client: Optional[OpenAI] = None
) -> None:
    """
    Process a batch of citations with thread-safe result storage.

    Args:
        citations_batch: A list of citations to process.
        results_queue: Thread-safe queue for storing results.
        client: Optional OpenAI client instance.
    """
    for citation in citations_batch:
        try:
            citation_str = str(citation)
            court_listener_data = fetch_case_data_from_court_listener(citation_str)
            gpt4_feedback = gpt4_parse_citations([citation_str], client=client)
            results_queue.put((citation_str, gpt4_feedback, court_listener_data))
        except Exception as e:
            logger.error(f"Error processing citation {citation}: {e}", exc_info=True)
            results_queue.put((str(citation), None, None))


def check_citations(
    text: str,
    batch_size: Optional[int] = None
) -> List[Tuple[str, Optional[str], Optional[Dict[str, Any]]]]:
    """
    Check citations in the given text using multi-threaded processing.

    Args:
        text: The text to check for citations.
        batch_size: Number of citations to process per batch. Defaults to config value.

    Returns:
        A list of tuples containing (citation_text, gpt4_feedback, court_listener_data).

    Raises:
        TypeError: If text is not a string.
        ValueError: If text is empty.
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be a string, got {type(text).__name__}")

    if not text.strip():
        logger.warning("Empty text provided")
        return []

    if batch_size is None:
        batch_size = config.batch_size

    # Clean and extract citations
    cleaning_steps = []
    cleaned_text = clean_text(text, steps=cleaning_steps)
    citations = get_citations(cleaned_text)
    normalized_citations = resolve_citations(citations)

    if not isinstance(normalized_citations, list):
        normalized_citations = list(normalized_citations)

    if not normalized_citations:
        logger.info("No citations found in text")
        return []

    logger.info(f"Found {len(normalized_citations)} citations to process")

    # Thread-safe queue for results
    results_queue: Queue = Queue()
    threads = []

    # Create OpenAI client once and share across threads
    client = get_openai_client()

    # Process citations in batches using threads
    for i in range(0, len(normalized_citations), batch_size):
        batch = normalized_citations[i:i + batch_size]
        thread = threading.Thread(
            target=process_citations_batch,
            args=(batch, results_queue, client)
        )
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Convert queue to list
    results = []
    while not results_queue.empty():
        results.append(results_queue.get())

    logger.info(f"Processed {len(results)} citations")
    return results


def extract_citations(text: str) -> List[Any]:
    """
    Extract citations from text using eyecite.

    Args:
        text: The text to extract citations from.

    Returns:
        List of extracted citations.

    Raises:
        TypeError: If text is not a string.
    """
    if not isinstance(text, str):
        raise TypeError(f"text must be a string, got {type(text).__name__}")

    # Define cleaning steps
    steps = [
        'html',                 # Removes HTML markup
        'inline_whitespace',    # Collapses multiple spaces or tabs into one space
        'all_whitespace',       # Collapses multiple whitespace characters into one space
        'underscores'           # Removes strings of two or more underscores
    ]

    # Clean the text and extract citations
    cleaned_text = clean_text(text, steps)
    citations = get_citations(cleaned_text)

    return list(citations)
