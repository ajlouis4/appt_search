import random
import pandas as pd
import streamlit as st
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
        "Price Category": categorize_price(price, bedrooms),
        "Size": size,
        "Size Category": categorize_size(size, bedrooms),
        "Neighborhood": neighborhood,
        "Amenities": amenities
    }

def categorize_price(price, bedrooms):
    """Categorize price into Low, Medium, or High buckets for importance evaluation."""
    if bedrooms == 1:
        if price < 2300:
            return "Low"
        elif price < 2700:
            return "Medium"
        else:
            return "High"
    else:
        if price < 3100:
            return "Low"
        elif price < 3500:
            return "Medium"
        else:
            return "High"

def categorize_size(size, bedrooms):
    """Categorize size into Small, Medium, or Large buckets for importance evaluation."""
    if bedrooms == 1:
        if size < 650:
            return "Small"
        elif size < 800:
            return "Medium"
        else:
            return "Large"
    else:
        if size < 850:
            return "Small"
        elif size < 1000:
            return "Medium"
        else:
            return "Large"

def generate_apartments(n_apartments=25, bedrooms=1):
    """Generate a list of apartments for rating."""
    return [generate_apartment(bedrooms) for _ in range(n_apartments)]

def analyze_preferences(user_ratings):
    """Analyze user ratings to determine the most important features, scaling importance by availability."""
    feature_importance = Counter()
    feature_counts = Counter()
    
    for rating_entry in user_ratings:
        apartment = rating_entry["Apartment"]
        rating = rating_entry["Rating"]
        
        feature_counts[f"Price - {apartment['Price Category']}"] += 1
        feature_importance[f"Price - {apartment['Price Category']}"] += rating
        
        feature_counts[f"Size - {apartment['Size Category']}"] += 1
        feature_importance[f"Size - {apartment['Size Category']}"] += rating
        
        feature_counts[f"Neighborhood - {apartment['Neighborhood']}"] += 1
        feature_importance[f"Neighborhood - {apartment['Neighborhood']}"] += rating
        
        for amenity in apartment["Amenities"]:
            feature_counts[f"Amenity - {amenity}"] += 1
            feature_importance[f"Amenity - {amenity}"] += rating
    
    # Scale importance by availability
    for feature in feature_importance:
        feature_importance[feature] /= feature_counts[feature]
    
    sorted_features = feature_importance.most_common()
    return pd.DataFrame(sorted_features, columns=["Feature", "Importance"])

def streamlit_app():
    """Streamlit UI for apartment rating study."""
    st.title("Apartment Rating Study")
    
    if "user_ratings" not in st.session_state:
        st.session_state.user_ratings = []
    
    if "current_index" not in st.session_state:
        st.session_state.current_index = 0
    
    bedroom_choice = st.radio("Select Apartment Type", ["1 Bedroom", "2 Bedroom"], key="bedroom_choice")
    bedrooms = 1 if bedroom_choice == "1 Bedroom" else 2
    
    if "last_bedroom_choice" not in st.session_state or st.session_state.last_bedroom_choice != bedroom_choice:
        st.session_state.apartments = generate_apartments(n_apartments=25, bedrooms=bedrooms)
        st.session_state.current_index = 0
        st.session_state.last_bedroom_choice = bedroom_choice
    
    if st.session_state.current_index < len(st.session_state.apartments):
        apartment = st.session_state.apartments[st.session_state.current_index]
        st.subheader(f"Apartment {st.session_state.current_index + 1} - {bedroom_choice}")
        
        for key, value in apartment.items():
            st.write(f"**{key}:** {', '.join(value) if isinstance(value, list) else value}")
        
        rating = st.slider("Rate this apartment (1-5)", 1, 5, 3, key=f"rating_{st.session_state.current_index}")
        
        if st.button("Save Rating"):
            st.session_state.user_ratings.append({"Apartment": apartment, "Rating": rating})
            st.session_state.current_index += 1
            st.experimental_set_query_params(index=st.session_state.current_index)
            st.rerun()
    
    if st.session_state.current_index >= len(st.session_state.apartments):
        if st.button("Analyze Preferences"):
            results_df = analyze_preferences(st.session_state.user_ratings)
            st.write("### Most Important Features")
            st.dataframe(results_df)
            st.download_button("Download Feature Importance CSV", results_df.to_csv(index=False).encode("utf-8"), "Feature_Importance.csv", "text/csv")

if __name__ == "__main__":
    streamlit_app()
