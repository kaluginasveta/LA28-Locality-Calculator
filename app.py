import streamlit as st
import googlemaps
from datetime import datetime

# Securely grab the API key from Streamlit's secrets
API_KEY = st.secrets["GOOGLE_MAPS_API_KEY"]
gmaps = googlemaps.Client(key=API_KEY)

st.title("LA28 Games - Locality Calculator")
st.write("Determine staff locality and service eligibility based on commuting distances and public transit.")

# 1. Define all LA28 venues using exact GPS coordinates (Latitude,Longitude)
VENUES = {
    'C00 - IBC': '34.1578705,-118.3441702',
    'C01 - Exposition Park Stadium (EXS)': '34.0127942,-118.284075',
    'C01 - LA Memorial Coliseum (MEM)': '34.0136647,-118.2878355',
    'C02 - Galen Center (GAL)': '34.0208427,-118.2798781',
    'C03 - DTLA Arena (DAR)': '34.0430175,-118.2672541',
    'C03 - LA Convention Center Hall 3 (DH3)': '34.0432322,-118.2697716',
    'C04 - LA Convention Center Hall 1 (DH1)': '34.0403207,-118.2695624',
    'C04 - LA Convention Center Hall 2 (DH2)': '34.0403207,-118.2695624',
    'C05 - Dodger Stadium (DGR)': '34.073851,-118.2399583',
    'C06 - Intuit Dome (IDM)': '33.9437983,-118.3421771',
    'C07 - 2028 Stadium (28S)': '33.9534651,-118.3390396',
    'C08 - Carson Field (CFD)': '33.8622873,-118.2641691',
    'C08 - Carson Stadium (CST)': '33.8640602,-118.2615563',
    'C09 - Carson Courts (CCS)': '33.8625164,-118.2611104',
    'C09 - Carson Velodrome (CVD)': '33.8590697,-118.2598152',
    'C12 - Belmont Shore (BMS)': '33.755431,-118.148839',
    'C13 - Port of Los Angeles (PLA)': '33.7365401,-118.264982',
    'C14 - Long Beach Aquatics Center (LAQ)': '33.7651393,-118.1858927',
    'C14 - Long Beach Arena (LOA)': '33.7641792,-118.1883324',
    'C14 - Long Beach Climbing Theater (LCT)': '33.7638007,-118.1868297',
    'C14 - Long Beach Target Shooting Hall (LSH)': '33.7650099,-118.1912155',
    'C15 - Marine Stadium (MRN)': '33.7679056,-118.1304895',
    'C17 - Alamitos Beach Stadium (ALA)': '33.7641159,-118.1799369',
    'C18 - Valley Complex 1 (VC1)': '34.1813999,-118.4984708',
    'C18 - Valley Complex 2 (VC2)': '34.1813999,-118.4984708',
    'C18 - Valley Complex 3 (VC3)': '34.1813999,-118.4984708',
    'C18 - Valley Complex 4 (VC4)': '34.1813999,-118.4984708',
    'C19 - Venice Beach (VBH)': '33.9932584,-118.480598',
    'C19.01 - Venice Beach Broadwalk (VBB)': '33.9948536,-118.4810376',
    'C20 - Riviera Country Club (RIV)': '34.0498288,-118.5013122',
    'C21 - Rose Bowl Stadium (RBS)': '34.1613284,-118.1676462',
    'C22 - Industry Hills MTB Course (INH)': '34.0207289,-117.927208',
    'C23 - Comcast Squash Center at Universal Studios (CSQ)': '34.1402766,-118.3600198',
    'C24 - Santa Anita Park (SAP)': '34.139204,-118.0452891',
    'C25 - Whittier Narrows Clay Shooting Center (WHI)': '34.0389694,-118.0687112',
    'C26 - Fairgrounds Cricket Stadium (FRG)': '34.0841898,-117.7674913',
    'C27 - Honda Center (ANH)': '33.8078476,-117.8764687',
    'C28 - Trestles State Beach (TSB)': '33.385011,-117.5841952',
    'C29 - OKC Softball Park (OSP)': '35.5243949,-97.4641342',
    'C30 - OKC Whitewater Center (OWC)': '35.4593303,-97.5189976',
    'C32 - San Diego Stadium (SDS)': '32.7841307,-117.1224366',
    'C33 - San Jose Stadium (SJS)': '37.351137,-121.924652',
    'C34 - Columbus Stadium (COS)': '39.9684078,-83.0169305',
    'C35 - St. Louis Stadium (STS)': '38.6306507,-90.2106091',
    'C36 - Nashville Stadium (NVS)': '36.1302013,-86.7655683',
    'C37 - New York Stadium (NYS)': '40.8135064,-74.074457',
    'C38 - Peacock Theater (PEA)': '34.0444495,-118.267151',
    'C39 - Rose Bowl Aquatics Center (RBA)': '34.1519873,-118.1648491',
    'C40 - Griffith Observatory (GRF)': '34.1184341,-118.3003935',
    'C40.01 - LA Zoo (LAZ)': '34.1471634,-118.2843674',
    'L50 - MPC': '33.9528342,-118.3413798',
    'L52 - Olympic Village': '34.0725242,-118.4512532',
    'LA2028 OCOG HQ': '34.0583287,-118.4441506',
    'Media Village (MVL)': '34.02483,-118.28413'
}

