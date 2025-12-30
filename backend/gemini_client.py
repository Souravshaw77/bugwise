import os
import json
import re
from typing import Dict, List

from openai import OpenAI  


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

    # 1. Try clean JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Extract first JSON object found
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not parse valid JSON from AI response")


class GeminiClient:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set")

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )

        # Stable, cheap, reliable
        self.model = "mistralai/mistral-7b-instruct"


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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
            )

            raw_text = response.choices[0].message.content
            data = extract_json(raw_text)

            return {
                "explanation": data.get("explanation", ""),
                "root_cause": data.get("root_cause", ""),
                "fix_steps": data.get("fix_steps", []),
                "example_code": data.get("example_code", ""),
            }

        except Exception as e:
            print("OpenRouter failed, using fallback:", e)
            return self._fallback_analysis(bug_text, language, context)


    def _fallback_analysis(self, bug_text, language=None, context=None) -> Dict:
        text = (bug_text or "").lower()

        explanation = (
            "The AI service could not be reached. "
            "A basic rule-based analysis is provided."
        )
        root_cause = "The error indicates a common programming mistake."
        fix_steps: List[str] = [
            "Read the error message carefully",
            "Check variable initialization",
            "Validate assumptions in the code",
        ]
        example_code = ""

        if "index" in text:
            root_cause = "The code is accessing an index outside the valid range."
            fix_steps = [
                "Ensure loop bounds are correct",
                "Check list length before accessing elements",
                "Prefer safe iteration patterns",
            ]
            example_code = (
                "for item in my_list:\n"
                "    print(item)"
            )

        elif "undefined" in text or "null" in text:
            root_cause = "The code is accessing a variable that is undefined or null."
            fix_steps = [
                "Initialize variables before use",
                "Add null/undefined checks",
                "Verify function return values",
            ]
            example_code = (
                "if data:\n"
                "    print(len(data))"
            )

        elif "typeerror" in text:
            root_cause = "An operation is being performed on incompatible data types."
            fix_steps = [
                "Check variable types",
                "Convert values explicitly",
                "Validate user input",
            ]

        return {
            "explanation": explanation,
            "root_cause": root_cause,
            "fix_steps": fix_steps,
            "example_code": example_code,
        }
