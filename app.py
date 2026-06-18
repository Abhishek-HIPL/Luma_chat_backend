from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_key TEXT PRIMARY KEY,
        message_count INTEGER DEFAULT 0
    )
    """)

    conn.commit()
    conn.close()

init_db()

app = Flask(__name__)
CORS(app)


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data:
        return jsonify({
            "locked": False,
            "reply": "Invalid request"
        })

    fingerprint = data.get("fingerprint", "")

    ip = request.headers.get(
        "X-Forwarded-For",
        request.remote_addr
    )

    user_key = f"{fingerprint}_{ip}"


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

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT message_count FROM users WHERE user_key=?",
        (user_key,)
    )

    row = cursor.fetchone()

    if row:
        count = row[0]
    else:
        count = 0

    if count >= 5:
        conn.close()

        return jsonify({
            "locked": True,
            "reply": "Free limit reached"
        })

    count += 1

    cursor.execute("""
    INSERT OR REPLACE INTO users
    (user_key, message_count)
    VALUES (?, ?)
    """, (user_key, count))

    conn.commit()
    conn.close()
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
                    - Image generation when user asks for pictures, wallpapers, art, avatars, or illustrations.

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

                    - 🌸 That's not something I cover,but I'm always here for a good conversation.

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
            "remaining": max(0, 5 - count)
        })

    except Exception as e:
        return jsonify({
            "locked": False,
            "reply": f" Error: {str(e)}"
        }), 500




if __name__ == "__main__":
    app.run(debug=True)
