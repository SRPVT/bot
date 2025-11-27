# Web server for keeping the Discord bot alive
# Import the Flask app from keep_alive.py
from keep_alive import app

# This file is used by gunicorn to serve the web application
if __name__ == "__main__":
    # This code won't run under gunicorn, but can be used for local testing
    app.run(host="0.0.0.0", port=5000)