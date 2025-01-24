import os
import pytest
import pickle
import numpy as np
from azure.storage.blob import BlobClient
from dotenv import load_dotenv

from app.utils.model_utils import import_model_from_azure

class TestIntegrationModelUtils:
    @pytest.fixture(scope="class") # created once for the whole class
    def azure_credentials(self):
        """Fixture to load Azure credentials"""
        load_dotenv()
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            pytest.skip("Azure credentials not available")
        return connection_string



    def test_import_model_function(self, azure_credentials):
        """Test the actual import_model_from_azure function"""
        try:
            # Test with default run_id
            dv, model = import_model_from_azure()

            # Verify the returned objects
            assert hasattr(model, 'predict'), "Model should have predict method"
            assert hasattr(dv, 'transform'), "DictVectorizer should have transform method"

            # Optional: Test with a specific run_id
            # specific_run_id = "your-specific-run-id"  # replace with actual run_id
            # dv2, model2 = import_model_from_azure(run_id=specific_run_id)
            # assert hasattr(model2, 'predict'), "Model should have predict method"

        except Exception as e:
            pytest.fail(f"Failed to import model: {str(e)}")

    def test_model_predictions(self, azure_credentials):
        """Test if the downloaded model can make predictions"""
        try:
            dv, model = import_model_from_azure()

            # Test data - adjust according to your model's input requirements
            test_input = {
                "DOLocationID": "239",
                "PULocationID": "236",
                "trip_distance": 1.98
            }

            # Transform the input
            X = dv.transform([test_input])

            # Make prediction
            prediction = model.predict(X)

            # Verify prediction structure
            assert isinstance(prediction, (np.ndarray, list)), "Prediction should be array-like"
            assert len(prediction) == 1, "Should have one prediction for one input"

        except Exception as e:
            pytest.fail(f"Failed to make predictions: {str(e)}")




    # Bonus
    def test_error_handling(self, azure_credentials):
        """Test error handling scenarios"""
        # Test with non-existent run_id
        with pytest.raises(Exception):
            import_model_from_azure(run_id="non-existent-run-id")

        # Test with invalid connection string
        original_conn_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        try:
            os.environ["AZURE_STORAGE_CONNECTION_STRING"] = "invalid_connection_string"
            with pytest.raises(Exception):
                import_model_from_azure()
        finally:
            # Restore the original connection string
            os.environ["AZURE_STORAGE_CONNECTION_STRING"] = original_conn_string
