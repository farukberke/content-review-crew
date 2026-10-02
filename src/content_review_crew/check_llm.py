from content_review_crew.llm import groq_llm


def run() -> None:
    llm = groq_llm()
    print(f"LLM class: {type(llm).__name__}")
    print(f"Model sent to API: {llm.model}")
    print(f"Base URL: {llm.base_url}")
    print("Answer:", llm.call("Reply with exactly: connection ok"))


if __name__ == "__main__":
    run()
