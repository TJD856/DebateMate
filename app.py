from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
import PyPDF2
import nltk
import spacy
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL Config
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "Cnsp2003"
app.config["MYSQL_DB"] = "mydatabase"

mysql = MySQL(app)
bcrypt = Bcrypt(app)

# Load NLP Models
nlp = spacy.load("en_core_web_sm")
nltk.download("punkt")

# Helper: Extract text from PDF
def extract_pdf_text(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

constitution_text = extract_pdf_text(r"C:\\users\\Pradeeth\\OneDrive\\Desktop\\Tech Terminators Project\\IPC_sections.pdf")

# Routes
@app.route("/")
def login():
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO sample (username, password) VALUES (%s, %s)", (username, password))
            mysql.connection.commit()
            return redirect(url_for("login"))
        except:
            return "Username already exists!"
    return render_template("signup.html")

@app.route("/login", methods=["POST"])
def login_post():
    username = request.form["username"]
    password = request.form["password"]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM sample WHERE username = %s", (username,))
    user = cur.fetchone()
    if user and bcrypt.check_password_hash(user[2], password):
        session["user_id"] = user[0]
        return redirect(url_for("home"))
    return "Invalid credentials!"

@app.route("/home")
def home():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("home.html")

@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    query = request.json.get("query")
    user_id = session["user_id"]

    # Search for relevant information in the PDF text
    response = "Sorry, I couldn't find an answer."
    doc = nlp(constitution_text)
    sentences = [sent.text for sent in doc.sents if query.lower() in sent.text.lower()]

    if sentences:
        response = " ".join(sentences[:5])  # Return up to 5 sentences for context

    # Store query and response in the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO queries (user_id, query_text, response_text) VALUES (%s, %s, %s)",
                (user_id, query, response))
    mysql.connection.commit()

    return jsonify({"response": response})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
