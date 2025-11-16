# AI Virtual Travel Guide (Ai-Projectt)

A lightweight Python-based prototype that demonstrates a utility-driven AI travel planner. The project includes:
- A small data scaffold stored inside a .docx file (travel_data.docx).
- Core planning logic (search algorithms, utility scoring, itinerary generation).
- A Streamlit UI for interactive planning and visualization.

This README explains how to install, run, and extend the project.

---

## Table of Contents
- [Demo](#demo)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the app](#running-the-app)
- [Project structure](#project-structure)
- [Data format](#data-format)
- [How it works (high level)](#how-it-works-high-level)
- [Customization](#customization)
- [Development & Contributing](#development--contributing)
- [Troubleshooting](#troubleshooting)
- [TODO / Roadmap](#todo--roadmap)
- [License & Contact](#license--contact)

---

## Demo
- The app is a local Streamlit application. It reads travel data from `travel_data.docx`, scores destinations by a simple utility function, and generates a rule-based itinerary for the top destination.

---

## Features
- Auto-generates `travel_data.docx` with sample JSON (if missing).
- Simple BFS/DFS/A* inspired algorithms used as examples:
  - BFS for budget filtering
  - DFS for activity exploration
  - A* heuristic (Euclidean distance) for distance scoring
- Utility-based ranking of destinations with a rule-based itinerary generator.
- Streamlit UI (`travel_ui.py`) to interact with the agent.

---

## Requirements
- Python 3.8+
- Dependencies in `requirements.txt`:
  - streamlit
  - python-docx

Install with:
```bash
pip install -r requirements.txt
```

---

## Installation
1. Clone the repository:
```bash
git clone https://github.com/Wahajulhaq7/Ai-Projectt.git
cd Ai-Projectt
```

2. (Optional) Create and activate a virtual environment:
```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Running the app

Option A — Quick start (recommended)
```bash
python main.py
```
- `main.py` will ensure `travel_data.docx` exists (creating it with sample JSON if needed) and then launches the Streamlit UI (`travel_ui.py`).

Option B — Direct Streamlit run
```bash
streamlit run travel_ui.py
```

Open the local Streamlit URL printed in the terminal (usually http://localhost:8501).

---

## Project structure
- main.py
  - Ensures `travel_data.docx` exists and launches the Streamlit UI.
- requirements.txt
  - Project dependencies.
- travel_core.py
  - Core domain logic: data loader, Destination model, SearchAlgorithms, TravelAgent and ItineraryPlanner.
- travel_ui.py
  - Streamlit-based user interface that collects input, runs planning, and displays results.
- travel_data.docx (generated at runtime if not present)
  - Contains JSON describing destinations.

---

## Data format
Data is stored as raw JSON text inside `travel_data.docx`. The app expects the JSON to contain a `destinations` array. Example (simplified):

{
  "destinations": [
    {
      "id": "kyoto_jp",
      "name": "Kyoto",
      "country": "Japan",
      "avg_daily_cost": 150,
      "best_season_score": {"spring": 10, "summer": 7, "autumn": 9, "winter": 5},
      "tags": ["culture","history","gardens","food","art"],
      "coords": [10,50],
      "activities": {
        "history": ["Fushimi Inari","Nijo Castle"],
        "food": ["Nishiki Market"]
      },
      "hotel_reco": "Traditional Ryokan in Gion"
    },
    ...
  ]
}

Notes:
- `coords` are arbitrary 2D coordinates used by the simple distance heuristic (not actual lat/long).
- The code will create a `travel_data.docx` with a sample dataset if it does not exist.

---

## How it works (high level)
1. Data loading: `load_json_from_docx()` reads the .docx and parses the JSON.
2. Filtering: BFS-style filter for budget.
3. Scoring: Utility function combines interest match, budget fit, season suitability, and a distance score to compute `utility_score` for each destination.
4. Planning: The itineraries are generated rule-based and use a DFS-inspired routine to pick activities.
5. UI: Streamlit (travel_ui.py) gathers inputs (budget, duration, season, interests) and shows the chosen destination, utility breakdown, and a day-by-day itinerary.

---

## Customization
- Add or edit destinations by updating `travel_data.docx` content or by replacing it with your own JSON text (inside the docx).
- Adjust scoring weights in `TravelAgent.calculate_utility_scores()` in `travel_core.py`.
- Expand the activity selection logic or add more rules in `ItineraryPlanner.generate_itinerary()`.

---

## Development & Contributing
- Create a branch for changes:
  git checkout -b feature/describe-feature
- Run the app locally and make changes to `travel_core.py` or `travel_ui.py`.
- Add unit tests under a `tests/` directory and run with pytest (not included yet).
- Consider adding GitHub Actions for CI and linting.

---

## Troubleshooting
- If `streamlit` command not found:
  - Ensure dependencies installed: `pip install -r requirements.txt`
  - Or run `python main.py` (it calls streamlit internally — but still requires streamlit to be installed).
- If the UI shows a data load error:
  - Confirm `travel_data.docx` exists and contains valid JSON (the app will create one if missing).
- If docx JSON parsing fails:
  - Open `travel_data.docx` and ensure the JSON is the only content or is valid JSON when concatenating all paragraphs.

---

## TODO / Roadmap
- Add unit tests and CI configuration (GitHub Actions).
- Replace docx-based data storage with JSON/YAML or a small database for easier editing and versioning.
- Add more realistic coordinates (lat/long) and proper routing for distance heuristics.
- Add model-backed recommendations (e.g., collaborative filtering or embeddings).
- Improve UI/UX and add export options (PDF, calendar).

---

## License & Contact
- No license selected yet. Add a LICENSE file (e.g., MIT) to clarify reuse terms.
- Repository owner: Wahajulhaq7 — https://github.com/Wahajulhaq7
