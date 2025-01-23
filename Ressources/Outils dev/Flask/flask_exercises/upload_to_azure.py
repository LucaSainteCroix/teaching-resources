import os
from azure.storage.blob import BlobClient
from dotenv import load_dotenv, find_dotenv

def upload_bin_to_azure(
    file_path: str,
    container_name: str,
    blob_name: str,
    connection_string: str = None
) -> str:
    """
    Upload a binary file to Azure Blob Storage.

    Args:
        file_path: Path to the .bin file
        container_name: Name of the container in Azure Blob Storage
        blob_name: Name for the blob in Azure
        connection_string: Azure storage connection string

    Returns:
        str: URL of the uploaded blob
    """
    # Get connection string from environment if not provided
    if connection_string is None:
        load_dotenv()
        connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        if not connection_string:
            raise ValueError("No connection string provided or found in environment")

    # Create the blob client
    blob_client = BlobClient.from_connection_string(
        connection_string,
        container_name=container_name,
        blob_name=blob_name
    )

    # Upload the binary file
    with open(file_path, 'rb') as data:
        blob_client.upload_blob(data, overwrite=True)

    return blob_client.url

# Usage example
if __name__ == "__main__":
    try:
        load_dotenv(find_dotenv())
        run_id = os.getenv("MLFLOW_BEST_RUN_ID")
        url = upload_bin_to_azure(
            file_path='app/assets/lin_reg.bin',
            container_name='lsc-mlflow',  # your container name
            blob_name=f'mlartifacts/1/{run_id}/artifacts/model/model.pkl'  # desired path in blob storage
        )
        print(f"Successfully uploaded to: {url}")

    except Exception as e:
        print(f"Error uploading file: {str(e)}")
