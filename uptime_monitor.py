import logging
import os
import threading
import time
import subprocess
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('uptime_monitor')

app = Flask(__name__)

def check_process_running(name):
    """Check if a process with the given name is running"""
    try:
        output = subprocess.check_output(["ps", "aux"]).decode()
        return name in output
    except Exception as e:
        logger.error(f"Error checking process: {e}")
        return False

def check_bot_heartbeat():
    """Check if the bot's heartbeat file is recent"""
    try:
        if not os.path.exists('.heartbeat'):
            return False
        
        with open('.heartbeat', 'r') as f:
            last_heartbeat = float(f.read().strip())
        
        # Check if heartbeat is more than 5 minutes old
        return time.time() - last_heartbeat < 300
    except Exception as e:
        logger.error(f"Error checking heartbeat: {e}")
        return False

def restart_bot_if_needed():
    """Check if the bot needs restarting and restart it if so"""
    while True:
        try:
            if not check_process_running("python main.py") or not check_bot_heartbeat():
                logger.warning("Bot appears to be down, restarting...")
                try:
                    subprocess.run(['bash', 'restart.sh'])
                    logger.info("Restart script executed")
                except Exception as e:
                    logger.error(f"Error running restart script: {e}")
            else:
                logger.debug("Bot appears to be running normally")
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
        
        # Check every 5 minutes
        time.sleep(300)

@app.route('/monitor')
def monitor():
    """Endpoint that checks both the web service and the Discord bot"""
    bot_running = check_process_running("python main.py")
    bot_heartbeat_ok = check_bot_heartbeat()
    
    status = {
        "web_server": True,  # If this responds, web server is up
        "discord_bot_process": bot_running,
        "discord_bot_heartbeat": bot_heartbeat_ok,
        "all_systems_ok": bot_running and bot_heartbeat_ok
    }
    
    # If all is well, return 200, otherwise 503
    if status["all_systems_ok"]:
        return jsonify(status), 200
    else:
        # Trigger restart if needed
        if not bot_running or not bot_heartbeat_ok:
            try:
                subprocess.Popen(['bash', 'restart.sh'])
                status["restart_initiated"] = True
            except Exception as e:
                logger.error(f"Error restarting: {e}")
                status["restart_initiated"] = False
                status["restart_error"] = str(e)
        
        return jsonify(status), 503

if __name__ == "__main__":
    # Start the monitoring thread
    monitor_thread = threading.Thread(target=restart_bot_if_needed)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Run the Flask app
    port = int(os.environ.get('MONITOR_PORT', 8081))
    app.run(host='0.0.0.0', port=port)