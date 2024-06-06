import requests
from retrieve_api_key import retrieve_api_key
from fetch_article_content import fetch_content_preview
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIRequestError(Exception):
    pass


def retrieve_articles(search_terms: str, from_date: str = None) -> list:
    """
    Retrieves articles from the Guardian API based on search terms and date.

    Args:
        search_terms (str): The search terms to query.
        from_date (str, optional): The start date for the search
        in YYYY-MM-DD format. If not provided, defaults to None,
        in which case recent articles will be retrieved

    Returns:
        list: A list of dictionaries containing
        the retrieved articles' information.
    """
    try:
        url = 'http://content.guardianapis.com/search'
        my_params = {
            'from-date': from_date,
            'order-by': 'relevance',
            'q': search_terms,
            'api-key': retrieve_api_key('guardian/api-key'),
        }
        logger.info(f'Making a request to the Guardian API.')
        base_url = "http://content.guardianapis.com/search"
        params = f"from-date={from_date}&" if from_date else ""
        logger.info(f'Request URL: {base_url}?{params}order-by=relevance&q={search_terms}')
        response = requests.get(url, params=my_params)
        data = response.json()
        if response.status_code == 200:
            logger.info('Request was successful')
            article_hits_info = []
            articles = data['response']['results']
            for article in articles:
                article_info = {
                    'webPublicationDate': article['webPublicationDate'],
                    'webTitle': article['webTitle'],
                    'webUrl': article['webUrl'],
                    'contentPreview': fetch_content_preview(
                        article['webUrl']
                    ) + '...'
                }
                article_hits_info.append(article_info)
        else:
            error_message = data['response'].get(
                'message', 'No message provided')
            raise APIRequestError(
                f'Error {response.status_code} : {error_message}')
    except requests.exceptions.RequestException as e:
        # Catch request-specific errors
        logger.error(f'Request failed: {e}')
        raise APIRequestError(f'Request failed: {e}')
    except Exception as e:
        # Catch other errors like invalid API key, etc.
        logger.error(f'An unexpected error occurred: {e}')
        raise
    return article_hits_info
