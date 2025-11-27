import json
import math
import heapq
import random
from docx import Document
from typing import List, Dict, Any, Tuple, Set

# Constants
PAK_CITIES_COORDS = {
    "Karachi": (65, 55), "Lahore": (68, 60), "Islamabad": (68, 62),
    "Rawalpindi": (68, 62), "Faisalabad": (67, 59), "Multan": (66, 58),
    "Peshawar": (67, 63), "Quetta": (64, 58), "Sialkot": (69, 61),
    "Hyderabad": (65, 56), "Gujranwala": (68, 61), "Rahim Yar Khan": (66, 57),
    "Bahawalpur": (67, 57), "Sargodha": (67, 60), "Abbottabad": (69, 63),
    "Sukkur": (66, 56), "Larkana": (65, 57), "Sheikhupura": (68, 60),
    "Jhelum": (69, 62), "Gwadar": (62, 55)
}

DISTANCE_SCALING = 0.005 

# --- Data Handling ---
def load_json_from_docx(filepath: str) -> Dict[str, Any]:
    try:
        doc = Document(filepath)
        raw_text = "".join([para.text for para in doc.paragraphs]).strip()
        return json.loads(raw_text)
    except FileNotFoundError:
        return {"error": f"Data file not found at: {filepath}"}
    except Exception as e:
        return {"error": f"Failed to read/parse JSON from docx: {e}"}

# --- Object Model ---
class Destination:
    """Represents a single destination."""
    def __init__(self, data: Dict[str, Any]):
        self.id = data["id"]
        self.name = data["name"]
        self.country = data["country"]
        self.cost = data["avg_daily_cost"]
        self.tags = set(data["tags"])
        self.coords = tuple(data["coords"])
        self.activities = data["activities"]
        self.hotel_reco = data["hotel_reco"]
        
        # Local transport only, preferred mode logic removed
        self.local_transport = data.get("local_transport", [])
        
        self.utility_score = 0.0
        self.estimated_flight_cost = 0

