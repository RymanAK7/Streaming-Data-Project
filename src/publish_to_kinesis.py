import boto3
from botocore.exceptions import (
    NoCredentialsError, PartialCredentialsError, ClientError)
from typing import List, Dict, Tuple
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def publish_to_kinesis(stream_name: str, partition_key: str,
                       list_articles: List[Dict]) -> Tuple[str, List[Dict]]:
    """
    Publishes a list of articles to a Kinesis stream.

    Parameters:
        stream_name (str): The name of the Kinesis stream
        to publish the articles to.
        partition_key (str): The partition key
        to use when publishing articles - the search term.
        list_articles (List[Dict]): A list
        of dictionaries representing articles.
            Each dictionary should contain the following keys:
            - 'webPublicationDate': The publication date of the article.
            - 'webTitle': The title of the article.
            - 'webUrl': The URL of the article.
            - 'contentPreview': Content preview of the article.

    Returns:
        Tuple[str, List[Dict]]: A tuple containing a success message and a list
        of dictionaries representing articles that were successfully published.

    Raises:
        ClientError: If there is an error in the
        client (e.g., invalid parameters).
        PartialCredentialsError: If only partial credentials are available.
        NoCredentialsError: If no credentials are found.
        Exception: For any unexpected errors encountered during publishing.
    """
    success_count = 0
    published_articles = []
    try:
        kinesis_client = boto3.client('kinesis')

        for index, article in enumerate(list_articles):
            article_json = json.dumps(article, indent=4, ensure_ascii=False)
            response = kinesis_client.put_record(
                StreamName=stream_name,
                Data=article_json.encode('utf-8'),
                PartitionKey=partition_key,
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                success_count += 1
                published_articles.append(list_articles[index])
            else:
                logging.error(f"Failed to publish article: {article}")

        if success_count == 0:
            return (
                f"Failed to add any records to Kinesis stream: {stream_name}"
            ), published_articles
        elif success_count < len(list_articles):
            return (
                f"Only added {success_count} out of {len(list_articles)} "
                f"records to Kinesis stream: {stream_name}"
            ), published_articles
        else:
            return (
                f"Successfully added all {success_count} records "
                f"to Kinesis stream: {stream_name}"
            ), published_articles

    except ClientError as e:
        logger.error(
            f"ClientError: {e}")
        raise e

    except PartialCredentialsError as e:
        logger.error((f"PartialCredentialsError: {e}"))
        raise e
    except NoCredentialsError as e:
        logger.error((f"NoCredentialsError: {e}"))
        raise e
    except Exception as e:
        logger.error(f"Unexpected error adding records to Kinesis stream: {e}")
        raise e
