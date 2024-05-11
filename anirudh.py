import streamlit as st
import pandas as pd
import pywhatkit
import requests
##pywhatkit.start_server()
from datetime import datetime
from datetime import datetime, timedelta
# Data storage
user_data = pd.DataFrame(columns=["Name", "Mobile Number", "WhatsApp Number", "Email", "Locality", "Classification"])

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
        # Store user data
        global user_data
        new_user = pd.DataFrame({"Name": [name], "Mobile Number": [mobile_number], "WhatsApp Number": [whatsapp_number], "Email": [email], "Locality": [locality], "Classification": [""]})
        user_data = pd.concat([user_data, new_user], ignore_index=True)
        st.success("User data submitted successfully!")
        
    # Owner classification
    st.subheader("Owner Classification")
    classification_options = ['A', 'B', 'C']
    for index, user in user_data.iterrows():
        classification = st.selectbox(f"Classification for {user['Name']}", classification_options, key=f"classification_{index}")
        user_data.at[index, "Classification"] = classification
    st.success("User classification updated successfully!")
    
    # WhatsApp message sending functionality
    if st.button("Send WhatsApp Message"):
        for index, user in user_data.iterrows():
            if user['WhatsApp Number']:
                message = f"Hello {user['Name']}, thank you for being our customer! We have classified you as Class {user['Classification']}."
                send_whatsapp_message(user['WhatsApp Number'], message)
        st.success("WhatsApp messages sent successfully!")




def send_whatsapp_message(phone_number, message):
    current_time = datetime.now()
    send_time = current_time + timedelta(minutes=2)
    hour = send_time.hour
    minute = send_time.minute
    # time.sleep(60)
    pywhatkit.sendwhatmsg(phone_number, message, hour, minute)

if __name__ == "__main__":
    main()
