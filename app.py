import streamlit as st
import requests

# Streamlit app
def main():
    st.title("Shopkeeper Messaging Portal")
    
    # Form to collect user data
    st.subheader("User Information")
    name = st.text_input("Name")
    mobile_number = st.text_input("Mobile Number")
    whatsapp_number = st.text_input("WhatsApp Number")
    email = st.text_input("Email")
    locality = st.text_input("Locality")
    
    if st.button("Submit"):
        # Prepare data payload
        data = {
            "name": name,
            "mobile_number": mobile_number,
            "whatsapp_number": whatsapp_number,
            "email": email,
            "locality": locality
        }
        
        # Send data to FastAPI endpoint
        response = requests.post("http://localhost:8000/submit_user_data/", data=data)
        
        # Check response status
        if response.status_code == 200:
            st.success("User data submitted successfully!")
        else:
            st.error("Failed to submit user data.")
    
    # Owner classification
    st.subheader("Owner Classification")
    classification_options = ['A', 'B', 'C']
    classification = st.selectbox("Classification", classification_options)
    
    if st.button("Classify Users"):
        # Send request to FastAPI endpoint to classify users
        response = requests.post("http://localhost:8000/classify_users/")
        if response.status_code == 200:
            st.success("User classification updated successfully!")
        else:
            st.error("Failed to update user classification.")
    
    # WhatsApp message sending functionality
    if st.button("Send WhatsApp Message"):
        st.write("Sending WhatsApp messages...")
        # Send request to FastAPI endpoint to send WhatsApp messages
        response = requests.post("http://localhost:8000/send_whatsapp_message/")
        if response.status_code == 200:
            st.success("WhatsApp messages sent successfully!")
        else:
            st.error("Failed to send WhatsApp messages.")

if __name__ == "__main__":
    main()
