import streamlit as st
import time
import requests
from datetime import datetime, timezone, timedelta
from locker_utils import send_password_sms, generate, put_request



try:
    st.title("Select a Locker")
    

    response = requests.get("http://127.0.0.1:8000/lockers/empty")
    response.raise_for_status()
    available_lockers = response.json()


    locker_ids = [locker['id'] for locker in available_lockers]
    selected_locker_id = st.selectbox("Select Locker", locker_ids)


    selected_locker = next(locker for locker in available_lockers if locker['id'] == selected_locker_id)
    phone = selected_locker['phone'] or ""  
    status = selected_locker['status']


    new_phone = st.text_input("Phone Number", "")


    valid_phone = new_phone.isdigit() and len(new_phone) == 10
    if not valid_phone and new_phone != "":
        st.error("Phone number must be exactly 10 digits.")


    lock_times = [5, 10, 15, 30]
    selected_lock_time = st.selectbox("Book locker for (in minutes)", lock_times)


    if "password" not in st.session_state:
        st.session_state.password = None


    if st.button("Generate password"):

        try:

            password=generate()
            if len(password) == 4:
                st.session_state.password = password  
                st.success(f"Confirm {password} as password or generate new password?")
            else:
                st.error("Failed to generate a valid password.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")


    if st.button("Confirm and pay") and valid_phone:
        phone_ext= "+91"+new_phone       
        try:
            password = send_password_sms(phone_ext, selected_locker["id"], st.session_state.password)
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")
        
        if st.session_state.password:
            
            payload = {
                "phone": new_phone,
                "password": st.session_state.password,  
                "unlock_time": str(datetime.now(timezone.utc) + timedelta(minutes=selected_lock_time)),
            }

            try:
                
                
              
                response=put_request(selected_locker_id, payload)
                response.raise_for_status()
                st.success(f"Payment successful! Locker {selected_locker_id} updated successfully with password {st.session_state.password}.")
                st.session_state.password=None
                time.sleep(1)
                st.empty()
                
            except requests.exceptions.HTTPError as e:
                st.error(f"Error updating locker: {response.json().get('detail', str(e))}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                
        else:
            st.error("You must generate a password for locker before confirming the selection.")

except requests.exceptions.RequestException as e:
    st.error(f"Error fetching available lockers: {e}")

