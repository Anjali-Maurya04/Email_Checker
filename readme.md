# AI Email Compliance Checker

An AI-powered tool that analyzes corporate emails and detects compliance risks such as legal exposure, sensitive data leaks, and unprofessional tone using LLMs.

---

##  Features
- Detects multiple types of risks:
  - Legal commitments (guarantees, promises)
  - Financial/pricing risks
  - Confidential information leaks
  - Personal data exposure
  - NDA violations
  - Offensive/unprofessional tone
- Assigns **severity score (1–10)**
- Provides **clear suggestions**
- Outputs structured **JSON report**
- Optional file saving

---

## Tech Stack

- Python
- LangChain
- Groq (LLaMA 3.1)
- dotenv

---

## Project Structure

```plaintext
.
├── main.py                  # Main script
├── email_risk_report.json  # Output (generated)
├── .env                     # Add this file with your api key
├── requirements.txt
```

## Setup Instructions

### Clone the Repository
git clone https://github.com/Anjali-Maurya04/Email_Checker.git
cd Email_AI

### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Add Environment Variables
```bash
GROQ_API_KEY=your_api_key_here
```
### Run the Application

```bash
python main.py
```

## Usage
- Run the script
- Paste your email content
- Press:
  Ctrl + D (Mac/Linux)

## Output File

If enabled, results are saved to:

```bash
email_risk_report.json
```
