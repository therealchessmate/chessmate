from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from data.helper_functions import load_config
from ml.dispatcher_app import DispatcherApp

app = Flask(__name__)
CORS(app)  # Allows cross-origin requests (useful for frontend dev)

# Initialize once
try:
    config = load_config()
    dispatcher_app = DispatcherApp.start(config)
except Exception as e:
    dispatcher_app = None
    print(f"Error initializing dispatcher: {e}")

@app.route("/")
def home():
    return render_template("index.html")  # Serve templates/index.html

@app.route("/analyse", methods=["POST"])
def analyse():
    if dispatcher_app is None:
        return jsonify({"error": "Server not initialized"}), 500

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    username = data.get("username")
    platform_name = data.get("platform_name")
    number_of_games = data.get("number_of_games", 10)

    if not username or not platform_name:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        df = dispatcher_app.analyse(username, platform_name, number_of_games=int(number_of_games))
        return jsonify(df.to_dict(orient="records"))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(debug=True)
