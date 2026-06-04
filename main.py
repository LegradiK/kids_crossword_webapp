from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import json, os

from game_logic import build_puzzle

load_dotenv("data.env")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_KEY")

# ── Load word bank ────────────────────────────────────────────────────────────
_base_dir  = os.path.dirname(__file__)
_json_path = os.path.join(_base_dir, os.getenv("WORDS_FILE"))

with open(_json_path, encoding="utf-8") as f:
    _raw = json.load(f)

# Convert {word, clue} dicts to (word, clue) tuples, keyed by human label
WORD_BANK = {
    cat["label"]: [(w["word"], w["clue"]) for w in cat["words"]]
    for cat in _raw["categories"].values()
}


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", topics=list(WORD_BANK.keys()))


@app.route("/api/puzzle")
def api_puzzle():
    topic = request.args.get("topic", "Animals")
    if topic not in WORD_BANK:
        topic = next(iter(WORD_BANK))
    puzzle = build_puzzle(WORD_BANK[topic])
    puzzle["topic"] = topic
    return jsonify(puzzle)


@app.route("/api/check", methods=["POST"])
def api_check():
    data    = request.get_json()
    answers = data.get("answers", {})   # {"1A": "CAT", "2D": "DOG", ...}
    correct = data.get("words",   {})   # correct answers sent from client
    result  = {}
    for key, guess in answers.items():
        right = correct.get(key, "")
        if guess.upper() == right.upper():
            result[key] = "correct"
        elif guess.strip() == "":
            result[key] = "empty"
        else:
            result[key] = "wrong"
    return jsonify(result)


if __name__ == "__main__":
    app.run(
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true",
        port=int(os.getenv("FLASK_PORT", 5050)),
    )