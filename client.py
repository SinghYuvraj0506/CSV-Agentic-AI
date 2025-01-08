import streamlit as st
import requests

API_URL = "http://localhost:8000/response_csv" 

def test_csv_api(user_command, upload_file, generate_new):
    """Function to send the user's request to the API and get a response"""
    try:
        files = {
            "upload_file": (upload_file.name, upload_file, upload_file.type)
        }
        data = {
            "user_command": user_command,
            "generateNew": generate_new
        }

        response = requests.post(API_URL, data=data, files=files)

        if response.status_code == 200:
            return response
        else:
            return f"Error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"An error occurred: {str(e)}"

# Streamlit UI
st.title("CSV File Processing and API Test")

st.write(
    "This app lets you test the functionality of the CSV processing API. Upload a CSV file, "
    "enter a user command, and choose whether to generate a new file or just get the output."
)

# File upload widget
upload_file = st.file_uploader("Upload CSV File", type=["csv"])

# User command input
user_command = st.text_input("Enter your command", "Highest revenue movies of all time")

# Option to generate a new CSV file or not
generate_new = st.checkbox("Generate New CSV File")

# Submit button to call the API
if st.button("Submit"):
    if upload_file and user_command:
        st.write("Processing... Please wait.")
        response = test_csv_api(user_command, upload_file, generate_new)
        
        if isinstance(response, requests.models.Response):
            if generate_new:
                st.download_button(
                    label="Download Generated CSV",
                    data=response.content,
                    file_name="output.csv",
                    mime="text/csv"
                )
            else:
                st.text_area("API Response", response.text, height=200)
        else:
            st.error(response)
    else:
        st.warning("Please upload a file and enter a command before submitting.")
