import requests
import logging
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FetchPageError(Exception):
    pass


def fetch_content_preview(url: str) -> str:
    """
    Fetches the preview content up to 1000 characters
    of a given URL by extracting text from the <p> tags.

    Args:
        url (str): The URL of the webpage to fetch content from.

    Returns:
        str: A preview of the webpage content,
        truncated to 1000 characters.

    Raises:
        FetchPageError: If an error occurs
        while fetching the page.
    """
    try:
        response = requests.get(url)
        # Raise HTTPError for bad responses (4xx and 5xx)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching the page: {e}")
        raise FetchPageError("Error fetching the page.") from e

    soup = BeautifulSoup(response.text, 'html.parser')

    content = ''
    for p in soup.find_all('p'):
        if len(p.text) + len(content) < 1000:
            content += p.text.strip() + ' '
        else:
            content += p.text[:(1000 - len(content))]
            break

    return content
