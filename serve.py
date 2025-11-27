# Simple wrapper to expose the keep_alive web server directly
from keep_alive import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)