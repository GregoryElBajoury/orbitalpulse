import pytest
from unittest.mock import patch, MagicMock
import requests
from collector import fetch_iss_position

@patch("collector.requests.get")
def test_fetch_iss_position_success(mock_get):
    """Teste le comportement nominal : l'API répond avec des données valides."""
    # Simuler la réponse JSON de l'API
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "latitude": 45.123,
        "longitude": 1.456,
        "altitude": 420.5,
        "velocity": 27600.0,
        "visibility": "daylight"
    }
    mock_get.return_value = mock_response

    data = fetch_iss_position()

    assert data is not None
    assert data["latitude"] == 45.123
    assert data["altitude"] == 420.5
    assert data["visibility"] == "daylight"
    mock_get.assert_called_once()

@patch("collector.requests.get")
def test_fetch_iss_position_http_error(mock_get):
    """Teste la gestion d'une erreur HTTP (ex: 500 ou 404)."""
    mock_get.side_effect = requests.exceptions.HTTPError("Erreur serveur")

    data = fetch_iss_position()

    assert data is None
    mock_get.assert_called_once()