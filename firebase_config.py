import streamlit as st
import firebase_admin
from firebase_admin import credentials, db

if not firebase_admin._apps:

    cred = credentials.Certificate(dict(st.secrets["firebase"]))

    firebase_admin.initialize_app(
        cred,
        {
            "databaseURL":
            "https://predectivemaintenance-aef92-default-rtdb.firebaseio.com/"
        }
    )

root = db.reference("/")
