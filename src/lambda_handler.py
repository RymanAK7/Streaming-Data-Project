from retrieve_articles import retrieve_articles
from publish_to_kinesis import publish_to_kinesis
import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    """
    The Lambda handler function that gets invoked when the API endpoint is hit
    """
    try:
        query_params = event.get('queryStringParameters', {})
        search_term = query_params.get('search_term')
        kinesis_stream = query_params.get('kinesis_stream')
        from_date = query_params.get('from_date')
        if not search_term or not kinesis_stream:
            raise ValueError(
                "search_term and kinesis_stream are required parameters")
        logger.info(f'## Input Parameters: Search term ({search_term}), '
                    f'Date ({from_date}), Kinesis stream ({kinesis_stream})'
                    )
        articles = retrieve_articles(search_term, from_date=from_date)
        result, published_articles = publish_to_kinesis(
            kinesis_stream, search_term, articles)
        response = {
            "statusCode": 200,
            "body": json.dumps(
                {'result': result, 'articles_published': (published_articles)},
                indent=4,
                ensure_ascii=False
            )
        }
        logger.info(f'## Response returned: {response}')
        return response
    except Exception as e:
        logger.error(f'Error processing request: {e}')
        return {
            "statusCode": 500,
            "body": json.dumps({'error': str(e)}),
        }

print(lambda_handler({
    'queryStringParameters':{
        'kinesis_stream':'testhgf',
        'search_term':'ch'
    }
},''))