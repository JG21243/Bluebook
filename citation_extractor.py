import fitz  # PyMuPDF
import json  # For pretty printing JSON output
from eyecite import get_citations, resolve_citations
from eyecite.clean import clean_text

def resource_to_dict(resource):
    """
    Converts a Resource object into a dictionary by dynamically handling
    different types of citations. It checks for the citation's type and 
    formats the output accordingly.

    Args:
        resource (Resource): The Resource object to convert into a dictionary.

    Returns:
        dict: A dictionary representation of the Resource object, with the citation
              information formatted based on its type.

    Example:
        >>> resource = Resource()
        >>> result = resource_to_dict(resource)
        >>> print(result)
        {'type': 'Unknown', 'details': 'No citation available'}
    """
    if hasattr(resource, 'citation'):
        citation = resource.citation
        citation_type = type(citation).__name__
        if citation_type == 'FullCaseCitation':
            return {
                "type": "FullCaseCitation",
                "volume": citation.volume,
                "reporter": citation.reporter,
                "page": citation.page,
                "year": citation.year,
                "court": getattr(citation, 'court', None)
            }
        elif citation_type == 'StatuteCitation':
            return {
                "type": "StatuteCitation",
                "title": citation.title,
                "section": citation.section
            }
        # Extend with more citation types as needed
        else:
            return {"type": "Unknown", "details": str(citation)}
    return None

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    """
    doc = fitz.open(pdf_path)
    text = "".join(page.get_text() for page in doc)
    doc.close()
    return text

def extract_and_resolve_citations(text):
    """
    Extracts and resolves citations from text using eyecite.
    """
    # If no specific steps are needed, pass an empty list or None based on eyecite's version
    cleaned_text = clean_text(text, steps=[])
    citations = get_citations(cleaned_text)
    return resolve_citations(citations)


def extract_text_and_resolve_citations(pdf_path):
    """
    Extracts text from a PDF and resolves any legal citations found.
    """
    text = extract_text_from_pdf(pdf_path)
    resolved_citations = extract_and_resolve_citations(text)
    return [resource_to_dict(citation) for citation in resolved_citations if resource_to_dict(citation)]

# Example usage (commented out - provide your own PDF path)
# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) > 1:
#         pdf_path = sys.argv[1]
#     else:
#         # Default example path - replace with your PDF path
#         pdf_path = 'path/to/your/legal_document.pdf'
#
#     resolved_citations = extract_text_and_resolve_citations(pdf_path)
#
#     # Convert the output to pretty JSON format and print
#     pretty_json_output = json.dumps(resolved_citations, indent=4)
#     print(pretty_json_output)

