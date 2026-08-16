import streamlit as st
import requests

API_URL = "http://localhost:8000/plan_trip/"

def trip_planner_app():
    st.title("Travel Agent")
    location = st.text_input("From where will you be traveling from?")
    city = st.text_input("Which place are you interested in visiting?")
    customer_interest_topic = st.text_input("Any interests or hobbies during the visit?")
    date_range = st.text_input("Date range for the trip?")

    if st.button("Plan My Trip"):
        if location and city and date_range:
            st.write("Planning your trip...")
            payload = {
                "origin": location,
                "city": city,
                "customer_interest_topic": customer_interest_topic,
                "date_range": date_range
            }
            try:
                response = requests.post(API_URL, json=payload)
                if response.status_code == 200:
                    result = response.json()["trip_plan"]
                    st.success("Here is your Trip Plan:")
                    st.write(result)
                else:
                    st.error("Something went wrong.")
            except Exception as e:
                st.error(f"Error calling the API: {e}")
        else:
            st.warning("Please fill in all fields.")

if __name__ == "__main__":
    trip_planner_app()