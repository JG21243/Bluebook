"""
Alternative citation processor with GPT-4 focus.

This module provides citation checking with an emphasis on GPT-4 validation.
Uses the shared core module for all processing logic.

This is a wrapper around the core module for backward compatibility.
For new code, consider importing from core.py directly.
"""

from core import check_citations
import logging

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Example usage
if __name__ == "__main__":
    example_text = (
        "As held in Roe v. Wade, 410 U.S. 113 (1973), privacy rights are fundamental. "
        "See also Planned Parenthood v. Casey, 505 U.S. 833 (1993)."
    )

    print("Processing citations with GPT-4 validation...")
    citation_results = check_citations(example_text)

    # Display the results
    print(f"\nFound {len(citation_results)} citations:\n")
    for citation_text, gpt4_feedback, court_listener_data in citation_results:
        print(f"Citation: {citation_text}")
        print(f"GPT-4 Feedback: {gpt4_feedback}")
        print(f"Court Listener Data: {court_listener_data}")
        print("-" * 80)
