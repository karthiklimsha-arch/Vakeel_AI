from flask import Flask, render_template, request, jsonify, session, redirect
from model import search
from deep_translator import GoogleTranslator
from openai import OpenAI
import os

app = Flask(__name__)
app.secret_key = "secret123"

# 🔐 SAFE API KEY
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

query_count = 0


# -----------------------
# DOMAIN DETECTION
# -----------------------
def detect_domain(query):
    q = query.lower()

    if "article" in q:
        return "general"

    if any(w in q for w in ["drive", "vehicle", "license", "traffic", "drunk", "alcohol"]):
        return "motor"

    elif any(w in q for w in ["theft", "murder", "assault", "fraud"]):
        return "ipc"

    elif any(w in q for w in ["hack", "cyber", "otp", "password"]):
        return "cyber"

    return "general"


# -----------------------
# AI RESPONSE (SAFE FALLBACK)
# -----------------------
def generate_answer(context, query):
    try:
        if not os.getenv("OPENAI_API_KEY"):
            return context  # 🔥 NO API → fallback

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Explain laws simply."},
                {"role": "user", "content": f"{query}\n\nLaw:\n{context}"}
            ]
        )
        return response.choices[0].message.content

    except Exception as e:
        print("AI ERROR:", e)
        return context

def detect_language(text):
    try:
        return GoogleTranslator().detect(text)
    except:
        return "en"


def translate_to_english(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except:
        return text


def translate_from_english(text, target_lang):
    try:
        return GoogleTranslator(source='en', target=target_lang).translate(text)
    except:
        return text
# -----------------------
# LOGIN
# -----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["user"] = "admin"
            return redirect("/")
    return render_template("login.html")


# -----------------------
# HOME
# -----------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("index.html")


# -----------------------
# CHAT API
# -----------------------
@app.route("/ask", methods=["POST"])
def ask():
    global query_count
    query_count += 1

    try:
        data = request.get_json()
        original_query = data.get("query", "").strip()

        if not original_query:
            return jsonify({"response": "Enter a question", "source": ""})

        # 🌍 Detect language
        selected_lang = data.get("lang", "auto")

        if selected_lang == "auto":
            lang = detect_language(original_query)
        else:
            lang = selected_lang

        # 🔄 Translate to English
        query = translate_to_english(original_query)

        # 🧠 Your existing logic
        domain = detect_domain(query)
        results = search(query, domain)

        if not results:
            response = "No relevant law found."
        else:
            context = "\n".join([r["text"] for r in results])
            response = generate_answer(context, query)

        # 🔄 Translate back to user language
        final_response = translate_from_english(response, lang)

        return jsonify({
            "response": final_response,
            "source": domain.upper()
        })

    except Exception as e:
        print("SERVER ERROR:", e)
        return jsonify({
            "response": "Server error occurred",
            "source": "ERROR"
        })

# -----------------------
# ADMIN
# -----------------------
@app.route("/admin")
def admin():
    return render_template("admin.html", count=query_count)


# -----------------------
if __name__ == "__main__":
    app.run(debug=True)