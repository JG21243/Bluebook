# Codebase Guide

This document provides an overview of the project structure, technologies, and functionality.

## Repository Tree

```
.
├── Citation_Extractor_Eyecite.py
├── LICENSE.txt
├── README.md
├── api_gov
├── arm.py
├── citation_extractor.py
├── eye.py
├── legal_citation_extractor.py
└── pdf_citation_extractor.py

1 directory, 9 files
```

*(generated with `tree -L 1`)*

## Main Technologies / Packages

The `README.md` outlines the main libraries used:

- **eyecite** – citation extraction and resolution
- **requests** – HTTP requests for APIs
- **OpenAI gpt-4-1106-preview** – citation analysis

Other scripts also reference:
- **PyMuPDF** (`fitz`) and **PyPDF2** for PDF parsing
- **pandas** for data handling
- Python `threading` and `logging` modules

## Backend Overview

The backend consists of standalone Python scripts:

- **Citation extraction & PDF parsing**: `citation_extractor.py`, `Citation_Extractor_Eyecite.py`, `pdf_citation_extractor.py`
- **API integration & GPT-4 analysis**: `eye.py`, `arm.py`
- **Sample utilities**: `legal_citation_extractor.py`, `api_gov`

`eye.py` and `arm.py` use threads to process citation batches concurrently. They call the OpenAI API for analysis and the Court Listener API for case data.

**Note**: API keys are embedded in several files:
- `eye.py` (lines 29-30) contains an OpenAI token, and line 67 includes a Court Listener token.
- `arm.py` includes a Court Listener token at line 65.
- `api_gov` stores a congressional API key at line 3.

## Frontend Overview

No dedicated frontend is included. Scripts are run from the command line and print results directly. A separate UI would need to be developed if required.

## Features and Functionality

According to the README and scripts, this project supports:

- Cleaning and extracting legal citations with Eyecite
- Fetching case details from the Court Listener API
- GPT‑4 analysis of citation accuracy and Bluebook compliance
- Multi-threaded processing of citation batches
- Basic INFO level logging
- OpenAI client setup for API interaction

## Usage

1. Install dependencies (`eyecite`, `openai`, `requests`, etc.).
2. Provide OpenAI and Court Listener API keys as required.
3. Run a script such as `python arm.py` to process sample text and view the results.

## License

See `LICENSE.txt` for MIT license terms.
