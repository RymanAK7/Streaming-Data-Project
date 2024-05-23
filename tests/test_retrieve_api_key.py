import pytest
from src.retrieve_api_key import retrieve_api_key
from moto import mock_secretsmanager
import boto3
from botocore.exceptions import (ClientError)
import os


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'test'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
    os.environ['AWS_SECURITY_TOKEN'] = 'test'
    os.environ['AWS_SESSION_TOKEN'] = 'test'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'


@pytest.fixture(scope="function")
def secrets_client(aws_credentials):
    with mock_secretsmanager():
        yield boto3.client("secretsmanager")


def test_retrieve_api_key_returns_secret_string(secrets_client):
    """check retrieve_credentials function always return
    a string"""

    secrets_client.create_secret(
        Name="guardian/api-key",
        SecretString="abc123"
    )
    output = retrieve_api_key("guardian/api-key")

    assert output == "abc123"


def test_retrieve_api_key_returns_error_when_secret_does_not_exist(
        secrets_client):
    """
        Check that retrieve_api_key raises a ClientError
        with a ResourceNotFoundException
        when attempting to retrieve a secret
        that does not exist in AWS Secrets Manager.

        This test creates a scenario where the
        specified secret does not exist and verifies
        that the retrieve_api_key function handles this
        by raising the appropriate exception.
    """

    secrets_client.create_secret(
        Name="guardian/api-key",
        SecretString="abc123"
    )

    with pytest.raises(ClientError) as exc_info:
        retrieve_api_key("Non_existent_secret")

    exception = 'ResourceNotFoundException'

    assert exc_info.value.response['Error']['Code'] == exception


def test_retrieve_api_key_raises_value_error_on_param_validation_error(
        secrets_client):
    """
    Test that retrieve_api_key raises a
    ValueError when a ParamValidationError
    is encountered.
    """

    secrets_client.create_secret(
        Name="guardian/api-key",
        SecretString="abc123"
    )

    with pytest.raises(ValueError):
        retrieve_api_key(2)
