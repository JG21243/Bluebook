import os
import openai
import pandas as pd
import json

# Set the OpenAI API key from an environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def extract_citations_with_features(text):
    """
    Extract legal citations and their features from the provided text.
    
    Parameters:
    text (str): The text containing legal citations.
    
    Returns:
    DataFrame: A DataFrame with the features of each citation.
    """
    columns = ["Citation", "Type", "Signal", "Year", "Court", "Page", "Volume", "Reporter", "Case Name"]
    citations_data = []

    prompt = f"Extract legal citations and their features from the following text:\n\n{text}"
    
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=200,
            temperature=0.5
        )
        # Safely parse the JSON response
        citations = json.loads(response['choices'][0]['text'])
        
        for citation in citations:
            citations_data.append(citation)
            
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    
    return pd.DataFrame(citations_data, columns=columns)

# Example usage
text = """
The Supreme Court of the United States has held that the First Amendment protects freedom of speech. 
See, e.g., Marbury v. Madison, 5 U.S. 137, 177–79 (1803); 42 U.S.C. §§ 2000e et seq.
"""
df = extract_citations_with_features(text)
print(df)
