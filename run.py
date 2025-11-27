# Single entry point for both web server and bot
import logging
import threading
import time
import os
import sys
from flask import Flask, render_template_string
import discord
from bot import run_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('run')

# Create Flask app for the web server
app = Flask(__name__)

@app.route('/')
def home():
    """Root endpoint for uptime monitoring"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Editor's Helper Discord Bot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #1e1e1e;
                color: #f0f0f0;
            }
            .container {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            h1 {
                color: #7289da;
                text-align: center;
            }
            .status {
                background-color: #3a3a3a;
                border-radius: 5px;
                padding: 10px;
                margin-top: 20px;
            }
            .commands {
                margin-top: 20px;
            }
            .command {
                background-color: #3a3a3a;
                border-radius: 5px;
                padding: 10px;
                margin-bottom: 10px;
            }
            .online {
                color: #43b581;
                font-weight: bold;
            }
            .footer {
                margin-top: 20px;
                text-align: center;
                font-size: 12px;
                color: #999;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 Editor's Helper Discord Bot</h1>
            
            <div class="status">
                <p>Bot Status: <span class="online">Online</span></p>
                <p>This page indicates that the Discord bot is currently running.</p>
            </div>
            
            <div class="commands">
                <h2>Available Commands</h2>
                
                <div class="command">
                    <h3>!help or !hi</h3>
                    <p>Get a simple greeting in your DMs</p>
                </div>
                
                <div class="command">
                    <h3>!list</h3>
                    <p>View all available commands</p>
                </div>
                
                <div class="command">
                    <h3>!files</h3>
                    <p>View available files</p>
                </div>
                
                <div class="command">
                    <h3>!software_list</h3>
                    <p>View all software-related commands</p>
                </div>
                
                <div class="command">
                    <h3>!presets</h3>
                    <p>View all color correction presets (.ffx files)</p>
                </div>
                
                <div class="command">
                    <h3>Software Commands</h3>
                    <p>!aecrack, !pscrack, !mecrack, !prcrack, !topazcrack</p>
                </div>
            </div>
            
            <div class="footer">
                <p>This bot serves as a helper for video editors, providing color correction presets and information.</p>
                <p>Created by bmr</p>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/ping')
def ping():
    """Simple ping endpoint for uptime monitoring"""
    logger.info("Ping received - bot is online")
    return 'Pong! Bot is online.', 200

@app.route('/restart')
def restart():
    """Endpoint to restart the bot process"""
    import subprocess
    import threading
    
    def restart_bot():
        try:
            subprocess.run(['bash', 'restart.sh'])
            logger.info("Restart script executed")
        except Exception as e:
            logger.error(f"Error restarting bot: {str(e)}")
    
    # Run restart in background
    thread = threading.Thread(target=restart_bot)
    thread.daemon = True
    thread.start()
    
    return 'Restart initiated. Bot should restart shortly.', 200

def run_flask():
    """Run the Flask web server on port 8080"""
    try:
        app.run(host='0.0.0.0', port=8080, threaded=True)
    except Exception as e:
        logger.error(f"Flask server error: {str(e)}")
        # Try to restart the server
        time.sleep(5)
        run_flask()

def run_bot_with_retry():
    """Run the Discord bot with automatic restart on failure"""
    while True:
        try:
            logger.info("Starting Discord bot...")
            run_bot()
        except Exception as e:
            logger.error(f"Discord bot crashed: {str(e)}")
            logger.info("Restarting Discord bot in 10 seconds...")
            time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Bot shutdown requested")
            break

if __name__ == "__main__":
    try:
        # Start the Flask server in a separate thread
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True  # This makes the thread exit when the main program exits
        flask_thread.start()
        logger.info("Web server started in background thread")
        
        # Run the Discord bot in the main thread
        run_bot_with_retry()
    except Exception as e:
        logger.critical(f"Critical error in main process: {str(e)}")
        # For a truly persistent service, restart the entire process
        logger.info("Restarting entire process in 10 seconds...")
        time.sleep(10)
        os.execv(sys.executable, ['python'] + sys.argv)