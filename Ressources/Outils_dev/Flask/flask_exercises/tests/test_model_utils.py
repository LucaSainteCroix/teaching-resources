import os
import pytest
from unittest.mock import patch, MagicMock, mock_open
import pickle
import numpy as np

from app.utils.model_utils import import_model_from_azure, prepare_features, predict




class MockDictVectorizer:
    """A simple mock class that can be pickled"""
    def transform(self, X):
        return np.array([[1.0]])

class MockModel:
    """A simple mock class that can be pickled"""
    def predict(self, X):
        return np.array([42.0])

class TestModelUtils:
    def test_import_model_from_azure(self):
        """
        Test importing a model from Azure Blob Storage.
        We'll mock the Azure BlobClient and environment variables.
        """
        # Create mock objects for our model components
        mock_dv = MockDictVectorizer()
        mock_model = MockModel()

        # with
        mock_pickle_data = pickle.dumps((mock_dv, mock_model))

        # Create a mock blob response
        mock_blob_response = MagicMock()
        mock_blob_response.readall.return_value = mock_pickle_data

        # Create a mock blob client
        mock_blob_client = MagicMock()
        mock_blob_client.download_blob.return_value = mock_blob_response

        # Mock environment variables and BlobClient
        with patch('app.utils.model_utils.load_dotenv'):
            with patch.dict('os.environ', {
                'MLFLOW_BEST_RUN_ID': 'test_run_id',
                'AZURE_STORAGE_CONNECTION_STRING': 'test_connection'
            }):
                with patch('app.utils.model_utils.BlobClient') as MockBlobClient:
                    # Configure the mock BlobClient
                    MockBlobClient.from_connection_string.return_value = mock_blob_client

                    # Call the function
                    dv, model = import_model_from_azure()

                    # Verify BlobClient was created correctly
                    MockBlobClient.from_connection_string.assert_called_once_with(
                        'test_connection',
                        container_name='lsc-mlflow',
                        blob_name='mlartifacts/1/test_run_id/artifacts/model/model.pkl'
                    )

                    # Verify the blob was downloaded
                    mock_blob_client.download_blob.assert_called_once()

                    # Test that the returned objects work as expected
                    assert hasattr(dv, 'transform')
                    assert hasattr(model, 'predict')

    def test_prepare_features(self):
        """
        Test the feature preparation function with sample ride data.
        This doesn't need mocking as it's a pure function.
        """
        # Sample ride data
        ride = {
            'PULocationID': 100,
            'DOLocationID': 200,
            'trip_distance': 10.5
        }

        # Expected features
        expected_features = {
            'PU_DO': '100_200',
            'trip_distance': 10.5
        }

        # Call the function and verify results
        features = prepare_features(ride)
        assert features == expected_features

    def test_predict(self):
        """
        Test the prediction function.
        We'll mock the model import and prediction.
        """
        # Create mock objects
        mock_dv = MagicMock()
        mock_model = MagicMock()

        # Configure the mocks
        mock_dv.transform.return_value = np.array([[1.0, 2.0]])
        mock_model.predict.return_value = np.array([42.0])

        # Mock the model import function
        with patch('app.utils.model_utils.import_model_from_azure',
                  return_value=(mock_dv, mock_model)):
            # Test features
            features = {
                'PU_DO': '100_200',
                'trip_distance': 10.5
            }

            # Call predict
            prediction = predict(features)

            # Verify the prediction pipeline
            mock_dv.transform.assert_called_once()
            mock_model.predict.assert_called_once()
            assert prediction == 42.0
