import streamlit as st
import requests

# Input field for the user's phone number
phone_number = st.text_input("Enter your Phone Number (10 digits):", "")

# Validation for phone number
valid_phone = phone_number.isdigit() and len(phone_number) == 10

if valid_phone:
    # Fetch lockers associated with the phone number
    try:
        response = requests.get(f"http://127.0.0.1:8000/lockers/locked/{phone_number}")  # Update your FastAPI endpoint as needed
        response.raise_for_status()
        lockers = response.json()

        if lockers:
            # Create a dropdown for lockers associated with the entered phone number
            locker_ids = [locker['id'] for locker in lockers]
            selected_locker_id = st.selectbox("Select your locker", locker_ids)

            # Get details of the selected locker
            selected_locker = next(locker for locker in lockers if locker['id'] == selected_locker_id)
            stored_password = selected_locker['password'] or ""  # Get the stored password for validation

            # Input field for password
            password = st.text_input("Password", value="", type="password")

            # Validation for password
            valid_password = password.isdigit() and len(password) == 4

            if not valid_password and password:
                st.error("Password must be exactly 4 digits.")

            # Unlock logic
            if st.button("Unlock Locker") and valid_password:
                if password != stored_password:
                    st.error("Password is incorrect.")
                else:
                    # Send request to update the locker status
                    try:
                        payload = {"phone": phone_number, "password": password}
                        response = requests.delete(f"http://127.0.0.1:8000/lockers/{selected_locker_id}", json=payload)
                        response.raise_for_status()
                        st.success(f"Locker {selected_locker_id} unlocked successfully.")
                    except requests.exceptions.HTTPError as e:
                        st.error(f"Error unlocking locker: {response.json().get('detail', str(e))}")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")
        else:
            st.warning("No lockers found for this phone number.")

    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching lockers: {e}")
else:
    if phone_number:
        st.error("Phone number must be exactly 10 digits.")
