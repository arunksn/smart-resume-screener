from app.extractor import extract_text_from_input


def test_text_resume_extraction():
    text = extract_text_from_input(
        "resume.txt",
        b"Arun Kumar\nPython\nMachine Learning\nB.Tech CSE",
    )
    assert "Python" in text
    assert "Machine Learning" in text
