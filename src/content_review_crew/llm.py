import os

from crewai import LLM

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODEL = "openai/gpt-oss-20b"


def groq_llm() -> LLM:
    # provider="openai" keeps the "openai/" prefix in the model name.
    # Without it CrewAI treats "openai/" as the provider and sends "gpt-oss-20b".
    return LLM(
        model=GROQ_MODEL,
        provider="openai",
        base_url=GROQ_BASE_URL,
        api_key=os.environ["GROQ_API_KEY"],
        temperature=0.2,
    )
