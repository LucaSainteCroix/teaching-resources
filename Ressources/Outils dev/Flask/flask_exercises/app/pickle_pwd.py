import pickle

db_credentials = {'username': 'root', 'password': 'example'}

with open('db_credentials.p', 'wb+') as f:

  pickle.dump(db_credentials, f)