import os
import pickle

from flask import Flask, request, jsonify

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

RUN_ID = os.getenv('MLFLOW_BEST_RUN_ID')

# Import the client object from the SDK library
from azure.storage.blob import BlobClient

# Retrieve the connection string from an environment variable. Note that a
# connection string grants all permissions to the caller, making it less
# secure than obtaining a BlobClient object using credentials.
conn_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

# Create the client object for the resource identified by the connection
# string, indicating also the blob container and the name of the specific
# blob we want.
blob_client = BlobClient.from_connection_string(
    conn_string,
    container_name="lsc-mlflow",
    blob_name=f"mlartifacts/1/{RUN_ID}/artifacts/model/model.pkl",
)

blob = blob_client.download_blob().readall()

model = pickle.loads(blob)

# logged_model = f's3://mlflow-models-alexey/1/{RUN_ID}/artifacts/model'
# logged_model = f'runs:/{RUN_ID}/model'
# model = mlflow.pyfunc.load_model(blob)



def prepare_features(ride):
    features = {}
    features['PU_DO'] = '%s_%s' % (ride['PULocationID'], ride['DOLocationID'])
    features['trip_distance'] = ride['trip_distance']
    return features


def predict(features):
    preds = model.predict(features)
    return float(preds[0])


app = Flask('duration-prediction')


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    ride = request.get_json()

    features = prepare_features(ride)
    pred = predict(features)

    result = {
        'duration': pred,
        'model_version': RUN_ID
    }

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9696)
