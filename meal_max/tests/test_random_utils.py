import pytest
from unittest.mock import patch, Mock
from requests.exceptions import Timeout, RequestException

# Adjust the import statement according to your project structure
from meal_max.utils.random_utils import get_random


@patch('meal_max.utils.random_utils.requests.get')
def test_get_random_success(mock_get):
    """Test that get_random returns the correct float when the request is successful."""
    # Mock the response from requests.get
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = '0.42\n'
    mock_get.return_value = mock_response

    random_number = get_random()

    assert random_number == 0.42
    mock_get.assert_called_once_with(
        "https://www.random.org/decimal-fractions/?num=1&dec=2&col=1&format=plain&rnd=new",
        timeout=5
    )


@patch('meal_max.utils.random_utils.requests.get')
def test_get_random_invalid_response(mock_get):
    """Test that get_random raises ValueError when the response is invalid."""
    # Mock the response with invalid text
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = 'invalid_number\n'
    mock_get.return_value = mock_response

    with pytest.raises(ValueError) as excinfo:
        get_random()
    assert str(excinfo.value) == "Invalid response from random.org: invalid_number"


@patch('meal_max.utils.random_utils.requests.get')
def test_get_random_timeout(mock_get):
    """Test that get_random raises RuntimeError on request timeout."""
    # Simulate a timeout exception
    mock_get.side_effect = Timeout()

    with pytest.raises(RuntimeError) as excinfo:
        get_random()
    assert str(excinfo.value) == "Request to random.org timed out."


@patch('meal_max.utils.random_utils.requests.get')
def test_get_random_request_exception(mock_get):
    """Test that get_random raises RuntimeError on general request exceptions."""
    # Simulate a general request exception
    mock_get.side_effect = RequestException("Some error")

    with pytest.raises(RuntimeError) as excinfo:
        get_random()
    assert str(excinfo.value) == "Request to random.org failed: Some error"


@patch('meal_max.utils.random_utils.requests.get')
def test_get_random_http_error(mock_get):
    """Test that get_random raises RuntimeError when response status is not 200."""
    # Mock response with a non-200 status code
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.raise_for_status.side_effect = RequestException("Internal Server Error")
    mock_get.return_value = mock_response

    with pytest.raises(RuntimeError) as excinfo:
        get_random()
    assert str(excinfo.value) == "Request to random.org failed: Internal Server Error"
