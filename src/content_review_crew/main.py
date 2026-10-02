from crewai import CrewOutput

from content_review_crew.crew import ContentReviewCrew

SAMPLE_TEXT = (
    "Yapay zeka birkaç yıl içinde bütün yazılımcıların yerini alacak. "
    "Bu yüzden programlama öğrenmek artık gereksiz."
)


def review_text(text: str) -> CrewOutput:
    result = ContentReviewCrew().crew().kickoff(inputs={"text": text})
    assert isinstance(result, CrewOutput)
    return result


def read_text() -> str:
    print("İncelenecek metni yazın. Bitirmek için boş bir satırda Enter'a basın.")
    print("Hiçbir şey yazmazsanız örnek metin kullanılır.\n")
    lines: list[str] = []
    while line := input("> "):
        lines.append(line)
    return "\n".join(lines).strip() or SAMPLE_TEXT


def run() -> None:
    result = review_text(read_text())

    claim_review = result.tasks_output[1].pydantic
    print("\nStructured claim review:")
    print(claim_review.model_dump_json(indent=2) if claim_review else "not available")
    print("\nFinal review:")
    print(result.raw)


if __name__ == "__main__":
    run()
