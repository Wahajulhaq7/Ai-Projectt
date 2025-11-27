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
      "tags": ["culture", "history", "gardens", "food", "art"],
      "coords": [85, 50],
      "activities": {
        "history": ["Fushimi Inari-taisha Shrine", "Nijo Castle"],
        "culture": ["Traditional Tea Ceremony", "Gion District Stroll"],
        "food": ["Nishiki Market Exploration"],
        "gardens": ["Kinkaku-ji (Golden Pavilion)"]
      },
      "hotel_reco": "Traditional Ryokan in Gion",
      "local_transport": ["metro", "bus", "taxi"]
    },
    {
      "id": "rio_br",
      "name": "Rio de Janeiro",
      "country": "Brazil",
      "avg_daily_cost": 90,
      "tags": ["beach", "nightlife", "adventure", "vibrant"],
      "coords": [30, 20],
      "activities": {
        "adventure": ["Hike Sugarloaf Mountain", "Hang gliding"],
        "beach": ["Ipanema Beach", "Copacabana Volleyball"],
        "nightlife": ["Samba in Lapa"],
        "history": ["Christ the Redeemer Statue"]
      },
      "hotel_reco": "Beachfront hotel in Copacabana",
      "local_transport": ["taxi", "metro"]
    },
    {
      "id": "amsterdam_nl",
      "name": "Amsterdam",
      "country": "Netherlands",
      "avg_daily_cost": 140,
      "tags": ["art", "history", "biking", "museums", "food"],
      "coords": [48, 85],
      "activities": {
        "art": ["Rijksmuseum", "Van Gogh Museum"],
        "history": ["Anne Frank House"],
        "biking": ["Canal Bike Tour"],
        "nightlife": ["Brown Cafés pub crawl"]
      },
      "hotel_reco": "Canal-side Boutique Hotel",
      "local_transport": ["rental_bike", "tram", "metro"]
    },
    {
      "id": "paris_fr",
      "name": "Paris",
      "country": "France",
      "avg_daily_cost": 180,
      "tags": ["art", "history", "food", "romance", "fashion"],
      "coords": [45, 80],
      "activities": {
        "art": ["The Louvre Museum", "Musée d'Orsay"],
        "history": ["Eiffel Tower Summit"],
        "food": ["Seine Dinner Cruise"],
        "gardens": ["Tuileries Garden Picnic"]
      },
      "hotel_reco": "Chic Hotel in Le Marais",
      "local_transport": ["metro", "taxi", "walk"]
    },
    {
      "id": "cairo_eg",
      "name": "Cairo",
      "country": "Egypt",
      "avg_daily_cost": 50,
      "tags": ["history", "culture", "desert", "adventure"],
      "coords": [55, 60],
      "activities": {
        "history": ["Pyramids of Giza", "The Sphinx"],
        "culture": ["Khan el-Khalili Market"],
        "adventure": ["Camel Ride at Sunset"],
        "food": ["Traditional Koshary Lunch"]
      },
      "hotel_reco": "Hotel with Pyramid View",
      "local_transport": ["taxi", "uber"]
    },
    {
      "id": "nyc_usa",
      "name": "New York City",
      "country": "USA",
      "avg_daily_cost": 220,
      "tags": ["nightlife", "food", "art", "urban", "history"],
      "coords": [20, 70],
      "activities": {
        "art": ["MoMA", "The Met"],
        "nightlife": ["Broadway Show"],
        "food": ["Chelsea Market", "Pizza Tour"],
        "gardens": ["Central Park Walk"]
      },
      "hotel_reco": "Modern Hotel in Midtown",
      "local_transport": ["metro", "taxi"]
    },
    {
      "id": "reykjavik_is",
      "name": "Reykjavik",
      "country": "Iceland",
      "avg_daily_cost": 190,
      "tags": ["nature", "adventure", "mountains", "wellness"],
      "coords": [40, 95],
      "activities": {
        "wellness": ["Blue Lagoon Thermal Bath"],
        "adventure": ["Golden Circle Tour"],
        "mountains": ["Volcano Tour"],
        "nightlife": ["Northern Lights Hunt"]
      },
      "hotel_reco": "Eco-Lodge outside City",
      "local_transport": ["rental_car", "bus"]
    },
    {
      "id": "dubai_ae",
      "name": "Dubai",
      "country": "UAE",
      "avg_daily_cost": 210,
      "tags": ["luxury", "shopping", "adventure", "modern"],
      "coords": [65, 55],
      "activities": {
        "adventure": ["Desert Safari 4x4"],
        "shopping": ["Dubai Mall", "Gold Souk"],
        "culture": ["Burj Khalifa View"],
        "beach": ["JBR Beach"]
      },
      "hotel_reco": "5-Star Resort on the Palm",
      "local_transport": ["taxi", "metro", "rental_car"]
    },
    {
      "id": "kathmandu_np",
      "name": "Kathmandu",
      "country": "Nepal",
      "avg_daily_cost": 45,
      "tags": ["mountains", "adventure", "culture", "history", "budget"],
      "coords": [75, 55],
      "activities": {
        "mountains": ["Everest Mountain Flight", "Nagarkot Sunrise"],
        "culture": ["Boudhanath Stupa"],
        "history": ["Durbar Square"],
        "adventure": ["Thamel Street Walking"]
      },
      "hotel_reco": "Heritage Guesthouse in Thamel",
      "local_transport": ["taxi", "rickshaw"]
    },
    {
      "id": "istanbul_tr",
      "name": "Istanbul",
      "country": "Turkey",
      "avg_daily_cost": 75,
      "tags": ["history", "culture", "food", "shopping"],
      "coords": [60, 70],
      "activities": {
        "history": ["Hagia Sophia", "Blue Mosque"],
        "culture": ["Bosphorus Ferry Cruise"],
        "food": ["Spice Market", "Turkish Delight Tasting"],
        "nightlife": ["Taksim Square"]
      },
      "hotel_reco": "Boutique Hotel in Sultanahmet",
      "local_transport": ["tram", "taxi", "ferry"]
    },
    {
      "id": "rome_it",
      "name": "Rome",
      "country": "Italy",
      "avg_daily_cost": 130,
      "tags": ["history", "food", "art", "culture"],
      "coords": [50, 75],
      "activities": {
        "history": ["Colosseum & Roman Forum", "Pantheon"],
        "art": ["Vatican Museums", "Sistine Chapel"],
        "food": ["Trastevere Food Tour", "Gelato Tasting"],
        "culture": ["Trevi Fountain Coin Toss"]
      },
      "hotel_reco": "Historic Villa near Pantheon",
      "local_transport": ["metro", "taxi", "walk"]
    },
    {
      "id": "bangkok_th",
      "name": "Bangkok",
      "country": "Thailand",
      "avg_daily_cost": 60,
      "tags": ["food", "nightlife", "culture", "markets"],
      "coords": [80, 45],
      "activities": {
        "culture": ["Grand Palace", "Wat Arun (Temple of Dawn)"],
        "food": ["Chinatown Street Food", "Floating Market Tour"],
        "nightlife": ["Khao San Road", "Rooftop Bar at Vertigo"],
        "history": ["Jim Thompson House"]
      },
      "hotel_reco": "Riverside Luxury Resort",
      "local_transport": ["taxi", "tuk-tuk", "bts skytrain"]
    },
    {
      "id": "bali_id",
      "name": "Bali",
      "country": "Indonesia",
      "avg_daily_cost": 70,
      "tags": ["beach", "nature", "wellness", "adventure"],
      "coords": [85, 10],
      "activities": {
        "beach": ["Uluwatu Surf/View", "Seminyak Beach Club"],
        "adventure": ["Monkey Forest Ubud", "Rice Terrace Trek"],
        "wellness": ["Yoga Retreat", "Balinese Massage"],
        "culture": ["Tanah Lot Temple"]
      },
      "hotel_reco": "Private Villa in Ubud",
      "local_transport": ["scooter rental", "taxi"]
    },
    {
      "id": "cape_town_za",
      "name": "Cape Town",
      "country": "South Africa",
      "avg_daily_cost": 90,
      "tags": ["adventure", "nature", "history", "wine", "beach"],
      "coords": [50, 10],
      "activities": {
        "adventure": ["Table Mountain Hike", "Cage Diving with Sharks"],
        "history": ["Robben Island Tour"],
        "gardens": ["Kirstenbosch Botanical Gardens"],
        "beach": ["Boulders Beach (Penguins)"]
      },
      "hotel_reco": "Waterfront Harbour Hotel",
      "local_transport": ["rental_car", "uber"]
    },
    {
      "id": "cusco_pe",
      "name": "Cusco",
      "country": "Peru",
      "avg_daily_cost": 80,
      "tags": ["history", "adventure", "mountains", "culture"],
      "coords": [25, 25],
      "activities": {
        "history": ["Machu Picchu Day Trip", "Sacsayhuaman Fortress"],
        "adventure": ["Inca Trail Hike", "Rainbow Mountain"],
        "culture": ["San Pedro Market"],
        "mountains": ["Andes Views"]
      },
      "hotel_reco": "Colonial Hotel near Plaza de Armas",
      "local_transport": ["taxi", "walk"]
    },
    {
      "id": "sydney_au",
      "name": "Sydney",
      "country": "Australia",
      "avg_daily_cost": 160,
      "tags": ["beach", "urban", "adventure", "food"],
      "coords": [95, 15],
      "activities": {
        "beach": ["Bondi to Coogee Walk", "Manly Ferry Trip"],
        "adventure": ["Sydney Harbour Bridge Climb"],
        "culture": ["Sydney Opera House Tour"],
        "food": ["Seafood at Fish Market"]
      },
      "hotel_reco": "Hotel with Harbour View",
      "local_transport": ["ferry", "train", "bus"]
    },
    {
      "id": "santorini_gr",
      "name": "Santorini",
      "country": "Greece",
      "avg_daily_cost": 170,
      "tags": ["beach", "romance", "views", "food"],
      "coords": [58, 68],
      "activities": {
        "beach": ["Red Beach", "Sunset Sailing Catamaran"],
        "food": ["Wine Tasting Tour", "Greek Taverna Dinner"],
        "adventure": ["Hike Fira to Oia"],
        "history": ["Akrotiri Archaeological Site"]
      },
      "hotel_reco": "Cave Hotel in Oia",
      "local_transport": ["atv rental", "bus", "taxi"]
    },
    {
      "id": "prague_cz",
      "name": "Prague",
      "country": "Czech Republic",
      "avg_daily_cost": 85,
      "tags": ["history", "nightlife", "beer", "culture"],
      "coords": [50, 82],
      "activities": {
        "history": ["Charles Bridge", "Prague Castle"],
        "nightlife": ["Old Town Square", "Beer Spa Experience"],
        "culture": ["Astronomical Clock"],
        "food": ["Trdelník Pastry Tasting"]
      },
      "hotel_reco": "Gothic Style Old Town Hotel",
      "local_transport": ["tram", "metro", "walk"]
    },
    {
      "id": "barcelona_es",
      "name": "Barcelona",
      "country": "Spain",
      "avg_daily_cost": 125,
      "tags": ["art", "beach", "nightlife", "food", "architecture"],
      "coords": [42, 75],
      "activities": {
        "art": ["Sagrada Familia", "Park Güell"],
        "beach": ["Barceloneta Beach"],
        "food": ["La Boqueria Market", "Tapas Crawl"],
        "nightlife": ["Gothic Quarter Bars"]
      },
      "hotel_reco": "Design Hotel in Eixample",
      "local_transport": ["metro", "taxi", "bike"]
    },
    {
      "id": "queenstown_nz",
      "name": "Queenstown",
      "country": "New Zealand",
      "avg_daily_cost": 155,
      "tags": ["adventure", "mountains", "nature", "nightlife"],
      "coords": [98, 10],
      "activities": {
        "adventure": ["Bungee Jumping", "Shotover Jet Boat"],
        "mountains": ["Skyline Gondola & Luge", "Milford Sound Day Trip"],
        "nature": ["Lake Wakatipu Cruise"],
        "food": ["Fergburger"]
      },
      "hotel_reco": "Lakeside Lodge",
      "local_transport": ["rental_car", "shuttle"]
    }
  ]
}
"""

def generate_data_docx():
    """Generates the required travel_data.docx file with the raw JSON content."""
    try:
        if os.path.exists(DATA_FILE):
             print(f"File {DATA_FILE} exists. Overwriting with new data...")
        else:
             print(f"Creating required data file: {DATA_FILE}")
        
        doc = Document()
        doc.add_paragraph(SAMPLE_JSON.strip())
        doc.save(DATA_FILE)
        print("Data Generation successful.")

    except Exception as e:
        print(f"ERROR: Could not generate {DATA_FILE}. Please check 'python-docx' installation. {e}")
        exit()

if __name__ == "__main__":
    generate_data_docx()
    print("\nStarting Streamlit UI...")
    try:
        subprocess.call(["streamlit", "run", "travel_ui.py"])
    except FileNotFoundError:
        print("\nFATAL ERROR: 'streamlit' command not found.")
        print("Please ensure Streamlit is installed: pip install streamlit")