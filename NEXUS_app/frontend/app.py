#!/usr/bin/env python3
"""Nexus Platform - Frontend Web Application"""
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import os, json, logging, requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "dev-secret-key-change-in-production"
)
app.config["API_BASE_URL"] = os.environ.get("API_BASE_URL", "http://localhost:8000")

# Enable CORS
CORS(app)

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    print("Starting Nexus Platform Frontend...")
    socketio.run(app, host="0.0.0.0", port=8001, debug=True, allow_unsafe_werkzeug=True)


@app.route("/dashboard/<dashboard_type>")
def dashboard(dashboard_type):
    return render_template("dashboard.html", dashboard_type=dashboard_type)
