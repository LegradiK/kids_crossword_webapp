from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import json, os

from game_logic import build_puzzle

load_dotenv("data.env")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_KEY")

_base_dir = os.path.dirname(__file__)


# ── Word-bank loader ──────────────────────────────────────────────────────────
def _load_bank(env_var, clue_key):
    path = os.path.join(_base_dir, os.getenv(env_var, ""))
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        return {
            cat["label"]: [(w["word"], w[clue_key]) for w in cat["words"]]
            for cat in raw["categories"].values()
        }
    except FileNotFoundError:
        return {}


WORD_BANK    = _load_bank("WORDS_FILE",    "clue")
PICTURE_BANK = _load_bank("PICTURES_FILE", "clue")


# ── Routes ────────────────────────────────────────────────────────────────────
def _render_index(initial_mode="advanced"):
    return render_template(
        "index.html",
        topics=list(WORD_BANK.keys()),
        beginner_topics=list(PICTURE_BANK.keys()),
        initial_mode=initial_mode,
    )


@app.route("/")
def index():
    return _render_index("beginner")


@app.route("/beginner")
def beginner():
    return _render_index("beginner")


@app.route("/advanced")
def advanced():
    return _render_index("advanced")


@app.route("/api/puzzle")
def api_puzzle():
    mode  = request.args.get("mode", "advanced")
    bank  = PICTURE_BANK if mode == "beginner" else WORD_BANK
    topic = request.args.get("topic", "")
    if topic not in bank:
        topic = next(iter(bank), None)
    if not topic:
        return jsonify({"error": "no topics available for this mode"}), 404
    puzzle = build_puzzle(bank[topic])
    puzzle["mode"]  = mode
    puzzle["topic"] = topic
    return jsonify(puzzle)


@app.route("/api/check", methods=["POST"])
def api_check():
    data    = request.get_json()
    answers = data.get("answers", {})
    correct = data.get("words",   {})
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
