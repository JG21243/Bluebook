import openai
import pandas as pd
import eyecite
from eyecite import get_citations, resolve_citations

# Initialize the OpenAI client with your API key
openai.api_key = 'YOUR_API_KEY'

def extract_citations_with_features(text):
    # Clean the text and extract citations using eyecite
    citations = get_citations(text)
    
    # Resolve the citations to get more information about them
    resolved_citations = resolve_citations(citations)
    
    # Initialize an empty list to store the features of each citation
    citations_data = []
    
    # Iterate over the resolved citations and extract their features
    for citation in resolved_citations:
        citation_data = {
            "Citation": str(citation),
            "Type": type(citation).__name__,
            "Signal": citation.metadata.signal if citation.metadata else None,
            "Year": citation.metadata.year if citation.metadata else None,
            "Court": citation.metadata.court if citation.metadata else None,
            "Page": citation.metadata.pin_cite if citation.metadata else None,
            "Volume": citation.volume.volume if citation.volume else None,
            "Reporter": citation.reporter.reporter if citation.reporter else None,
            "Case Name": citation.metadata.case_name if citation.metadata else None
        }
        citations_data.append(citation_data)
    
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(citations_data)
    return df

# Example text containing legal citations
text = """
The Supreme Court of the United States has held that the First Amendment protects freedom of speech. 
See, e.g., Marbury v. Madison, 5 U.S. 137, 177–79 (1803); 42 U.S.C. §§ 2000e et seq.
"""

# Extract citations and their features from the example text
df = extract_citations_with_features(text)
print(df)
