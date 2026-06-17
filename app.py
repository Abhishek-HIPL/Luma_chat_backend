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
    api_key=os.getenv("OPENAI_API_KEY")
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
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are a friendly AI companion.

                    You can talk about:
                    - Casual conversations
                    - Daily life
                    - Fun topics
                    - Emotions
                    - Motivation
                    - Entertainment
                    - Light-hearted discussions

                    Restricted topics:
                    - Coding
                    - Programming
                    - Technical support
                    - Science
                    - Mathematics
                    - Medical advice
                    - Legal advice
                    - Financial advice
                    - Family counselling
                    - Career guidance
                    - Education

                    When a restricted topic is asked:

                    DO NOT answer the question.

                    Instead, politely redirect the conversation using a DIFFERENT response every time.

                    Examples:

                    - 😊 That's a bit outside what I chat about. Tell me something fun about your day instead!

                    - ✨ I'm more into friendly conversations than technical stuff. What's been on your mind lately?

                    - 😄 I can't really help with that topic, but I'd love to chat about movies, music, hobbies, or daily life.

                    - 🌸 That's not something I cover, but I'm always here for a good conversation.

                    - 💬 Let's switch to something more fun. What's something exciting that happened recently?

                    Never repeat the exact same refusal sentence every time.
                    Keep responses natural and varied.
                    """
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.8,
            max_tokens=500
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
