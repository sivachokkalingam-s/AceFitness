from flask import Flask, request, jsonify, render_template
import logic

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/init')
def init_db():
    logic.init_db()
    return jsonify({"message": "Database initialized"})


@app.route('/client', methods=['POST'])
def api_save_client():
    data = request.json
    result = logic.save_client(
        data['name'],
        int(data['age']),
        float(data['weight']),
        data['program']
    )
    return jsonify(result)


@app.route('/client/<name>', methods=['GET'])
def api_load_client(name):
    result = logic.load_client(name)
    return jsonify(result)


@app.route('/progress', methods=['POST'])
def api_save_progress():
    data = request.json
    result = logic.save_progress(
        data['name'],
        int(data['adherence'])
    )
    return jsonify(result)


@app.route('/save_client', methods=['POST'])
def save_client():
    data = request.form
    result = logic.save_client(
        data['name'],
        int(data['age']),
        float(data['weight']),
        data['program']
    )
    return render_template('index.html', message=result)


@app.route('/load_client', methods=['POST'])
def load_client():
    name = request.form['name']
    result = logic.load_client(name)

    # Format output like Tkinter summary
    if "error" not in result:
        summary = f"""
CLIENT PROFILE
--------------
Name     : {result['name']}
Age      : {result['age']}
Weight   : {result['weight']} kg
Program  : {result['program']}
Calories : {result['calories']} kcal/day
"""
    else:
        summary = result["error"]

    return render_template('index.html', summary=summary)


@app.route('/save_progress', methods=['POST'])
def save_progress():
    data = request.form
    result = logic.save_progress(
        data['name'],
        int(data['adherence'])
    )
    return render_template('index.html', message=result)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
