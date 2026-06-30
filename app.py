import streamlit as st
import googlemaps
from datetime import datetime

# Securely grab the API key from Streamlit's secrets
API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
gmaps = googlemaps.Client(key=API_KEY)

st.title("LA28 Games - Locality Calculator")
st.write("Determine staff locality and service eligibility based on commuting distances and public transit.")

# 1. Define your venues and their exact ZIP codes (or full addresses)
VENUES = {
    "Downtown LA Cluster (Crypto.com Arena)": "90015",
    "Inglewood Cluster (SoFi Stadium)": "90301",
    "Long Beach Cluster (Arena)": "90802",
    "Pasadena (Rose Bowl)": "91103",
    "Oklahoma City (Softball Park)": "73111",
    "New York (New York Stadium)": "07073", # MetLife is in NJ
    "San Diego (Snapdragon Stadium)": "92108"
}

# 2. User Inputs
home_zip = st.text_input("Applicant Home ZIP Code", placeholder="e.g., 90210")
venue_name = st.selectbox("Select Assigned Venue", list(VENUES.keys()))
venue_location = VENUES[venue_name]

if st.button("Calculate Locality"):
    if home_zip:
        try:
            with st.spinner("Calculating routes with Google Maps..."):
                # Fetch Driving Distance
                dist_result = gmaps.distance_matrix(home_zip, venue_location, mode="driving", units="imperial")
                distance_miles = dist_result['rows'][0]['elements'][0]['distance']['value'] * 0.000621371
                
                # Fetch Public Transit Time
                transit_result = gmaps.distance_matrix(home_zip, venue_location, mode="transit", departure_time=datetime.now())
                transit_status = transit_result['rows'][0]['elements'][0]['status']
                
                if transit_status == "OK":
                    transit_seconds = transit_result['rows'][0]['elements'][0]['duration']['value']
                    transit_minutes = transit_seconds / 60
                    transit_text = f"{int(transit_minutes)} minutes"
                else:
                    transit_minutes = 9999
                    transit_text = "No direct public transit available"

                # Apply Locality Logic
                if distance_miles > 100:
                    locality = "NL (Non-Local)"
                    services = "Flight Booking + Hotel Accommodation"
                    color = "red"
                elif distance_miles > 50:
                    locality = "SL (Semi-Local)"
                    services = "Hotel Accommodation Only"
                    color = "orange"
                else:
                    if transit_minutes > 90:
                        locality = "SL (Semi-Local) - Due to Transit Exception"
                        services = "Hotel Accommodation Only"
                        color = "orange"
                    else:
                        locality = "L (Local)"
                        services = "None (Local commuter)"
                        color = "green"

                # Display Results
                st.markdown("---")
                st.subheader("Results:")
                st.write(f"**Venue Location:** {venue_name} ({venue_location})")
                st.write(f"**Distance:** {distance_miles:.1f} miles")
                st.write(f"**Public Transit Commute:** {transit_text}")
                
                st.markdown(f"### Recommended Locality: :{color}[{locality}]")
                st.markdown(f"**Required Services:** {services}")

        except Exception as e:
            st.error("Error calculating routes. Please verify the Home ZIP code is valid.")
    else:
        st.warning("Please enter an Applicant Home ZIP code.")
