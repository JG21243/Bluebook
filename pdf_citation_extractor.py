from PyPDF2 import PdfReader
from eyecite import get_citations, resolve_citations
from eyecite.clean import clean_text

def extract_citations(text):
    # Define the cleaning steps using actual functions from eyecite.clean
    steps = [
        'html',                 # Removes HTML markup
        'inline_whitespace',    # Collapses multiple spaces or tabs into one space
        'all_whitespace',       # Collapses multiple whitespace characters into one space
        'underscores'           # Removes strings of two or more underscores
    ]

    # Clean the text and extract citations
    cleaned_text = clean_text(text, steps)
    citations = get_citations(cleaned_text)

    return citations

def find_first_full_case_citation(citations):
    for citation in citations:
        if citation.__class__.__name__ == "FullCaseCitation":
            return citation

    return None

def print_citation_details(citation):
    #print(dir(citation))  # Lists all attributes and methods

    # To see the value of a specific attribute, for example, 'reporter'
    print(getattr(citation, 'corrected_citation', 'Attribute not found'))

    # Or simply using dot notation if you know the attribute exists
    #print(citation.corrected_citation())

    #print(citation.groups['reporter'])

# Path to your PDF document
def new_func():
    pdf_path = 'Your/PDF/PATH.pdf'
    return pdf_path

pdf_path = new_func()

# Read the PDF file and extract text
reader = PdfReader(pdf_path)
text = ""
for page in reader.pages:
    text += page.extract_text()

citations = extract_citations(text)
full_case_citation = find_first_full_case_citation(citations)
if full_case_citation is not None:
    print_citation_details(full_case_citation)
