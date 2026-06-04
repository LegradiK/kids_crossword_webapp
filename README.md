# Letter Quest — Crossword Puzzles for Kids

A browser-based crossword puzzle app aimed at KS1 children (ages 5–7). It runs two difficulty modes from the same interface:

- **Beginner** — emoji picture clues; kids look at a picture and spell the word
- **Advanced** — text clues; kids read a hint and work out the answer

Check, Reveal, and Clear work the same way in both modes. The active cell is highlighted with a bold border as letters are typed.

---

## Features

- Procedurally generated crossword grid — a fresh layout every time
- Two word banks: `words.json` (text clues) and `pictures.json` (emoji clues)
- 22 topic categories per bank (Animals, Food, Space, Transport, etc.)
- Score bar tracking words solved and checks used
- Win banner when all words are completed
- About modal explaining how to play

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, Flask 3.1 |
| Templating | Jinja2 |
| Frontend | Vanilla JS, CSS (no frameworks) |
| Fonts | Google Fonts — Fredoka One, Nunito |
| Config | `python-dotenv` / `data.env` |

---

## Project structure

```
kids_crossword_webapp/
├── main.py              # Flask app — routes and word-bank loading
├── game_logic.py        # Crossword generation algorithm
├── data.env             # Environment variables (keys, file paths, port - not committed)
├── static/
│   ├── style.css        # All styling
│   ├── words.json       # Advanced mode word bank
│   └── pictures.json    # Beginner mode word bank (emoji clues)
├── templates/
│   └── index.html       # Single-page app template + JS
└── venv/                # Python virtual environment (not committed)
```

---

## Setup

### 1. Clone and enter the project

```bash
git clone https://github.com/LegradiK/kids_crossword_webapp.git
cd kids_crossword_webapp
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install flask python-dotenv
```

### 4. Configure `data.env`

```env
FLASK_KEY=your-secret-key-here
FLASK_DEBUG=true
FLASK_PORT=5050
WORDS_FILE=/absolute/path/to/static/words.json
PICTURES_FILE=/absolute/path/to/static/pictures.json
```

### 5. Run

```bash
python main.py
```

Open `http://localhost:5050` in a browser.

---

## Word bank format

Both JSON files share the same top-level structure. The only difference is the clue field name.

### `words.json` — Advanced mode

```json
{
  "categories": {
    "animals": {
      "label": "Animals",
      "words": [
        { "word": "ELEPHANT", "clue": "The largest land animal" },
        { "word": "GIRAFFE",  "clue": "Has a very long neck" }
      ]
    }
  }
}
```

### `pictures.json` — Beginner mode

```json
{
  "categories": {
    "animals": {
      "label": "Animals",
      "words": [
        { "word": "CAT",  "clue": "🐱" },
        { "word": "BEAR", "clue": "🐻" }
      ]
    }
  }
}
```

**Rules for adding words:**

- `word` must be **uppercase**, letters only
- `clue` is a plain text hint (advanced) or a single emoji (beginner)
- Category `label` is what appears in the topic dropdown
- Aim for at least **10–15 words per category** so the generator has enough to build a connected grid
- Shorter words (3–6 letters) cross more easily and make better puzzles

---

## How the crossword generator works (`game_logic.py`)

1. Words are shuffled and placed one at a time onto a 22×22 internal grid
2. The first word goes across the centre
3. Each subsequent word is tried at every possible crossing point with already-placed words; the placement with the most letter overlaps wins
4. Up to 10 generation attempts are made to ensure at least 5 words are placed
5. The grid is cropped to its bounding box and numbered top-to-bottom, left-to-right
6. The result is serialised to JSON and sent to the browser

---

## Routes

| Route | Description |
|---|---|
| `GET /` | Main app (defaults to Beginner mode) |
| `GET /beginner` | Main app, Beginner mode pre-selected |
| `GET /advanced` | Main app, Advanced mode pre-selected |
| `GET /api/puzzle?topic=Animals&mode=beginner` | Returns a generated puzzle as JSON |
