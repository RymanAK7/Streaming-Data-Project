import unittest
from unittest.mock import patch, Mock
from src.retrieve_articles import retrieve_articles, APIRequestError
import pytest
import requests


class TestRetrieveArticles(unittest.TestCase):
    """Unit tests for the retrieve_articles function."""

    @patch('src.retrieve_articles.requests.get')
    @patch('src.retrieve_articles.retrieve_api_key',
           return_value='test_api_key')
    def test_successful_request(self, mock_retrieve_api_key, mock_get):
        """
        Test retrieve_articles function for a successful API request.

        This test mocks the requests.get call and the retrieve_api_key
        function to simulate a successful response from the Guardian API.
        It checks that the function correctly processes the response and
        returns the expected list of articles.
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': {
                'results': [
                    {'webUrl': 'test_url',
                     'webPublicationDate': 'test_date',
                     'webTitle': 'test_title'}
                ]
            }
        }
        mock_response.url = 'http://example.com'
        mock_get.return_value = mock_response

        with patch(
            'src.retrieve_articles.fetch_content_preview'
        ) as mock_fetch_content_preview:
            mock_fetch_content_preview.return_value = 'test_content_preview'

            articles = retrieve_articles('TEST')

        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]['webUrl'], 'test_url')
        self.assertEqual(articles[0]['webPublicationDate'], 'test_date')
        self.assertEqual(articles[0]['webTitle'], 'test_title')
        self.assertEqual(
            articles[0]['contentPreview'],
            'test_content_preview...')

    @patch('src.retrieve_articles.requests.get')
    @patch('src.retrieve_articles.retrieve_api_key',
           return_value='test_api_key')
    def test_unsuccessful_requests_4xx_5xx_errors(
            self, mock_retrieve_api_key, mock_get):
        """
        Test retrieve_articles function for unsuccessful
        API requests resulting in 4xx or 5xx errors.

        This test mocks the requests.get call and
        the retrieve_api_key function to simulate
        an unsuccessful response from the Guardian API.
        It checks that the function raises
        an APIRequestError in response to a 404 status code.
        """
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.return_value = {
            'response': {
                'message': 'Not found'
            }
        }
        mock_get.return_value = mock_response

        with pytest.raises(APIRequestError):
            retrieve_articles('test_search_term', 'test_date')

    @patch('src.retrieve_articles.requests.get')
    @patch('src.retrieve_articles.retrieve_api_key',
           return_value='test_api_key')
    def test_successful_request_multiple_articles(
            self, mock_retrieve_api_key, mock_get):
        """Test retrieve_articles for a successful
        API request with multiple articles."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': {
                'results': [
                    {'webUrl': 'test_url_1',
                     'webPublicationDate': 'test_date_1',
                     'webTitle': 'test_title_1'},
                    {'webUrl': 'test_url_2',
                     'webPublicationDate': 'test_date_2',
                     'webTitle': 'test_title_2'}
                ]
            }
        }
        mock_response.url = 'http://example.com'
        mock_get.return_value = mock_response

        with patch(
            'src.retrieve_articles.fetch_content_preview'
        ) as mock_fetch_content_preview:
            mock_fetch_content_preview.side_effect = [
                'test_content_preview_1',
                'test_content_preview_2'
            ]

            articles = retrieve_articles('TEST', '2024-05-01')

        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]['webUrl'], 'test_url_1')
        self.assertEqual(articles[0]['webPublicationDate'], 'test_date_1')
        self.assertEqual(articles[0]['webTitle'], 'test_title_1')
        self.assertEqual(
            articles[0]['contentPreview'],
            'test_content_preview_1...')
        self.assertEqual(articles[1]['webUrl'], 'test_url_2')
        self.assertEqual(articles[1]['webPublicationDate'], 'test_date_2')
        self.assertEqual(articles[1]['webTitle'], 'test_title_2')
        self.assertEqual(
            articles[1]['contentPreview'],
            'test_content_preview_2...')

    @patch('src.retrieve_articles.requests.get')
    @patch('src.retrieve_articles.retrieve_api_key',
           return_value='dummy_api_key')
    def test_empty_results(self, mock_retrieve_api_key, mock_get):
        """Test retrieve_articles when the API returns no articles."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'response': {
                'results': []
            }
        }
        mock_response.url = 'http://example.com'
        mock_get.return_value = mock_response

        articles = retrieve_articles('TEST')

        self.assertEqual(len(articles), 0)

    @patch('src.retrieve_articles.requests.get')
    @patch('src.retrieve_articles.retrieve_api_key',
           return_value='test_api_key')
    def test_invalid_api_key(self, mock_retrieve_api_key, mock_get):
        """Test retrieve_articles with an invalid API key."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {
            'response': {
                'message': 'Invalid authentication credentials'
            }
        }

        mock_get.return_value = mock_response

        with self.assertRaises(APIRequestError):
            retrieve_articles('TEST')

    @patch('src.retrieve_articles.requests.get')
    @patch('src.retrieve_articles.retrieve_api_key',
           return_value='test_api_key')
    def test_invalid_date_format(self, mock_retrieve_api_key, mock_get):
        """Test retrieve_articles with an invalid date format."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'response': {
                'message': 'Invalid date format'
            }
        }

        mock_get.return_value = mock_response

        with self.assertRaises(APIRequestError):
            retrieve_articles('TEST', 'invalid-date-format')

    @patch('src.retrieve_articles.requests.get')
    @patch('src.retrieve_articles.retrieve_api_key',
           return_value='test_api_key')
    def test_network_error(self, mock_retrieve_api_key, mock_get):
        """Test retrieve_articles with a network error.
        By mocking requests.get to raise a ConnectionError."""

        mock_get.side_effect = requests.exceptions.ConnectionError

        with self.assertRaises(APIRequestError):
            retrieve_articles('TEST', '2024-05-01')

    @patch('src.retrieve_articles.requests.get')
    @patch('src.retrieve_articles.retrieve_api_key',
           return_value='test_api_key')
    def test_general_exception_handling(self, mock_retrieve_api_key, mock_get):
        """Test retrieve_articles for general exception handling.
        By mocking requests.get to raise a general exception.
        """
        mock_get.side_effect = Exception('Unexpected error')

        with self.assertRaises(Exception):
            retrieve_articles('TEST')
