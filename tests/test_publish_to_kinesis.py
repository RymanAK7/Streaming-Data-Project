import pytest
from src.publish_to_kinesis import publish_to_kinesis
from moto import mock_kinesis
import boto3
from botocore.exceptions import (
    NoCredentialsError, PartialCredentialsError, ClientError)
from unittest.mock import patch
import os
import json

articles = [
    {
        "webPublicationDate": "2024-05-01T12:00:00Z",
        "webTitle": "Sample Article 1",
        "webUrl": "http://example.com/article1",
        "contentPreview": "This is a preview of article 1."
    },
    {
        "webPublicationDate": "2024-05-02T12:00:00Z",
        "webTitle": "Sample Article 2",
        "webUrl": "http://example.com/article2",
        "contentPreview": "This is a preview of article 2."
    }
]


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'test'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'test'
    os.environ['AWS_SECURITY_TOKEN'] = 'test'
    os.environ['AWS_SESSION_TOKEN'] = 'test'
    os.environ['AWS_DEFAULT_REGION'] = 'eu-west-2'


@pytest.fixture(scope="function")
def aws_kinesis(aws_credentials):
    """Mock AWS Kinesis client with a created stream for testing."""
    with mock_kinesis():
        client = boto3.client("kinesis", region_name='eu-west-2')
        client.create_stream(StreamName="test_stream", ShardCount=1)
        yield client


def test_publish_to_kinesis_adds_all_articles_to_stream(aws_kinesis):
    """
    Test that the publish_to_kinesis function
    adds all articles to the stream successfully
    and verfies the records in the stream.
    """
    partition_key = 'test-search'
    stream_name = "test_stream"
    output = publish_to_kinesis(stream_name, partition_key, articles)[0]

    assert output == (
        f"Successfully added all {len(articles)} records "
        f"to Kinesis stream: {stream_name}"
    )
    response = aws_kinesis.get_shard_iterator(
        StreamName=stream_name,
        ShardId='shardId-000000000000',
        ShardIteratorType='TRIM_HORIZON'
    )
    shard_iterator = response['ShardIterator']

    response = aws_kinesis.get_records(ShardIterator=shard_iterator, Limit=10)

    records = response['Records']
    assert len(records) == len(articles)

    for i, record in enumerate(records):
        data = json.loads(record['Data'])
        assert data == articles[i]


def test_publish_to_kinesis_no_records_added_failure(aws_kinesis):
    """Test that publish_to_kinesis function
    handles failure when no articles are added."""
    stream_name = "test_stream"
    output = publish_to_kinesis(stream_name, "test_search", [])
    assert output == (
        f"Failed to add any records to Kinesis stream: {stream_name}"
    )


def test_publish_to_kinesis_invalid_input():
    """Test that publish_to_kinesis function
    raises an exception for invalid input."""
    with pytest.raises(Exception):
        publish_to_kinesis("test_stream", "test_search", None)


def test_publish_to_kinesis_Client_Error(aws_kinesis):
    """Test handling of ClientError."""
    with pytest.raises(ClientError):
        publish_to_kinesis("non_existent_stream", "test_search", articles)


@patch('boto3.client')
def test_publish_to_kinesis_partial_credentials_error(mock_boto_client):
    """Test handling of PartialCredentialsError."""
    mock_boto_client.side_effect = PartialCredentialsError(
        provider='aws', cred_var='test_var')

    with pytest.raises(PartialCredentialsError):
        publish_to_kinesis("test_stream", "test_search", articles)


@patch('boto3.client')
def test_publish_to_kinesis_no_credentials_error(mock_boto_client):
    """Test handling of NoCredentialsError."""
    mock_boto_client.side_effect = NoCredentialsError()
    with pytest.raises(NoCredentialsError):
        publish_to_kinesis("test_stream", "test_search", articles)
