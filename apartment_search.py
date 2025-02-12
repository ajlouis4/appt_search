import random
import pandas as pd
import streamlit as st
from itertools import combinations
from collections import Counter

def generate_apartment(bedrooms):
    """Generate a random apartment with given constraints."""
    if bedrooms == 1:
        price_brackets = [(2000, 2200), (2300, 2600), (2800, 3000)]
        size_range = (500, 900)
    else:
        price_brackets = [(2800, 3000), (3000, 3400), (3600, 3900)]
        size_range = (700, 1100)
    
    neighborhoods = ["Lake Shore East", "River North", "Loop", "Lincoln Park", "Wicker Park", "West Loop", "Fulton Market"]
    neighborhood = random.choice(neighborhoods)
    
    price_range = random.choice(price_brackets)
    price = random.randint(*price_range)
    size = random.randint(*size_range)
    
    possible_amenities = ["Pool", "Sauna", "Fitness Center", "EV Charging", "Basketball Court", "Rooftop Lounge", "Dog Park", "Coworking Space", "Bike Storage", "Smart Home Features"]
    num_amenities = random.randint(0, len(possible_amenities))  # Allows for no amenities up to all amenities
    amenities = random.sample(possible_amenities, num_amenities)
    
    return {
        "Bedrooms": bedrooms,
        "Price": price,
        "Size": size,
        "Neighborhood": neighborhood,
        "Amenities": amenities
    }

def generate_comparisons(n_apartments=100, bedrooms=1):
    """Generate 100 apartments and select 25 random pairwise comparisons."""
    apartments = [generate_apartment(bedrooms) for _ in range(n_apartments)]
    pairs = random.sample(list(combinations(apartments, 2)), 25)
    return pairs

def analyze_preferences(user_choices):
    """Analyze user choices to determine the most important features, with price and size scoring based on preference."""
    feature_importance = Counter()
    neighborhood_counts = Counter()
    neighborhood_wins = Counter()
    total_comparisons = len(user_choices)
    
    for choice in user_choices:
        apt_a, apt_b = choice["Apartment A"], choice["Apartment B"]
        preferred = choice["Preferred"]
        
        # Price sensitivity: 1 if lower price was picked, 0 otherwise
        if (apt_a["Price"] < apt_b["Price"] and preferred == "Apartment A") or (apt_b["Price"] < apt_a["Price"] and preferred == "Apartment B"):
            feature_importance["Price Sensitivity"] += 1
        
        # Size preference: 1 if larger size was picked, 0 otherwise
        if (apt_a["Size"] > apt_b["Size"] and preferred == "Apartment A") or (apt_b["Size"] > apt_a["Size"] and preferred == "Apartment B"):
            feature_importance["Size Preference"] += 1
        
        # Neighborhood importance
        neighborhood_counts[apt_a["Neighborhood"]] += 1
        neighborhood_counts[apt_b["Neighborhood"]] += 1
        
        selected_apartment = apt_a if preferred == "Apartment A" else apt_b
        neighborhood_wins[selected_apartment["Neighborhood"]] += 1
        
        # Amenity importance
        for amenity in selected_apartment["Amenities"]:
            feature_importance[f"Amenity - {amenity}"] += 1
    
    # Calculate neighborhood score as win rate multiplied by total comparisons
    for neighborhood, wins in neighborhood_wins.items():
        if neighborhood_counts[neighborhood] > 0:
            feature_importance[f"Neighborhood - {neighborhood}"] = (wins / neighborhood_counts[neighborhood]) * total_comparisons
    
    sorted_features = feature_importance.most_common()
    return pd.DataFrame(sorted_features, columns=["Feature", "Importance"])

def streamlit_app():
    """Streamlit UI for apartment comparisons."""
    st.title("Apartment Pairwise Comparison Study")
    
    if "user_choices" not in st.session_state:
        st.session_state.user_choices = []
    
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    
    bedroom_choice = st.radio("Select Apartment Type", ["1 Bedroom", "2 Bedroom"], key="bedroom_choice")
    bedrooms = 1 if bedroom_choice == "1 Bedroom" else 2
    
    if "last_bedroom_choice" not in st.session_state or st.session_state.last_bedroom_choice != bedroom_choice:
        st.session_state.comparison_pairs = generate_comparisons(n_apartments=100, bedrooms=bedrooms)
        st.session_state.current_index = 0
        st.session_state.last_bedroom_choice = bedroom_choice
    
    if st.session_state.current_index < len(st.session_state.comparison_pairs):
        apt1, apt2 = st.session_state.comparison_pairs[st.session_state.current_index]
        st.subheader(f"Comparison {st.session_state.current_index + 1} - {bedroom_choice}")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Apartment A")
            for key, value in apt1.items():
                st.write(f"**{key}:** {', '.join(value) if isinstance(value, list) else value}")
        
        with col2:
            st.write("### Apartment B")
            for key, value in apt2.items():
                st.write(f"**{key}:** {', '.join(value) if isinstance(value, list) else value}")
        
        choice = st.radio("Select your preferred apartment", ("Apartment A", "Apartment B"), key=f"choice_{st.session_state.current_index}")
        
        if st.button("Save Response"):
            st.session_state.user_choices.append({"Comparison": st.session_state.current_index + 1, "Preferred": choice, "Apartment A": apt1, "Apartment B": apt2})
            st.session_state.current_index += 1
            st.experimental_set_query_params(index=st.session_state.current_index)
            st.rerun()
    
    if st.session_state.current_index >= len(st.session_state.comparison_pairs):
        if st.button("Analyze Preferences"):
            results_df = analyze_preferences(st.session_state.user_choices)
            st.write("### Most Important Features")
            st.dataframe(results_df)
            st.download_button("Download Feature Importance CSV", results_df.to_csv(index=False).encode("utf-8"), "Feature_Importance.csv", "text/csv")

if __name__ == "__main__":
    streamlit_app()
