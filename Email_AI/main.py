import os
import json
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_groq import ChatGroq

# Load env
load_dotenv()

# LLM setup (Groq)
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0,
    max_tokens=800
)

# Prompt Template (Evaluator)
prompt = PromptTemplate(
    input_variables=["email"],
    template="""
You are a STRICT corporate email compliance auditor.

Your job is to IDENTIFY ALL possible risks in the email.

You MUST detect:
- Legal commitments (e.g., guarantees, promises)
- Financial/pricing risks
- Confidential/internal information leaks
- Personal data exposure (phone, email, etc.)
- NDA violations
- Offensive or unprofessional tone

IMPORTANT RULES:
- DO NOT miss any risk
- Be strict and critical
- Return MULTIPLE risks if applicable
- Severity must reflect seriousness (1–10)

Return ONLY valid JSON:

{{
  "risks": [
    {{
      "type": "",
      "description": "",
      "why_risk": "",
      "suggestion": "",
      "severity": 1
    }}
  ]
}}

Email:
{email}
"""
)

# Parser
parser = JsonOutputParser()

# Chain
chain = prompt | llm | parser

# Function: Evaluate Email
def evaluate_email(email_text, save=False):
    try:
        result = chain.invoke({"email": email_text})

        print("\nRisk Analysis:\n")

        if not result["risks"]:
            print("No risks detected.")
            return result

        for i, risk in enumerate(result["risks"], 1):
            print(f"Risk {i}: {risk['type']}")
            print(f"Why: {risk['why_risk']}")
            print(f"Suggestion: {risk['suggestion']}")
            print(f"Severity: {risk['severity']}/10\n")

        # Optional save
        if save:
            with open("email_risk_report.json", "w") as f:
                json.dump(result, f, indent=2)
            print("💾 Report saved to email_risk_report.json")

        return result

    except Exception as e:
        print("Error:", str(e))


# CLI Input
if __name__ == "__main__":
    print("📧 Corporate Email Compliance Checker\n")

    print("Enter email (press Ctrl+D when done):\n")
    import sys
    email = sys.stdin.read()

    evaluate_email(email, save=True)