import json
import math
import heapq
import random
from docx import Document
from typing import List, Dict, Any, Tuple, Set

# Constants
START_COORDS = (50, 50) 
DISTANCE_SCALING = 0.005 # Used to normalize distance score

# --- Data Handling ---
def load_json_from_docx(filepath: str) -> Dict[str, Any]:
    """Reads raw JSON text from a docx file and parses it."""
    try:
        doc = Document(filepath)
        raw_text = "".join([para.text for para in doc.paragraphs]).strip()
        # The JSON is expected to be the entirety of the text content
        return json.loads(raw_text)
    except FileNotFoundError:
        return {"error": f"Data file not found at: {filepath}"}
    except Exception as e:
        return {"error": f"Failed to read/parse JSON from docx: {e}"}

# --- Object Model ---
class Destination:
    """Represents a single destination with utility and planning data."""
    def __init__(self, data: Dict[str, Any]):
        self.id = data["id"]
        self.name = data["name"]
        self.country = data["country"]
        self.cost = data["avg_daily_cost"]
        self.season_scores = data["best_season_score"]
        self.tags = set(data["tags"])
        self.coords = tuple(data["coords"])
        self.activities = data["activities"]
        self.hotel_reco = data["hotel_reco"]
        self.utility_score = 0.0

# --- Search Algorithms ---
class SearchAlgorithms:
    """Implements graph traversal methods."""

    @staticmethod
    def bfs_budget_filter(all_destinations: List[Destination], max_cost: float) -> List[Destination]:
        """
        [BFS: Breadth-First Search] Finds all destinations within the user's budget.
        The search is shallow, exploring only the 'cost' attribute level.
        """
        queue = all_destinations[:]
        filtered_destinations = []
        while queue:
            dest = queue.pop(0)  # FIFO queue for BFS
            if dest.cost <= max_cost:
                filtered_destinations.append(dest)
        return filtered_destinations

    @staticmethod
    def dfs_activity_explorer(activities_list: List[str], max_depth: int) -> List[str]:
        """
        [DFS: Depth-First Search] Explores possible unique activity combinations 
        up to max_depth (number of required activities).
        Uses recursion to simulate the stack-based DFS traversal.
        """
        def dfs(current_path: List[str]):
            if len(current_path) >= max_depth:
                return current_path

            # Randomize order to simulate exploring different branches
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
        # Pad with random activities if DFS couldn't find enough unique ones
        if result and len(result) < max_depth:
            while len(result) < max_depth:
                 result.append(random.choice(activities_list))
        
        return result if result else activities_list[:max_depth]


    @staticmethod
    def a_star_route_finder(start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> float:
        """
        [A*: A-Star Search] Calculates the Euclidean distance as the heuristic 
        for the "best" (shortest) path cost between two simulated locations.
        """
        x1, y1 = start_coords
        x2, y2 = end_coords
        # The cost is the distance itself (h(n))
        return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# --- AI Engines ---

class TravelAgent:
    """Manages utility scoring and orchestrates the planning process."""
    def __init__(self, data: Dict[str, Any]):
        self.all_destinations: List[Destination] = []
        if 'destinations' in data:
            self.all_destinations = [Destination(d) for d in data['destinations']]

    def calculate_utility_scores(self, filtered_destinations: List[Destination], user_input: Dict[str, Any]):
        """
        [Utility-Based Decision Making] Calculates the final weighted score for each destination.
        """
        user_interests = set(user_input["interests"])
        user_month = user_input["month"].lower()
        max_daily_cost = user_input["budget"]

        for dest in filtered_destinations:
            # 1. Budget Fit (0.0 to 1.0)
            budget_fit = dest.cost / max_daily_cost if dest.cost <= max_daily_cost else 0.1
            budget_fit = min(budget_fit, 1.0)

            # 2. Season Suitability (0.0 to 1.0)
            # Use max score if the user input is a generic season (e.g., 'summer')
            score_key = next((k for k in dest.season_scores if user_month in k.lower()), user_month)
            season_score = dest.season_scores.get(score_key, 5) / 10.0

            # 3. Interest Match (0.0 to 1.0)
            common_interests = dest.tags.intersection(user_interests)
            interest_match = len(common_interests) / len(user_interests) if user_interests else 0.5

            # 4. Distance Score (0.0 to 1.0)
            # Use A* heuristic (distance) to find the cost
            distance = SearchAlgorithms.a_star_route_finder(START_COORDS, dest.coords)
            distance_score = max(0.1, 1.0 - (distance * DISTANCE_SCALING))

            # Utility Formula Application
            dest.utility_score = (
                (interest_match * 0.4) +
                (budget_fit * 0.3) +
                (season_score * 0.2) +
                (distance_score * 0.1)
            )
        
        filtered_destinations.sort(key=lambda d: d.utility_score, reverse=True)
        return filtered_destinations

    def run_planning(self, user_input: Dict[str, Any]) -> Tuple[List[Destination], Destination, List[List[str]]]:
        """Orchestrates the entire planning pipeline."""
        
        # 1. BFS: Filter by Budget
        affordable_destinations = SearchAlgorithms.bfs_budget_filter(self.all_destinations, user_input["budget"])
        if not affordable_destinations:
            return [], None, []

        # 2. Utility Scoring: Rank Destinations
        ranked_destinations = self.calculate_utility_scores(affordable_destinations, user_input)
        
        best_dest = ranked_destinations[0]
        
        # 3. Rule-Based Planning & DFS
        planner = ItineraryPlanner()
        itinerary = planner.generate_itinerary(best_dest, user_input)

        return ranked_destinations, best_dest, itinerary

class ItineraryPlanner:
    """Handles Rule-Based Planning and Activity Generation."""
    
    def generate_itinerary(self, dest: Destination, user_input: Dict[str, Any]):
        """
        [Rule-Based Planning] Generates a full itinerary based on user input and destination data.
        """
        itinerary = []
        user_interests = user_input["interests"]
        duration = user_input["duration"]
        
        # Prepare activities using DFS (Activity Combination Explorer)
        all_activities = []
        for interest in user_interests:
            all_activities.extend(dest.activities.get(interest, []))
        
        # Fallback if no specific activities match
        if not all_activities:
            all_activities.extend(dest.activities.get("culture", []))
            all_activities.extend(dest.activities.get("history", []))

        # Use DFS to select the required number of unique activities
        num_activities_needed = duration * 2
        selected_activities = SearchAlgorithms.dfs_activity_explorer(all_activities, num_activities_needed)
        
        activity_index = 0
        for day in range(1, duration + 1):
            daily_plan = []
            
            # RULE 1: Budget Constraint Rule
            if user_input["budget"] <= 120:
                # Add a rule-based cheap activity if budget is low
                daily_plan.append("RULE: Find a FREE city park or viewing point.")

            # RULE 2: Interest-Specific Day Rule (Beach)
            if 'beach' in user_interests and day == 1:
                daily_plan.append("RULE: Full Beach Day (Relaxation/Water Sports)")

            # RULE 3: Season Rule (Winter)
            if 'winter' in user_input['month'].lower():
                 daily_plan.append("RULE: Indoor Activity Focus (e.g., museums, galleries).")
            
            # RULE 4 & 5: Activity Assignment
            if activity_index < len(selected_activities):
                daily_plan.append(f"Morning: {selected_activities[activity_index]}")
                activity_index += 1
            
            if activity_index < len(selected_activities):
                daily_plan.append(f"Afternoon: {selected_activities[activity_index]}")
                activity_index += 1
            
            # RULE 6: Nightlife Rule
            if 'nightlife' in user_interests:
                daily_plan.append("Evening: Explore local nightlife or bars.")
            else:
                 daily_plan.append("Evening: Quiet dinner and early rest.")
            
            itinerary.append(daily_plan)
        
        return itinerary