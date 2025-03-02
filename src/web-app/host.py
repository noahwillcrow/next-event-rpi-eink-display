from flask import Flask, redirect, url_for, session, render_template, request, send_file
from google_auth_oauthlib.flow import Flow
import os
import uuid
import yaml

# Flask App Setup
app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Change this to a secure random string

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # 👈 Allow HTTP for local testing

# OAuth Configuration
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

PORT = 5001

# Define your redirect URI (Update with your actual domain)
REDIRECT_URI = (
    "http://localhost:"
    + str(PORT)
    + "/oauth2callback"  # Update if using ngrok or SSH tunneling
)

# OAuth Flow
flow = Flow.from_client_secrets_file(
    "../../oauth-secrets.json", scopes=SCOPES, redirect_uri=REDIRECT_URI
)


@app.route("/")
def index():
    return send_file("index.html")


@app.route("/index.css")
def indexcss():
    return send_file("index.css")


@app.route("/index.js")
def indexjs():
    return send_file("index.js")


@app.route("/calendars")
def get_calendars():
    config = load_config_yaml()
    calendars = config["events"]["calendars"]
    return {"calendars": calendars}


@app.route("/calendars", methods=["POST"])
def update_calendars():
    config = load_config_yaml()
    print(request.json)
    print(config)
    config["events"]["calendars"] = request.json["calendars"]
    write_config_yaml(config)
    return {"calendars": config["events"]["calendars"]}


@app.route("/oauth-login")
def login():
    """Initiate OAuth login flow."""
    auth_url, state = flow.authorization_url(prompt="consent")
    session["state"] = state
    return redirect(auth_url)


@app.route("/oauth2callback")
def oauth2callback():
    """Handle OAuth callback and save credentials."""
    print(request)
    flow.fetch_token(authorization_response=request.url)

    creds = flow.credentials
    creds_json = creds.to_json()
    creds_file_uuid = uuid.uuid4()
    with open("../../" + creds_file_uuid + "-credentials.json", "w") as f:
        f.write(creds_json)

    config = load_config_yaml()
    config["events"]["calendars"].append(
        {
            "type": "google-oauth",
            "name": "New OAuth Calendar",
            "client-id": creds.client_id,
        }
    )
    write_config_yaml(config)

    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    """Clear the session and log out the user."""
    session.pop("credentials", None)
    return redirect(url_for("index"))


CONFIG_PATH = "../../config.yaml"


def load_config_yaml() -> dict:
    """This function reads the config yaml file and returns the content as a dictionary."""
    with open(CONFIG_PATH, 'r') as file:
        config = yaml.safe_load(file)
    return config


def write_config_yaml(config: dict):
    """This function writes the config dictionary to the config yaml file."""
    with open(CONFIG_PATH, 'w') as file:
        yaml.dump(config, file)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)
