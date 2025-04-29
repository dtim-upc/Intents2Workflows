from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
from utils.llm_text_to_intent import get_prediction

# --- Configuration ---
MODEL = "phi4"
BASE_PATH = "/intent2Workflow-textToIntent"

# --- Blueprint Setup ---
intent_api = Blueprint('intent_api', __name__, url_prefix=BASE_PATH)

routes_info = {
    f"{BASE_PATH}/predictIntent": {
        "method": "POST",
        "description": "Classify text and return the intent.",
        "request_body": {
            "text": "string"
        },
        "response": {
            "intent": "string",
            "model": "string"
        },
        "example_usage": {
            "curl": f'curl -X POST http://localhost:8001{BASE_PATH}/predictIntent -H "Content-Type: application/json" -d \'{{"text": "Your text to classify"}}\''
        }
    }
}

@intent_api.route('/', methods=['GET'])
def base_route():
    return jsonify(routes_info), 200

@intent_api.route('/predictIntent', methods=['POST'])
def predict():
    try:
        data = request.json
        text = data.get("text")

        if not text or text.strip() == "":
            return jsonify({"error": "Text parameter is required."}), 400

        prediction = get_prediction(text, MODEL)
        return jsonify({"intent": prediction, "model": MODEL}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- App Setup ---
app = Flask(__name__)
CORS(app)
app.register_blueprint(intent_api)

if __name__ == '__main__':
    app.run(debug=True, port=9003)