# Helper function to assign the correct arrival airport based on the venue selected
def get_arrival_airport(venue):
    if 'C29' in venue or 'C30' in venue: 
        return 'Will Rogers World Airport (OKC)'
    elif 'C32' in venue: 
        return 'San Diego International Airport (SAN)'
    elif 'C33' in venue: 
        return 'San Jose Mineta International Airport (SJC)'
    elif 'C34' in venue: 
        return 'John Glenn Columbus International Airport (CMH)'
    elif 'C35' in venue: 
        return 'St. Louis Lambert International Airport (STL)'
    elif 'C36' in venue: 
        return 'Nashville International Airport (BNA)'
    elif 'C37' in venue: 
        return 'Newark Liberty Intl (EWR) / John F. Kennedy Intl (JFK)'
    else:
        return 'Los Angeles International Airport (LAX)' # Default for LA / Southern California clusters

# 2. User Inputs
home_zip = st.text_input("Applicant Home ZIP Code", placeholder="e.g., 90210")
venue_name = st.selectbox("Select Assigned Venue", list(VENUES.keys()))
venue_location = VENUES[venue_name]

if st.button("Calculate Locality"):
    if home_zip:
        try:
            with st.spinner("Calculating routes and travel options with Google Maps..."):
                # Fetch Driving Distance & Time
                dist_result = gmaps.distance_matrix(home_zip, venue_location, mode="driving", units="imperial")
                
                if dist_result['rows'][0]['elements'][0]['status'] == "OK":
                    distance_miles = dist_result['rows'][0]['elements'][0]['distance']['value'] * 0.000621371
                    driving_text = dist_result['rows'][0]['elements'][0]['duration']['text']
                else:
                    st.error("Could not calculate a driving distance. Please check the Home ZIP code.")
                    st.stop()
                
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

                # Apply Locality Logic (Updated Rules)
                if distance_miles > 100:
                    locality = "NL (Non-Local)"
                    services = "Accommodation + Travel"
                    color = "red"
                elif distance_miles > 50:
                    locality = "SL (Semi-Local)"
                    services = "Accommodation only"
                    color = "orange"
                elif distance_miles < 5.0:
                    # Automatically Local if under 5 miles, bypassing transit check
                    locality = "L (Local)"
                    services = "None (Local commuter)"
                    color = "green"
                else:
                    # Between 5 and 50 miles: Check the 90-minute transit exception
                    if transit_minutes > 90:
                        locality = "SL (Semi-Local) - Due to Transit Exception"
                        services = "Accommodation only"
                        color = "orange"
                    else:
                        locality = "L (Local)"
                        services = "None (Local commuter)"
                        color = "green"

                # Display Results
                st.markdown("---")
                st.subheader("General Commute Information:")
                st.write(f"**Assigned Venue:** {venue_name}")
                st.write(f"**Distance:** {distance_miles:.1f} miles")
                st.write(f"**Average Driving Time (Informational):** {driving_text}")
                st.write(f"**Public Transit Commute:** {transit_text}")
                
                st.markdown(f"### Recommended Locality: :{color}[{locality}]")
                st.markdown(f"**Required Services:** {services}")

                # Identify Flight Commute for Non-Local Allocations
                if "NL" in locality:
                    st.markdown("---")
                    st.subheader("Flight Commute Details:")
                    
                    departure_airport = "Unknown Airport (Manual Check Required)"
                    
                    # Look up coordinates of applicant ZIP to search for nearest airport
                    geocode_res = gmaps.geocode(home_zip)
                    if geocode_res:
                        latlng = geocode_res[0]['geometry']['location']
                        # Search Google Places for the closest major airport to the applicant
                        places_res = gmaps.places(query="international airport", location=latlng)
                        if places_res.get('results'):
                            departure_airport = places_res['results'][0]['name']
                            
                    arrival_airport = get_arrival_airport(venue_name)
                    
                    st.write(f"🛫 **Recommended Departure Airport:** {departure_airport}")
                    st.write(f"🛬 **Recommended Arrival Airport:** {arrival_airport}")

        except Exception as e:
            st.error(f"Error calculating routes: {e}. Please verify the Home ZIP code is valid.")
    else:
        st.warning("Please enter an Applicant Home ZIP code.")
