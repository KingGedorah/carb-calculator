from flask import Flask, render_template, request
import requests
from dotenv import load_dotenv
from flask_supabase import Supabase

load_dotenv()

app = Flask(__name__)