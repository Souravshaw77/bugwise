import os
import json
import re
from typing import Dict

from google import genai

MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = """
You are a senior software engineer helping junior developers debug errors.

STRICT RULES:
- Respond with ONLY valid JSON
- NO markdown
- NO ``` fences
- NO extra commentary

JSON schema (must match exactly):
{
  "explanation": "string",
  "root_cause": "string",
  "fix_steps": ["string"],
  "example_code": "string"
}
"""


def extract_json(text: str) -> Dict:
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return json.loads(match.group())

    raise ValueError("Could not parse valid JSON")


class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        self.client = genai.Client(api_key=self.api_key)

    def analyze_bug(self, bug_text, language=None, context=None) -> Dict:

        prompt = f"""
Bug/Error:
{bug_text}

Language/Tech:
{language or "Unknown"}

Context:
{context or "Not provided"}

Analyze the bug and return structured JSON.
"""

        try:
            response = self.client.models.generate_content(
                model=MODEL,
                contents=f"{SYSTEM_PROMPT}\n\n{prompt}"
            )

            raw_text = response.text
            data = extract_json(raw_text)

            return {
                "explanation": data.get("explanation", ""),
                "root_cause": data.get("root_cause", ""),
                "fix_steps": data.get("fix_steps", []),
                "example_code": data.get("example_code", ""),
            }

        except Exception as e:
            print("Gemini failed, using fallback:", e)
            return self._fallback_analysis(bug_text)

    def _fallback_analysis(self, bug_text) -> Dict:
        text = (bug_text or "").lower()

        explanation = (
            "The AI service could not be reached. "
            "A basic rule-based analysis is provided."
        )

        root_cause = "A common programming error occurred."

        fix_steps = [
            "Check boundary conditions",
            "Validate inputs",
            "Add defensive checks",
        ]

        example_code = ""

        if "index" in text:
            root_cause = "Index access outside valid bounds."

            fix_steps = [
                "Check list length before access",
                "Fix loop boundaries",
                "Use safe iteration",
            ]

            example_code = """for item in my_list:
    print(item)"""

        elif "null" in text or "none" in text:
            root_cause = "A null/None value is being accessed."

            fix_steps = [
                "Check if the object is None before using it.",
                "Initialize the variable properly.",
                "Add defensive null checks."
            ]

            example_code = """if obj is not None:
    obj.method()"""

        elif "syntax" in text:
            root_cause = "There is a syntax error in the code."

            fix_steps = [
                "Check brackets and parentheses.",
                "Check indentation.",
                "Review commas, colons, and quotes."
            ]

        return {
            "explanation": explanation,
            "root_cause": root_cause,
            "fix_steps": fix_steps,
            "example_code": example_code,
        }