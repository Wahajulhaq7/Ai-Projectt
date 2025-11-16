import os
import subprocess
from docx import Document

# --- 1. Data Definitions for docx Generation ---
DATA_FILE = "travel_data.docx"

SAMPLE_JSON = """
{
  "destinations": [
    {
      "id": "kyoto_jp",
      "name": "Kyoto",
      "country": "Japan",
      "avg_daily_cost": 150, 
      "best_season_score": {"spring": 10, "summer": 7, "autumn": 9, "winter": 5},
      "tags": ["culture", "history", "gardens", "food", "art"],
      "coords": [10, 50],
      "activities": {
        "history": ["Fushimi Inari-taisha Shrine", "Nijo Castle"],
        "culture": ["Traditional Tea Ceremony", "Gion District Stroll"],
        "food": ["Nishiki Market Exploration"],
        "gardens": ["Kinkaku-ji (Golden Pavilion)", "Ryoan-ji Rock Garden (Free)"]
      },
      "hotel_reco": "Traditional Ryokan in Gion"
    },
    {
      "id": "rio_br",
      "name": "Rio de Janeiro",
      "country": "Brazil",
      "avg_daily_cost": 90,
      "best_season_score": {"spring": 8, "summer": 10, "autumn": 8, "winter": 7},
      "tags": ["beach", "nightlife", "adventure", "vibrant"],
      "coords": [70, 20],
      "activities": {
        "adventure": ["Hike Sugarloaf Mountain", "Hang gliding"],
        "beach": ["Ipanema Beach", "Copacabana Volleyball"],
        "nightlife": ["Samba in Lapa"],
        "history": ["Christ the Redeemer Statue"]
      },
      "hotel_reco": "Beachfront hotel in Copacabana"
    },
    {
      "id": "amsterdam_nl",
      "name": "Amsterdam",
      "country": "Netherlands",
      "avg_daily_cost": 120,
      "best_season_score": {"spring": 9, "summer": 9, "autumn": 7, "winter": 4},
      "tags": ["art", "history", "biking", "museums", "food"],
      "coords": [30, 80],
      "activities": {
        "art": ["Rijksmuseum", "Van Gogh Museum"],
        "history": ["Anne Frank House", "Westerkerk"],
        "biking": ["Canal Bike Tour (Free/Cheap)"],
        "nightlife": ["Brown Cafés pub crawl"]
      },
      "hotel_reco": "Canal-side Boutique Hotel"
    }
  ]
}
"""

def generate_data_docx():
    """Generates the required travel_data.docx file with the raw JSON content."""
    try:
        if not os.path.exists(DATA_FILE):
            print(f"Creating required data file: {DATA_FILE}")
            doc = Document()
            # Insert the raw JSON string into the document
            doc.add_paragraph(SAMPLE_JSON.strip())
            doc.save(DATA_FILE)
            print("Creation successful.")
        else:
            print(f"Data file {DATA_FILE} already exists.")
    except Exception as e:
        print(f"ERROR: Could not generate {DATA_FILE}. Please check 'python-docx' installation. {e}")
        exit()

if __name__ == "__main__":
    # Ensure the data file exists
    generate_data_docx()

    # Run the Streamlit UI application
    print("\nStarting Streamlit UI...")
    # Using subprocess.call to run the Streamlit command
    try:
        subprocess.call(["streamlit", "run", "travel_ui.py"])
    except FileNotFoundError:
        print("\nFATAL ERROR: 'streamlit' command not found.")
        print("Please ensure Streamlit is installed: pip install streamlit")