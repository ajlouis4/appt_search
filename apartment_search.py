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
    neighborhood = random.choices(neighborhoods, weights=[1, 1, 1, 1, 1, 1, 1])[0]  # West Loop & Fulton Market more likely
    
    if neighborhood in ["West Loop", "Fulton Market"]:
        price_range = random.choice(price_brackets[1:])  # More expensive options
    else:
        price_range = random.choice(price_brackets)
    
    price = random.randint(*price_range)
    size = random.randint(*size_range)
    
    amenities_pool = random.random() < 0.3  # 30% chance for a pool if allowed
    
    amenities = set()
    if price_range == price_brackets[0]:  # Low price tier
        amenities.add("Fitness Center")
        if amenities_pool:
            amenities.add("Pool")
    else:
        possible_amenities = ["Pool", "Sauna", "Fitness Center", "EV Charging", "Basketball Court"]
        if price_range in price_brackets[1:]:  # Mid and High price tiers
            amenities.update(random.sample(possible_amenities, k=random.randint(1, 5)))
        # Ensure EV Charging, Sauna, and Basketball Court only appear in mid or high price tiers
        if "EV Charging" in amenities or "Sauna" in amenities or "Basketball Court" in amenities:
            if price_range == price_brackets[0]:
                amenities.discard("EV Charging")
                amenities.discard("Sauna")
                amenities.discard("Basketball Court")
    
    return {
        "Bedrooms": bedrooms,
        "Price": price,
        "Size": size,
        "Neighborhood": neighborhood,
        "Amenities": list(amenities)
    }

def generate_comparisons(n_apartments=10, bedrooms=1):
    """Generate random pairwise comparisons within the selected bedroom group, limited to 25 comparisons."""
    apartments = [generate_apartment(bedrooms) for _ in range(n_apartments)]
    pairs = list(combinations(apartments, 2))
    random.shuffle(pairs)
    return pairs[:25]

def normalize_price(price, bedrooms):
    """Normalize price based on bedroom type."""
    if bedrooms == 1:
        min_price, max_price = 2000, 3000
    else:
        min_price, max_price = 2800, 3900
    return (price - min_price) / (max_price - min_price)

def normalize_size(size, bedrooms):
    """Normalize size based on bedroom type."""
    if bedrooms == 1:
        min_size, max_size = 500, 900
    else:
        min_size, max_size = 700, 1100
    return (size - min_size) / (max_size - min_size)

def analyze_preferences(user_choices):
    """Analyze user choices to determine the most important features."""
    feature_importance = Counter()
    
    for choice in user_choices:
        preferred = choice["Preferred"]
        apartment = choice["Apartment A"] if preferred == "Apartment A" else choice["Apartment B"]
        
        feature_importance["Normalized Price"] += normalize_price(apartment["Price"], apartment["Bedrooms"])
        feature_importance["Normalized Size"] += normalize_size(apartment["Size"], apartment["Bedrooms"])
        feature_importance[f"Neighborhood - {apartment['Neighborhood']}"] += 1
        for amenity in apartment["Amenities"]:
            feature_importance[f"Amenity - {amenity}"] += 1
    
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
        st.session_state.comparison_pairs = generate_comparisons(n_apartments=15, bedrooms=bedrooms)
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
