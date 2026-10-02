from crewai import CrewOutput

from content_review_crew.crew import ContentReviewCrew

SAMPLE_TEXT = (
    "Yapay zeka birkaç yıl içinde bütün yazılımcıların yerini alacak. "
    "Bu yüzden programlama öğrenmek artık gereksiz."
)


def run() -> None:
    result = ContentReviewCrew().crew().kickoff(inputs={"text": SAMPLE_TEXT})
    assert isinstance(result, CrewOutput)

    claim_review = result.tasks_output[1].pydantic
    print("\nStructured claim review:")
    print(claim_review.model_dump_json(indent=2) if claim_review else "not available")
    print("\nFinal review:")
    print(result.raw)


if __name__ == "__main__":
    run()
