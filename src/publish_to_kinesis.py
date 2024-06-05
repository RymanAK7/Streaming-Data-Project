import boto3
from botocore.exceptions import (
    NoCredentialsError, PartialCredentialsError, ClientError)
from typing import List, Dict
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def publish_to_kinesis(stream_name: str, partition_key: str,
                       list_articles: List[Dict]) -> str:
    """
    Publish a list of articles to a Kinesis stream.

    Parameters:
    stream_name (str): The name of the Kinesis stream.
    list_articles (List[Dict]): A list of dictionaries,
    each containing article info with keys:
    'webPublicationDate','webTitle','webUrl',
    and 'contentPreview'.

    Returns:
    str: Success message indicating records added to Kinesis stream.
    """
    # Track number of successful records
    success_count = 0
    try:
        # Initialize Kinesis client
        kinesis_client = boto3.client('kinesis')

        for article in list_articles:
            # Convert article to JSON string
            article_json = json.dumps(article, indent=4, ensure_ascii=False)
            response = kinesis_client.put_record(
                StreamName=stream_name,
                Data=article_json.encode('utf-8'),  # Encode data to bytes
                # Use search_term as the partition key
                PartitionKey=partition_key,
            )
            if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                success_count += 1
            else:
                logging.error(f"Failed to publish article: {article}")

        # Generate return message based on success_count
        if success_count == 0:
            return (
                f"Failed to add any records to Kinesis stream: {stream_name}"
            )
        elif success_count < len(list_articles):
            return (
                f"Only added {success_count} out of {len(list_articles)} "
                f"records to Kinesis stream: {stream_name}"
            )
        else:
            return (
                f"Successfully added all {success_count} records "
                f"to Kinesis stream: {stream_name}"
            )

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
