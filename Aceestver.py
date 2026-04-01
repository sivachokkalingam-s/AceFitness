from flask import Flask, request, jsonify
import logic

app = Flask(__name__)

# Initialize DB once
@app.route('/init', methods=['GET'])
def init():
    logic.init_db()
    return jsonify({"message": "Database initialized"})


# Save Client (same as button click)
@app.route('/client', methods=['POST'])
def save_client():
    data = request.json

    try:
        calories = logic.save_client(
            data["name"],
            data["age"],
            data["weight"],
            data["program"]
        )
        return jsonify({
            "message": "Client saved",
            "calories": calories
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# Load Client (same as load button)
@app.route('/client/<name>', methods=['GET'])
def load_client(name):
    data = logic.load_client(name)

    if not data:
        return jsonify({"error": "Client not found"}), 404

    return jsonify(data)


# Save Progress
@app.route('/progress', methods=['POST'])
def save_progress():
    data = request.json

    logic.save_progress(
        data["name"],
        data["adherence"]
    )

    return jsonify({"message": "Progress saved"})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)