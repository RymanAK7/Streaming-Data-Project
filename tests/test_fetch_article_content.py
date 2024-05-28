import pytest
from src.fetch_article_content import fetch_content_preview, FetchPageError
import requests_mock

TEST_URL = "http://testexample.com/page"


def test_fetch_content_preview_success():
    """
    Test that the fetch_content_preview function
    returns the content of a page successfully.
    """

    response_text = """
    <html>
      <body>
        <p> Guardian article content  </p>
      </body>
    </html>
    """

    with requests_mock.Mocker() as mocker:
        mocker.get(TEST_URL, text=response_text)
        content_preview = fetch_content_preview(TEST_URL)
        assert content_preview == "Guardian article content "


def test_fetch_content_preview_raises_FetchPageError():
    """
    Test that the fetch_content_preview
    function raises FetchPageError
    when unable to fetch page content.
    """
    with pytest.raises(FetchPageError):
        fetch_content_preview(TEST_URL)


def test_fetch_content_preview_handles_empty_response():
    '''
    Test how the function handles an empty response from the URL.
    '''
    with requests_mock.Mocker() as mocker:
        mocker.get(TEST_URL, text="")
        content_preview = fetch_content_preview(TEST_URL)
        assert content_preview == ""


def test_fetch_content_preview_handles_non_html_content():
    '''
    Test how the function handles a URL that
    returns content not in HTML format.
    '''
    with requests_mock.Mocker() as mocker:
        mocker.get(TEST_URL, text="Not HTML content")
        content_preview = fetch_content_preview(TEST_URL)
        assert content_preview == ""


def test_fetch_content_preview_handles_no_paragraphs():
    '''
    Test how the function handles HTML content
    that doesn't contain any <p> tags.
    '''

    response_text = "<html><body>No paragraphs</body></html>"
    with requests_mock.Mocker() as mocker:
        mocker.get(TEST_URL, text=response_text)
        content_preview = fetch_content_preview(TEST_URL)
        assert content_preview == ""


def test_fetch_content_preview_handles_long_paragraphs():
    '''
    Test how the function handles URLs
    where individual paragraphs are
    longer than 1000 characters.
    '''
    response_text = "<html><body><p>Test Article</p></body></html>" * 2000
    with requests_mock.Mocker() as mocker:
        mocker.get(TEST_URL, text=response_text)
        content_preview = fetch_content_preview(TEST_URL)
        assert len(content_preview) == 1000
