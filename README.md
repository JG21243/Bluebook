# Bluebook Legal Citation Processor

A comprehensive Python toolkit for extracting, validating, and enriching legal citations with AI-powered analysis and external data integration.

## Overview

The Bluebook Legal Citation Processor is a powerful tool designed for legal professionals, researchers, and developers who need to:

- **Extract legal citations** from text documents and PDFs using the industry-standard `eyecite` library
- **Validate citation accuracy** using OpenAI's GPT-4 for factual verification and 21st edition Legal Bluebook compliance
- **Enrich citations** with comprehensive case data from the Court Listener API
- **Process documents efficiently** using multi-threaded batch processing for high-performance workflows

## Features

- 🔍 **Smart Citation Extraction**: Advanced text processing with `eyecite` for accurate citation detection
- 🤖 **AI-Powered Validation**: GPT-4 integration for factual accuracy and Legal Bluebook compliance checking
- 📚 **Data Enrichment**: Automatic case data retrieval from Court Listener API
- ⚡ **High Performance**: Multi-threaded batch processing for efficient large-document handling
- 📄 **PDF Support**: Extract citations directly from PDF documents using PyMuPDF
- 🔧 **Modular Design**: Multiple specialized scripts for different use cases
- 📊 **Comprehensive Logging**: Detailed logging for debugging and process tracking

## Project Structure

```
├── arm.py                          # Main citation processor with threading and API integration
├── eye.py                          # Alternative citation processor with GPT-4 analysis
├── citation_extractor.py          # PDF and general citation extraction utilities  
├── Citation_Extractor_Eyecite.py  # Basic eyecite citation extraction example
├── legal_citation_extractor.py    # Additional citation extraction utilities
├── pdf_citation_extractor.py      # PDF-specific citation extraction tools
├── api_gov                         # Congressional API integration example
├── README.md                       # This documentation
├── CODEBASE_GUIDE.md              # Detailed codebase overview
└── LICENSE.txt                     # MIT License
```

## Requirements

- **Python 3.7+** (tested with Python 3.12)
- **Required Libraries**:
  - `eyecite` - Legal citation extraction and parsing
  - `openai` - OpenAI API integration for GPT-4 analysis
  - `requests` - HTTP requests for API communication
  - `PyMuPDF` (fitz) - PDF document processing
  - `PyPDF2` - Alternative PDF processing library
  - `pandas` - Data manipulation and analysis

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/JG21243/Bluebook.git
   cd Bluebook
   ```

2. **Install required dependencies**:
   ```bash
   pip install eyecite openai requests PyMuPDF PyPDF2 pandas
   ```

## API Configuration

### ⚠️ Security Warning
**Do not commit API keys to version control.** The current codebase contains hardcoded API keys that should be removed and replaced with environment variables.

### Required API Keys

1. **OpenAI API Key** (for GPT-4 analysis):
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Create an API key and set it as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key-here"
   ```

2. **Court Listener API Token** (for case data enrichment):
   - Register at [Court Listener](https://www.courtlistener.com/api/)
   - Set your token as an environment variable:
   ```bash
   export COURT_LISTENER_TOKEN="your-court-listener-token-here"
   ```

3. **Congressional API Key** (optional, for `api_gov` script):
   - Register at [Congress.gov API](https://api.congress.gov/)
   - Set your key as an environment variable:
   ```bash
   export CONGRESS_API_KEY="your-congress-api-key-here"
   ```

### Updating the Code for Environment Variables

Before using the scripts, update the hardcoded API keys to use environment variables:

```python
import os
from openai import OpenAI

# Replace hardcoded keys with environment variables
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
court_listener_token = os.getenv('COURT_LISTENER_TOKEN')
```

## Usage

### Basic Citation Extraction

```python
from Citation_Extractor_Eyecite import extract_citations

text = """As held in Roe v. Wade, 410 U.S. 113 (1973), privacy rights are fundamental. 
See also Planned Parenthood v. Casey, 505 U.S. 833 (1993)."""

citations = extract_citations(text)
for citation in citations:
    print(f"Found citation: {citation}")
```

### Advanced Processing with AI Analysis

```python
from arm import check_citations

example_text = """The Supreme Court in Brown v. Board of Education, 347 U.S. 483 (1954), 
held that racial segregation in public schools violates the Equal Protection Clause."""

# Process citations with GPT-4 analysis and Court Listener data
citation_results = check_citations(example_text)

for citation_text, gpt4_feedback, court_listener_data in citation_results:
    print(f"Citation: {citation_text}")
    print(f"GPT-4 Analysis: {gpt4_feedback}")
    print(f"Case Data: {court_listener_data}")
    print("-" * 50)
```

### PDF Citation Extraction

```python
from citation_extractor import extract_text_from_pdf
from eyecite import get_citations

# Extract text from PDF and find citations
pdf_text = extract_text_from_pdf("legal_document.pdf")
citations = get_citations(pdf_text)

for citation in citations:
    print(f"PDF Citation: {citation}")
```

## Script Descriptions

| Script | Purpose | Key Features |
|--------|---------|--------------|
| `arm.py` | Main processing engine | Multi-threading, GPT-4 analysis, Court Listener integration |
| `eye.py` | Alternative processor | Focused GPT-4 citation validation |
| `citation_extractor.py` | PDF utilities | PDF text extraction, citation conversion utilities |
| `Citation_Extractor_Eyecite.py` | Basic example | Simple eyecite usage demonstration |
| `legal_citation_extractor.py` | Utility functions | Additional citation processing tools |
| `pdf_citation_extractor.py` | PDF specialist | Dedicated PDF citation extraction |
| `api_gov` | Government data | Congressional API integration example |

## Development

### Running the Scripts

1. **Basic citation extraction**:
   ```bash
   python Citation_Extractor_Eyecite.py
   ```

2. **Advanced processing**:
   ```bash
   python arm.py
   ```

3. **PDF processing**:
   ```bash
   python pdf_citation_extractor.py
   ```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with proper testing
4. Remove any hardcoded API keys
5. Submit a pull request

### Security Best Practices

- Never commit API keys or sensitive credentials
- Use environment variables for all API configurations
- Regularly rotate API keys
- Review code for security vulnerabilities before committing

## Troubleshooting

**Common Issues:**

1. **Import Errors**: Ensure all required libraries are installed
2. **API Errors**: Verify API keys are set correctly as environment variables
3. **PDF Processing Issues**: Install PyMuPDF with: `pip install PyMuPDF`
4. **Rate Limiting**: Implement delays between API calls if needed

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Acknowledgments

- [eyecite](https://github.com/freelawproject/eyecite) - Legal citation extraction
- [Court Listener](https://www.courtlistener.com/) - Legal case data API
- [OpenAI](https://openai.com/) - GPT-4 AI analysis
- Contributors and the legal technology community