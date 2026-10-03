import gradio as gr

from content_review_crew.main import SAMPLE_TEXT, review_text


def review(text: str) -> str:
    if not text.strip():
        return "Lütfen incelenecek bir metin girin."
    try:
        return review_text(text).raw
    except Exception as error:
        return f"İnceleme tamamlanamadı: {error}"


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Content Review Crew", fill_width=True) as ui:
        gr.Markdown("# Content Review Crew")
        with gr.Row():
            with gr.Column(scale=2):
                text = gr.Textbox(label="Metin", value=SAMPLE_TEXT, lines=12)
                button = gr.Button("Review", variant="primary")
            with gr.Column(scale=3):
                result = gr.Textbox(label="Değerlendirme", lines=30, max_lines=200)
        button.click(review, inputs=text, outputs=result)
    return ui


def run() -> None:
    build_ui().launch()


if __name__ == "__main__":
    run()
