from src.lambda_handler import lambda_handler
import pytest
from moto import mock_kinesis
import boto3
from unittest.mock import patch


@pytest.fixture(scope="function")
def aws_kinesis():
    """Mock AWS Kinesis client with a created stream for testing."""
    with mock_kinesis():
        client = boto3.client("kinesis", region_name='eu-west-2')
        client.create_stream(StreamName="test_stream", ShardCount=1)
        yield client


@patch('src.lambda_handler.retrieve_articles')
def test_lambda_handler_valid_params(
        mock_retrieve_articles, aws_kinesis):
    """
    Test Lambda handler with valid parameters.
    """
    # Mock the return value of retrieve_articles
    mock_retrieve_articles.return_value = [
        {
            "webPublicationDate": "2024-05-01T12:00:00Z",
            "webTitle": "Sample Article 1",
            "webUrl": "http://example.com/article1",
            "contentPreview": "This is a preview of article 1."
        }]

    event = {
        'queryStringParameters': {
            'search_term': 'test_search',
            'kinesis_stream': 'test_stream',
            # Optional: 'from_date':'2024-05-05'
        }
    }
    context = {}
    response = lambda_handler(event, context)
    assert (response['statusCode']) == 200
    assert 'result' in response['body']


@patch('src.lambda_handler.retrieve_articles')
def test_lambda_handler_missing_search_term(
        mock_retrieve_articles):
    """
    Test Lambda handler with missing search term.
    """
    event = {
        'queryStringParameters': {
            # Missing 'search_term'
            'kinesis_stream': 'test_stream',
            # Optional: 'from_date':'2024-05-05'
        }
    }
    context = {}
    response = lambda_handler(event, context)
    assert response['statusCode'] == 500
    assert 'error' in response['body']


def test_lambda_handler_missing_kinesis_stream():
    """
    Test Lambda handler with missing kinesis stream.
    """
    event = {
        'queryStringParameters': {
            'search_term': 'test_search',
            # Missing 'kinesis_stream'
            # Optional: 'from_date':'2024-05-05'
        }
    }
    context = {}
    response = lambda_handler(event, context)
    assert response['statusCode'] == 500
    assert 'error' in response['body']
