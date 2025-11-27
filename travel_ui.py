import streamlit as st
import os
from typing import Dict, List, Any
from travel_core import TravelAgent, load_json_from_docx, Destination


def run_ui():
    """Main function to run the Streamlit application."""

    st.set_page_config(layout="wide", page_title="AI Virtual Travel Guide")

    # --- FIXED CSS ---
    # I removed 'header {visibility: hidden;}' and '#MainMenu {visibility: hidden;}'
    # so the Sidebar Toggle arrow stays visible.
    hide_st_style = """
    <style>
    /* Hides the "Made with Streamlit" footer */
    footer {visibility: hidden;}
    /* Hides the deployment status/manage app button in the bottom corner */
    .stDeployButton {visibility: hidden;} 
    .stStatusWidget {visibility: hidden;}
    </style>
    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    # 1. Load Data
    data_path = "travel_data.docx"
    data = load_json_from_docx(data_path)

    if "error" in data:
        st.error(f"FATAL ERROR: {data['error']}")
        return

    # 2. Header
    col_img, col_title = st.columns([1, 4])
    with col_img:
        st.markdown("## 🤖")
    with col_title:
        st.markdown("# ✈️ AI Virtual Travel Guide Agent")
        st.markdown("### From Pakistan to the World 🌍")

    st.markdown("---")

    # 3. User Input Form
    st.sidebar.header("🎯 Trip Settings")

    # Origin City Input (20 Cities from Pakistan)
    pak_cities = [
        "Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad", 
        "Multan", "Peshawar", "Quetta", "Sialkot", "Hyderabad", 
        "Gujranwala", "Rahim Yar Khan", "Bahawalpur", "Sargodha", 
        "Abbottabad", "Sukkur", "Larkana", "Sheikhupura", "Jhelum", "Gwadar"
    ]
    origin_city = st.sidebar.selectbox("1. Traveling From (Pakistan)", pak_cities)

    # Budget Input (Max 3000)
    budget = st.sidebar.number_input(
        "2. Max Daily Budget ($USD)", 
        min_value=50, 
        max_value=3000, 
        value=150, 
        step=10,
        help="Enter your daily spending limit (Up to $3000)"
    )

    duration = st.sidebar.number_input("3. Travel Duration (Days)", min_value=1, value=5)
    
    interest_options = ["beach", "adventure", "mountains", "history", "nightlife", "food", "art", "gardens"]
    interests = st.sidebar.multiselect("4. Interests", interest_options, default=["history", "food"])

    st.sidebar.markdown("---")
    
    st.sidebar.header("🚆 Transport Prefs")
    inside_city = st.sidebar.selectbox("Inside City", ["metro", "taxi", "rental car", "walk"])
    airline_pref = st.sidebar.radio("Class", ["Cheap", "Comfortable"])

    # Run button
    if st.sidebar.button("✨ Find Optimal Trip"):
        if not interests:
            st.sidebar.warning("Please select at least one interest.")
        else:
            user_input = {
                "origin_city": origin_city,
                "budget": budget,
                "duration": duration,
                "interests": interests,
                "inside_city": inside_city,
                "airline_pref": airline_pref
            }

            st.session_state['run_plan'] = user_input
            st.session_state['is_planning'] = True

    # 4. Main Display Logic
    if 'run_plan' in st.session_state and st.session_state.get('is_planning'):

        agent = TravelAgent(data)
        user_input = st.session_state['run_plan']

        with st.spinner(f'Calculating flights from {user_input["origin_city"]} and planning itinerary...'):
            try:
                ranked_destinations, best_dest, itinerary = agent.run_planning(user_input)
                
                if not ranked_destinations:
                    st.error("No destinations found matching your Budget criteria.")
                    st.session_state['best'] = None
                else:
                    st.session_state['ranked'] = ranked_destinations
                    st.session_state['best'] = best_dest
                    st.session_state['itinerary'] = itinerary
                    st.session_state['is_planning'] = False

            except Exception as e:
                st.error(f"An error occurred during planning: {e}")
                st.session_state['is_planning'] = False

    # 5. Display Results
    if 'best' in st.session_state and st.session_state['best']:

        best_dest = st.session_state['best']
        ranked_destinations = st.session_state['ranked']
        itinerary = st.session_state['itinerary']
        origin = st.session_state['run_plan']['origin_city']

        st.header(f"Trip Recommendation: {origin} ✈️ {best_dest.name}, {best_dest.country}")
        st.markdown(f"**Utility Score: {best_dest.utility_score:.4f}**")
        
        # Metrics Display including FLIGHT COST
        col_metrics1, col_metrics2, col_metrics3 = st.columns(3)
        with col_metrics1:
             st.metric("Avg Daily Cost", f"${best_dest.cost}/day")
        with col_metrics2:
             st.metric("Est. Flight Cost", f"${best_dest.estimated_flight_cost}")
        with col_metrics3:
             st.metric("Transport", best_dest.local_transport[0].title() if best_dest.local_transport else "N/A")

        st.markdown("---")

        col_itinerary, col_ranking = st.columns([2, 1])

        # Ranking Section
        with col_ranking:
            st.subheader("📊 Top Alternatives")
            for i, dest in enumerate(ranked_destinations[:3]):
                st.info(f"**{i+1}. {dest.name}**\n*Flight: ${dest.estimated_flight_cost}*")

        # Itinerary Section
        with col_itinerary:
            st.subheader("🗺️ Itinerary")
            st.markdown(f"**Hotel Suggestion:** {best_dest.hotel_reco}")
            st.markdown("---")

            for day_num, activities in enumerate(itinerary):
                st.markdown(f"**DAY {day_num + 1}**")
                for activity in activities:
                    if "FLIGHT:" in activity:
                        st.info(f"✈️ {activity}")
                    elif "TIP:" in activity or "TRANSPORT:" in activity:
                        st.success(f"🤖 {activity}")
                    else:
                        st.markdown(f"- {activity}")
                st.markdown("---")


if __name__ == "__main__":
    run_ui()