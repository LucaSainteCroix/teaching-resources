import pickle
import os
from dotenv import load_dotenv, find_dotenv
from azure.storage.blob import BlobClient



def import_model(model_name):
    with open(f'app/assets/{model_name}.bin', 'rb') as f_in:
        (dv, model) = pickle.load(f_in)
    return dv, model

def import_model_from_azure(run_id=None):

    _ = load_dotenv(find_dotenv())

    RUN_ID = run_id or os.getenv('MLFLOW_BEST_RUN_ID')

    # Retrieve the connection string from an environment variable. Note that a
    # connection string grants all permissions to the caller, making it less
    # secure than obtaining a BlobClient object using credentials.
    conn_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    # Create the client object for the resource identified by the connection
    # string, indicating also the blob container and the name of the specific
    # blob we want.
    blob_client = BlobClient.from_connection_string(
        conn_string,
        container_name="lsc-mlflow",
        blob_name=f"mlartifacts/1/{RUN_ID}/artifacts/model/model.pkl",
    )

    blob = blob_client.download_blob().readall()

    dv, model = pickle.loads(blob)

    return dv, model

def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    dv, model = import_model('lin_reg')
    # dv, model = import_model_from_azure()
    X = dv.transform(features)
    preds = model.predict(X)
    return float(preds[0])
