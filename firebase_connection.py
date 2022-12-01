import firebase_admin
from firebase_admin import credentials, firestore
import urllib.request
import json

class Firestore_Connection:
    def firebase_initialize():
        url = "https://firebasestorage.googleapis.com/v0/b/topes-projeto-python-2022.appspot.com/o/securityKey.json?alt=media&token=cdeea10a-6a34-46e7-82b3-4662bd7e29e8"
        response = urllib.request.urlopen(url)
        skey = dict(json.load(response))

        cred = credentials.Certificate(skey)
        return firebase_admin.initialize_app(cred)
    def firestore_client(app):
        return firestore.client(app)
