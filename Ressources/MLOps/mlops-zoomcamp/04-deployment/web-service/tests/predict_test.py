import pytest
from unittest.mock import patch, MagicMock

from predict import app, prepare_features, import_model


def test_prepare_features():

    ride = {
        "PULocationID": 130,
        "DOLocationID": 205,
        "trip_distance": 3.66,
    }

    actual_features = prepare_features(ride)

    expected_features = {
        "PU_DO": "130_205",
        "trip_distance": 3.66,
    }

    assert actual_features == expected_features


def test_import_model():
    dv, model = import_model('lin_reg')
    assert dv is not None
    assert model is not None



@pytest.fixture
def client():
    # Flask provides a way to test your app without running a server
    with app.test_client() as client:
        yield client


def test_predict_endpoint(client):
    # Mock import_model in the context of the endpoint call
    with patch('predict.import_model') as mock_import:
        # Mock dv and model
        mock_dv = MagicMock()
        mock_model = MagicMock()

        mock_dv.transform.return_value = [[0.5, 1.5]]
        mock_model.predict.return_value = [20.0]

        mock_import.return_value = (mock_dv, mock_model)

        # Perform a POST request to the /predict endpoint
        ride_data = {
            'PULocationID': '10',
            'DOLocationID': '20',
            'trip_distance': 4.5
        }
        response = client.post('/predict', json=ride_data)

        assert response.status_code == 200
        json_data = response.get_json()
        assert 'duration' in json_data

        # Check that the mocks were called as expected
        mock_dv.transform.assert_called_once_with({
            'PU_DO': '10_20',
            'trip_distance': 4.5
        })
        mock_model.predict.assert_called_once()


# test_cases = [
#     ({"PU_DO": "10_20", "trip_distance": 3.0}, 12.34),
#     ({"PU_DO": "30_40", "trip_distance": 10.0}, 45.67)
# ]
# @pytest.mark.parametrize("features, expected_prediction", test_cases)
# def test_predict(features, expected_prediction):
#     # Mock import_model in the context of the endpoint call
#     with patch('predict.import_model') as mock_import:
#         # Mock dv and model
#         mock_dv = MagicMock()
#         mock_model = MagicMock()

#         mock_dv.transform.return_value = [[0.5, 1.5]]
#         mock_model.predict.return_value = [20.0]

#     # Act
#     result = predict(features)

#     # Assert
#     assert result == expected_prediction
