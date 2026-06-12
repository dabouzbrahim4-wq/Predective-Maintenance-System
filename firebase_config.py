import os
import firebase_admin
from firebase_admin import credentials, db

if not firebase_admin._apps:

    firebase_credentials = {
        "type": os.environ["type"],
        "project_id": os.environ["project_id"],
        "private_key_id": os.environ["private_key_id"],
        "private_key": os.environ["private_key"].replace("\\n", "\n"),
        "client_email": os.environ["client_email"],
        "client_id": os.environ["client_id"],
        "auth_uri": os.environ["auth_uri"],
        "token_uri": os.environ["token_uri"],
        "auth_provider_x509_cert_url": os.environ["auth_provider_x509_cert_url"],
        "client_x509_cert_url": os.environ["client_x509_cert_url"],
        "universe_domain": os.environ["universe_domain"]
    }

    cred = credentials.Certificate(firebase_credentials)

    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL":
            "https://predectivemaintenance-aef92-default-rtdb.firebaseio.com/"
        }
    )

root = db.reference("/")
