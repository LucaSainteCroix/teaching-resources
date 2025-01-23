import os
import pytest
import pickle
from azure.storage.blob import BlobClient, BlobServiceClient
from dotenv import load_dotenv

from utils.model_utils import import_model_from_azure

class TestAzureIntegration:
    @pytest.fixture(scope="class")
    def azure_credentials(self):
        """Fixture to load Azure credentials and create test resources"""
        load_dotenv()
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            pytest.skip("Azure credentials not available")
        return connection_string

    @pytest.fixture(scope="class")
    def test_container(self, azure_credentials):
        """Fixture to create and clean up a test container"""
        # Create a unique test container
        service_client = BlobServiceClient.from_connection_string(azure_credentials)
        container_name = "test-container-integration"

        try:
            container_client = service_client.create_container(container_name)
            yield container_name
        finally:
            # Cleanup: Delete the test container
            service_client.delete_container(container_name)

    @pytest.fixture
    def sample_model(self):
        """Fixture to create a sample model for testing"""
        class DummyModel:
            def predict(self, X):
                return [1, 2, 3]

        return {
            'model': DummyModel(),
            'metadata': {'version': '1.0'}
        }

    @pytest.fixture
    def uploaded_test_model(self, azure_credentials, test_container, sample_model):
        """Fixture to upload a test model and clean it up after"""
        blob_name = "test/model.pkl"

        # Upload the test model
        blob_client = BlobClient.from_connection_string(
            azure_credentials,
            container_name=test_container,
            blob_name=blob_name
        )

        pickled_model = pickle.dumps(sample_model)
        blob_client.upload_blob(pickled_model, overwrite=True)

        yield blob_name

        # Cleanup: Delete the test blob
        try:
            blob_client.delete_blob()
        except:
            pass

    def test_model_download_integration(self, azure_credentials, test_container, uploaded_test_model):
        """Test actual download from Azure"""
        # Set environment variables for the test
        os.environ["AZURE_STORAGE_CONNECTION_STRING"] = azure_credentials
        os.environ["AZURE_TEST_CONTAINER"] = test_container

        try:
            # Create the blob client
            blob_client = BlobClient.from_connection_string(
                azure_credentials,
                container_name=test_container,
                blob_name=uploaded_test_model
            )

            # Download and unpickle
            blob_data = blob_client.download_blob().readall()
            model_dict = pickle.loads(blob_data)

            # Assertions
            assert isinstance(model_dict, dict)
            assert 'model' in model_dict
            assert 'metadata' in model_dict
            assert model_dict['metadata']['version'] == '1.0'

        except Exception as e:
            pytest.fail(f"Failed to download model: {str(e)}")

    @pytest.mark.slow
    def test_end_to_end_model_workflow(self, azure_credentials, test_container, sample_model):
        """End-to-end test of upload and download"""
        blob_name = "test/e2e_model.pkl"

        # Upload
        blob_client = BlobClient.from_connection_string(
            azure_credentials,
            container_name=test_container,
            blob_name=blob_name
        )

        try:
            # Upload
            pickled_model = pickle.dumps(sample_model)
            blob_client.upload_blob(pickled_model, overwrite=True)

            # Download
            downloaded_data = blob_client.download_blob().readall()
            downloaded_model = pickle.loads(downloaded_data)

            # Verify
            assert isinstance(downloaded_model, dict)
            assert downloaded_model['metadata']['version'] == sample_model['metadata']['version']

        finally:
            # Cleanup
            try:
                blob_client.delete_blob()
            except:
                pass

    def test_error_handling(self, azure_credentials):
        """Test handling of various error conditions"""
        # Test with non-existent container
        with pytest.raises(Exception):
            blob_client = BlobClient.from_connection_string(
                azure_credentials,
                container_name="non-existent-container",
                blob_name="test.pkl"
            )
            blob_client.download_blob()

        # Test with invalid connection string
        with pytest.raises(Exception):
            BlobClient.from_connection_string(
                "invalid_connection_string",
                container_name="test",
                blob_name="test.pkl"
            )
