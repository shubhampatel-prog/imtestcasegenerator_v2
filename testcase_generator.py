from openai import OpenAI
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from agent_prompt import build_prompt
import re

# LLM Gateway client
client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL
)


# =====================================================
# JSON CLEANER
# =====================================================
def _clean_json(text: str) -> str:

    if not text:
        return text

    text = re.sub(r"```json", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    text = (
        text.replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
    )

    return text.strip()


# =====================================================
# MAIN GENERATOR  — only change: return_prompt param
# =====================================================
def generate_testcases(requirement: dict, kb: list, return_prompt: bool = False, platform: str = "IndiaMart Android App"):

    prompt = build_prompt(requirement, kb, platform=platform)

    try:

        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior QA automation architect generating structured manual test cases."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
  #          max_tokens=3000
        )

        raw_output = response.choices[0].message.content

    except Exception as e:
        raise Exception(f"❌ LLM generation failed: {e}")

    clean_output = _clean_json(raw_output)

    if return_prompt:
        return clean_output, prompt

    return clean_output
