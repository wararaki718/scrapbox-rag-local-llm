import pytest
from app.services.scrapbox_service import ScrapboxService
from app.models.scrapbox import ScrapboxPage

def test_clean_scrapbox_text():
    text = "This is a [link] and [image.jpg]"
    cleaned = ScrapboxService.clean_scrapbox_text(text)
    assert cleaned == "This is a link and image.jpg"

def test_chunk_page():
    page = ScrapboxPage(
        id="page123",
        title="Test Page",
        lines=[
            "First line of text",
            "",
            "Second line that is a bit longer and should be part of a chunk.",
            "Indented line",
            "Another line to ensure we exceed the chunk length if we set it low enough."
        ],
        updated=1612345678
    )
    
    # Mocking internal state or just testing the logic
    chunks = ScrapboxService.chunk_page(page, "test-project")
    
    assert len(chunks) > 0
    assert chunks[0].page_id == "page123"
    assert chunks[0].title == "Test Page"
    assert "https://scrapbox.io/test-project/Test_Page" == chunks[0].url
    assert "First line of text" in chunks[0].text
