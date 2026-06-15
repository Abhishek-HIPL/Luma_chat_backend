from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

message_count = 0

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    global message_count

    data = request.get_json()

    if not data:
        return jsonify({
            "locked": False,
            "reply": " Invalid request"
        })

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "locked": False,
            "reply": " Please enter a message."
        })

    message_count += 1

    # Free limit
    if message_count > 5:
        return jsonify({
            "locked": True,
            "reply": " Free limit reached. App download karke continue karein."
        })

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a friendly AI assistant.

                    Rules:
                    - Talk in natural English.
                    - Use emojis naturally 😊🔥✨🚀🥱😪😫.
                    - Be friendly and conversational.
                    - Keep replies engaging.
                    - Sound like a helpful friend.
                    """
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        )

        reply = response.choices[0].message.content

        return jsonify({
            "locked": False,
            "reply": reply,
            "remaining": max(0, 5 - message_count)
        })

    except Exception as e:
        return jsonify({
            "locked": False,
            "reply": f" Error: {str(e)}"
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
