from flask import Flask, send_from_directory
from flask.ext.cors import CORS


app = Flask(__name__)
app.secret_key = 'MPbYC1wUIQ1vGT2rQR3k'
cors = CORS(app)
from app import views
