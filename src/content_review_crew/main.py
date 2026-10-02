from crewai import CrewOutput

from content_review_crew.crew import ContentReviewCrew

SAMPLE_TEXT = (
    "Yapay zeka birkaç yıl içinde bütün yazılımcıların yerini alacak. "
    "Bu yüzden programlama öğrenmek artık gereksiz."
)


def run() -> None:
    result = ContentReviewCrew().crew().kickoff(inputs={"text": SAMPLE_TEXT})
    assert isinstance(result, CrewOutput)
    print(result.raw)


if __name__ == "__main__":
    run()
