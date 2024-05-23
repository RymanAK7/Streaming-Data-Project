import boto3
from botocore.exceptions import (ClientError, ParamValidationError,
                                 ConnectTimeoutError, NoCredentialsError)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def retrieve_api_key(secret_name: str) -> str:
    """
    Retrieve the API key from AWS Secrets Manager.

    Args:
        secret_name (str): The name of the secret in AWS Secrets Manager.

    Returns:
        str: The retrieved secret string.
    """

    logger.info('Interacting with AWS Secretsmanager')
    try:
        secrets_manager = boto3.client("secretsmanager")
        logger.info('Attempting to retrieve Guardian API Key')
        response = secrets_manager.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == "ResourceNotFoundException":
            logger.error(
                f"Secrets Manager can't find the\
 specified secret: {secret_name}")
        else:
            logger.error(f"An unexpected error occured: {error_code}")
        raise e
    except ParamValidationError as e:
        raise ValueError(
            f"The parameters you provided are incorrect: {e}")
    except NoCredentialsError as e:
        logger.error(
            "AWS credentials not found. Please configure AWS credentials.")
        raise e
    except ConnectTimeoutError as e:
        logger.error("Connection to AWS timed out. Please try again later.")
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise e
    secret = response['SecretString']
    if secret:
        logger.info('Successfully retreieved the secret string.')
    else:
        logger.error("SecretString not found in the response.")
        raise ValueError("SecretString not found in the response.")
    return secret


try:
    secret_name = "guardian/api-key"
    api_key = retrieve_api_key(secret_name=secret_name)
except Exception as e:
    logger.error(f"Error occurred: {str(e)}")
