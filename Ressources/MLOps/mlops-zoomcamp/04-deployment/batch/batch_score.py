#!/usr/bin/env python
# coding: utf-8

import os
import io

import uuid
import pickle
import argparse
from flask import Flask, request, jsonify

from azure.storage.blob import BlobClient
from datetime import datetime

import pandas as pd

from dateutil.relativedelta import relativedelta


from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())


def generate_uuids(n):
    ride_ids = []
    for i in range(n):
        ride_ids.append(str(uuid.uuid4()))
    return ride_ids


def read_dataframe(filename: str):

    conn_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    blob = get_blob_from_azure(conn_string, "taxi-trip-input-data", filename)
    blob_str = blob.decode('utf-8')

    df = pd.read_csv(io.StringIO(blob_str), parse_dates=['lpep_pickup_datetime', 'lpep_dropoff_datetime'])

    df['duration'] = df.lpep_dropoff_datetime - df.lpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60
    df = df[(df.duration >= 1) & (df.duration <= 60)]

    df['ride_id'] = generate_uuids(len(df))

    return df


def prepare_dictionaries(df: pd.DataFrame):
    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)

    df['PU_DO'] = df['PULocationID'] + '_' + df['DOLocationID']

    categorical = ['PU_DO']
    numerical = ['trip_distance']
    dicts = df[categorical + numerical].to_dict(orient='records')
    return dicts

def get_blob_from_azure(conn_string, container_name, blob_path):

    blob_client = BlobClient.from_connection_string(
        conn_string,
        container_name=container_name,
        blob_name=blob_path,
    )

    blob = blob_client.download_blob().readall()

    return blob

def load_model(run_id):
    conn_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

    blob_path = f"mlartifacts/1/{run_id}/artifacts/model/model.pkl"

    blob = get_blob_from_azure(conn_string, "lsc-mlflow", blob_path)

    model = pickle.loads(blob)
    return model


def save_results(df, y_pred, run_id, output_file):
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['lpep_pickup_datetime'] = df['lpep_pickup_datetime']
    df_result['PULocationID'] = df['PULocationID']
    df_result['DOLocationID'] = df['DOLocationID']
    df_result['actual_duration'] = df['duration']
    df_result['predicted_duration'] = y_pred
    df_result['diff'] = df_result['actual_duration'] - df_result['predicted_duration']
    df_result['model_version'] = run_id

    # df_result.to_csv(output_file, index=False)
    csv_string = df_result.to_csv(index=False)
    csv_bytes = str.encode(csv_string)

    conn_string = os.environ["AZURE_STORAGE_CONNECTION_STRING"]

    blob_client = BlobClient.from_connection_string(
        conn_string,
        container_name="taxi-fare-batch-scoring-outputs",
        blob_name=output_file,
    )

    blob_client.upload_blob(csv_bytes, overwrite=True)



def apply_model(input_file, run_id, output_file):

    df = read_dataframe(input_file)
    dicts = prepare_dictionaries(df)

    model = load_model(run_id)

    y_pred = model.predict(dicts)

    save_results(df, y_pred, run_id, output_file)
    return output_file


def get_paths(run_date, taxi_type, run_id):
    prev_month = run_date - relativedelta(months=1)
    year = prev_month.year
    month = prev_month.month
    input_file = f'{taxi_type}_tripdata_{year:04d}-{month:02d}.csv'
    # input_file = f's3://nyc-tlc/trip data/{taxi_type}_tripdata_{year:04d}-{month:02d}.parquet'
    output_file = f'taxi_type={taxi_type}/year={year:04d}/month={month:02d}/{run_id}.csv'

    return input_file, output_file



def ride_duration_prediction(
        taxi_type: str,
        run_id: str,
        run_date: datetime = None):
    if run_date is None:
        run_date = datetime.now()

    input_file, output_file = get_paths(run_date, taxi_type, run_id)

    apply_model(
        input_file=input_file,
        run_id=run_id,
        output_file=output_file
    )
    return output_file


app = Flask('duration-prediction')


@app.route('/batch_predict', methods=['POST'])
def batch_predict():

    # # If you want to use Python arguments (to run as script and not Flask)
    # parser = argparse.ArgumentParser(description='Taxi Fare Model Batch Scoring')
    # parser.add_argument('taxi_type', type=str, help='The taxi type (e.g. "green")')
    # parser.add_argument('year', type=int, help='The year (e.g. 2021)')
    # parser.add_argument('month', type=int, help='The month (e.g. 3)')
    # parser.add_argument('run_id', type=str, help='The run ID (e.g. "53ed06ef39724cdc85896f22c72b2f78")')

    # args = parser.parse_args()
    args = request.get_json()

    run_date = datetime(year=args.get('year'), month=args.get('month'), day=1)

    output_file = ride_duration_prediction(
        taxi_type=args.get('taxi_type'),
        run_id=args.get('run_id'),
        run_date=run_date
    )

    return jsonify({'output_file': output_file})


if __name__ == '__main__':
    # batch_predict()
    app.run(debug=True, host='0.0.0.0', port=8080)
