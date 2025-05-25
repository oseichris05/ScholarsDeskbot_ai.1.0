from flask import Flask, request, jsonify
import logging
from menus.router import route_message

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET'])
def index():
    return "ScholarDeskBot is Running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    app.logger.debug("Received update: %s", update)
    route_message(update)
    return jsonify({"status": "ok"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
