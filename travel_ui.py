import streamlit as st
import os
from typing import Dict, List, Any
from travel_core import TravelAgent, load_json_from_docx, Destination

# --- UI Layout and Input Collection ---

def run_ui():
    """Main function to run the Streamlit application."""
    
    st.set_page_config(layout="wide", page_title="AI Virtual Travel Guide")
    
    # 1. Load Data
    data_path = "travel_data.docx"
    data = load_json_from_docx(data_path)

    # Error Check for Data Loading
    if "error" in data:
        st.error(f"FATAL ERROR: Could not load travel data. Please ensure {data_path} exists and contains valid JSON.\nError: {data['error']}")
        return

    # 2. Header and Avatar
    col_img, col_title = st.columns([1, 4])
    with col_img:
        # Placeholder for agent_avatar.png
        if os.path.exists("agent_avatar.png"):
            st.image("agent_avatar.png", width=120)
        else:
            st.markdown("## 🤖")
    
    with col_title:
        st.markdown("# ✈️ AI Virtual Travel Guide Agent")
        st.markdown("### Utility-Driven Planning & Search Algorithms")

    st.markdown("---")

    # 3. User Input Form
    st.sidebar.header("🎯 Define Your Travel Utilities")
    
    budget = st.sidebar.slider("1. Max Daily Budget ($USD)", 50, 250, 120, 10)
    duration = st.sidebar.slider("2. Travel Duration (Days)", 2, 7, 5)
    
    season_options = ["Spring", "Summer", "Autumn", "Winter"]
    season = st.sidebar.selectbox("3. Travel Season", season_options)
    
    interest_options = ["beach", "adventure", "mountains", "history", "nightlife", "food", "art", "gardens"]
    interests = st.sidebar.multiselect("4. Interests", interest_options, default=["history", "food", "adventure"])
    
    # Run button
    if st.sidebar.button("✨ Find Optimal Trip"):
        if not interests:
            st.sidebar.warning("Please select at least one interest.")
        else:
            user_input = {
                "budget": budget,
                "duration": duration,
                "month": season,
                "interests": interests
            }
            # Start AI Planning
            st.session_state['run_plan'] = user_input
            st.session_state['is_planning'] = True

    # 4. Main Display Logic
    
    if 'run_plan' in st.session_state and st.session_state['is_planning']:
        
        # Initialize Agent
        agent = TravelAgent(data)
        user_input = st.session_state['run_plan']
        
        with st.spinner('AI Agent is calculating optimal routes and utility scores...'):
            try:
                # RUN ALL CORE LOGIC
                ranked_destinations, best_dest, itinerary = agent.run_planning(user_input)
                
                st.session_state['ranked'] = ranked_destinations
                st.session_state['best'] = best_dest
                st.session_state['itinerary'] = itinerary
                st.session_state['is_planning'] = False
            
            except Exception as e:
                st.error(f"An error occurred during planning: {e}")
                st.session_state['is_planning'] = False


    if 'best' in st.session_state and st.session_state['best']:
        best_dest = st.session_state['best']
        ranked_destinations = st.session_state['ranked']
        itinerary = st.session_state['itinerary']

        st.header(f"The Agent Recommends: {best_dest.name}, {best_dest.country}")
        st.markdown(f"**Optimal Destination Chosen based on {best_dest.utility_score:.4f} Utility Score.**")
        st.markdown("---")

        # Utility Breakdown and Top 3
        col_itinerary, col_ranking = st.columns([2, 1])

        with col_ranking:
            st.subheader("📊 Utility Ranking (Top 3)")
            for i, dest in enumerate(ranked_destinations[:3]):
                st.info(f"**{i+1}. {dest.name}**\n*Score: {dest.utility_score:.4f}*")
        
        with col_itinerary:
            st.subheader("🗺️ Rule-Based Itinerary")
            st.markdown(f"**Hotel Suggestion:** {best_dest.hotel_reco}")
            st.markdown("---")

            for day_num, activities in enumerate(itinerary):
                st.markdown(f"**DAY {day_num + 1}**")
                for activity in activities:
                    if "RULE:" in activity:
                        st.success(f"⭐ {activity}", icon="✅")
                    else:
                        st.markdown(f"- {activity}")
                st.markdown("---")


if __name__ == "__main__":
    run_ui()