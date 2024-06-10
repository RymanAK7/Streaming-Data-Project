import requests
from src.retrieve_api_key import retrieve_api_key
from src.fetch_article_content import fetch_content_preview
import logging
from typing import List, Dict, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIRequestError(Exception):
    pass


def retrieve_articles(
        search_terms: str, from_date: str = None) -> Union[str, List[Dict]]:
    """
    Retrieves articles from the Guardian API based on search terms and date.

    Args:
        search_terms (str): The search terms to query.
        from_date (str, optional): The start date for the search
        in YYYY-MM-DD format. If not provided, defaults to None,
        in which case most relevant articles will be retrieved

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
        logger.info('Making a request to the Guardian API.')
        base_url = "http://content.guardianapis.com/search"
        params = f'order-by=relevance&q={search_terms}'
        if from_date:
            params = f'from-date={from_date}&{params}'
        logger.info(f'Request URL: {base_url}?{params}')
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
        logger.error(f'Request failed: {e}')
        raise APIRequestError(f'Request failed: {e}')
    except Exception as e:
        logger.error(f'An unexpected error occurred: {e}')
        raise
    return article_hits_info
