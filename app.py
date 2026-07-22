from flask import Flask, request, render_template, jsonify
from genarate_message import generate_cover_message, verify_message

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    job_description = data.get("job_description", "")
    resume = data.get("resume", "")

    if not job_description or not resume:
        return jsonify({"error": "Both fields are required"}), 400

    message = generate_cover_message(job_description, resume)
    flagged = verify_message(message, resume)

    return jsonify({
        "message": message,
        "flagged": flagged
    })

if __name__ == "__main__":
    app.run(debug=True)