# --- Search Algorithms ---
class SearchAlgorithms:

    @staticmethod
    def bfs_budget_filter(all_destinations: List[Destination], max_cost: float) -> List[Destination]:
        """[BFS] Finds all destinations within the user's daily budget."""
        queue = all_destinations[:]
        filtered_destinations = []
        while queue:
            dest = queue.pop(0) 
            if dest.cost <= max_cost:
                filtered_destinations.append(dest)
        return filtered_destinations

    @staticmethod
    def dfs_activity_explorer(activities_list: List[str], max_depth: int) -> List[str]:
        """[DFS] Explores activity combinations."""
        def dfs(current_path: List[str]):
            if len(current_path) >= max_depth:
                return current_path

            shuffled = list(activities_list)
            random.shuffle(shuffled) 
            
            for activity in shuffled:
                if activity not in current_path:
                    new_path = current_path + [activity]
                    result = dfs(new_path)
                    if result:
                        return result
            return None

        result = dfs([])
        if result is None:
            result = []
        while len(result) < max_depth:
             result.append(random.choice(activities_list) if activities_list else "Relaxing Walk")
        return result

    @staticmethod
    def calculate_distance(start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> float:
        """Calculates Euclidean distance."""
        x1, y1 = start_coords
        x2, y2 = end_coords
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# --- AI Engines ---

class TravelAgent:
    """Manages utility scoring and flight cost calculation."""
    def __init__(self, data: Dict[str, Any]):
        self.all_destinations: List[Destination] = []
        if 'destinations' in data:
            self.all_destinations = [Destination(d) for d in data['destinations']]

    def estimate_flight_costs(self, origin_city: str):
        """Calculates flight cost from Origin (Pakistan) to Destination."""
        origin_coords = PAK_CITIES_COORDS.get(origin_city, (65, 55)) 
        
        for dest in self.all_destinations:
            distance = SearchAlgorithms.calculate_distance(origin_coords, dest.coords)
            # Flight cost formula: Base $300 + ($8 * distance units)
            cost = 300 + (distance * 8)
            dest.estimated_flight_cost = int(cost)

    def calculate_utility_scores(self, filtered_destinations: List[Destination], user_input: Dict[str, Any]):
        """Calculates weighted score (Preferred Mode logic REMOVED)."""
        user_interests = set(user_input["interests"])
        max_daily_cost = user_input["budget"]
        
        origin_city = user_input.get("origin_city", "Karachi")
        origin_coords = PAK_CITIES_COORDS.get(origin_city, (65, 55))

        for dest in filtered_destinations:
            # 1. Budget Fit
            budget_fit = dest.cost / max_daily_cost if dest.cost <= max_daily_cost else 0.1
            budget_fit = min(budget_fit, 1.0)

            # 2. Interest Match
            common_interests = dest.tags.intersection(user_interests)
            interest_match = len(common_interests) / len(user_interests) if user_interests else 0.5

            # 3. Distance Score
            distance = SearchAlgorithms.calculate_distance(origin_coords, dest.coords)
            distance_score = max(0.1, 1.0 - (distance * DISTANCE_SCALING))

            # Updated Formula: Interest 55% + Budget 40% + Distance 5%
            dest.utility_score = (
                (interest_match * 0.55) +
                (budget_fit * 0.40) +
                (distance_score * 0.05)
            )
        
        filtered_destinations.sort(key=lambda d: d.utility_score, reverse=True)
        return filtered_destinations

    def run_planning(self, user_input: Dict[str, Any]) -> Tuple[List[Destination], Destination, List[List[str]]]:
        
        # 0. Pre-calc flight costs
        self.estimate_flight_costs(user_input.get("origin_city", "Karachi"))

        # 1. BFS: Filter by Budget
        affordable_destinations = SearchAlgorithms.bfs_budget_filter(self.all_destinations, user_input["budget"])
        
        # 2. Utility Scoring
        ranked_destinations = self.calculate_utility_scores(affordable_destinations, user_input)
        
        if not ranked_destinations:
            return [], None, []

        best_dest = ranked_destinations[0]
        
        # 3. Rule-Based Planning
        planner = ItineraryPlanner()
        itinerary = planner.generate_itinerary(best_dest, user_input)

        return ranked_destinations, best_dest, itinerary

class ItineraryPlanner:
    
    def generate_itinerary(self, dest: Destination, user_input: Dict[str, Any]):
        itinerary = []
        user_interests = user_input["interests"]
        duration = int(user_input["duration"])
        
        airline_pref = user_input.get("airline_pref", "Cheap")
        inside_city_pref = user_input.get("inside_city", "taxi")
        origin_city = user_input.get("origin_city", "Pakistan")

        all_activities = []
        for interest in user_interests:
            all_activities.extend(dest.activities.get(interest, []))
        if not all_activities:
            all_activities.extend(dest.activities.get("culture", []))

        num_activities_needed = duration * 2
        selected_activities = SearchAlgorithms.dfs_activity_explorer(all_activities, num_activities_needed)
        
        activity_index = 0
        for day in range(1, duration + 1):
            daily_plan = []
            
            # RULE: Flight info on Day 1 (Assumed Flight for international travel)
            if day == 1:
                daily_plan.append(f"FLIGHT: Depart from {origin_city} -> Arrive in {dest.name}.")
                if airline_pref == "Comfortable":
                    daily_plan.append(f"TIP: Book premium economy for the flight (~${dest.estimated_flight_cost * 1.5}).")
                else:
                    daily_plan.append(f"TIP: Look for budget flight deals (~${dest.estimated_flight_cost}).")

            # RULE: Local Transport
            if inside_city_pref == "rental car":
                daily_plan.append("TRANSPORT: Pick up Rental Car.")
            elif inside_city_pref == "metro":
                 daily_plan.append("TRANSPORT: Buy a Day Pass for Metro.")
            elif inside_city_pref == "walk":
                 daily_plan.append("TRANSPORT: Wear comfortable shoes for walking.")
            else:
                 daily_plan.append("TRANSPORT: Use Taxi/Uber.")

            if activity_index < len(selected_activities):
                daily_plan.append(f"Morning: {selected_activities[activity_index]}")
                activity_index += 1
            if activity_index < len(selected_activities):
                daily_plan.append(f"Afternoon: {selected_activities[activity_index]}")
                activity_index += 1
            
            if 'nightlife' in user_interests:
                daily_plan.append("Evening: Explore local nightlife.")
            else:
                 daily_plan.append("Evening: Relaxing dinner at hotel.")
            
            itinerary.append(daily_plan)
        
        return itinerary