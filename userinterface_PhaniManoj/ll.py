import streamlit as st
import psycopg2
import hashlib
from PIL import Image
import os
import cv2
import numpy as np
import streamlit.components.v1 as components

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Connect to PostgreSQL database
def get_connection():
    return psycopg2.connect(
        host="localhost", 
        database="tea_leaf_detection",  
        user="yourusername",  
        password="yourpassword"   
    )

# Function to add a new user to the database
def add_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

# Function to check login credentials
def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, hashed_password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Streamlit App
st.markdown(
    """
    <style>
    .main {
        background-image: url("https://c4.wallpaperflare.com/wallpaper/465/306/506/fresh-green-tea-leaves-sunlight-wallpaper-preview.jpg");
        background-size:cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Define your custom HTML for the background
background_html = """
<style>
body {
background-image: url('C://Users//phani//desktop//userinterface_PhaniManoj//ko.jpeg');
background-size: cover;
}
</style>
"""

# Inject custom HTML
components.html(background_html, height=0)

# Custom CSS for the sidebar background and text color
sidebar_bg = """
<style>
[data-testid="stSidebar"] > div:first-child {
    background-image: url('https://c4.wallpaperflare.com/wallpaper/241/692/522/tea-leaves-nature-plants-wallpaper-preview.jpg');
    background-size: cover;
}
[data-testid="stSidebar"] .css-1d391kg {
    color: orange; /* Orange text color */
}
</style>
"""
st.markdown(sidebar_bg, unsafe_allow_html=True)

# Login and Signup Pages
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Select Page", ["Login", "Sign Up", "Home", "Detect Disease"])

    if page == "Login":
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.success("Login successful!")
                st.session_state['logged_in'] = True
            else:
                st.error("Invalid username or password")

    elif page == "Sign Up":
        st.title("Sign Up")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        if st.button("Sign Up"):
            if add_user(username, password):
                st.success("Account created successfully!")
            else:
                st.error("Username already exists")

    elif page == "Home":
        if st.session_state.get('logged_in'):
            st.title("Welcome to Tea Leaf Disease Detection")
            st.markdown("""
            ## Tea Leaf Disease Detection System
            This application is designed to help identify and diagnose various diseases that affect tea leaves. By analyzing images of tea leaves, the system can provide insights into the type of disease present, aiding in timely and effective treatment.

            ### Common Tea Leaf Diseases:
            - **Algal Leaf**: Controlled with fungicides like copper oxychloride.
            - **Anthracnose**: Controlled with fungicides like mancozeb or copper hydroxide.
            - **Bird Eye Spot**: Controlled with fungicides like copper oxychloride or carbendazim.
            - **Brown Blight**: Controlled with fungicides like mancozeb or carbendazim.
            - **Gray Light**: Controlled with fungicides like copper oxychloride or chlorothalonil.
            - **Red Leaf Spot**: Controlled with fungicides like copper oxychloride or mancozeb.
            - **White Spot**: Controlled with fungicides like hexaconazole or thiophanate-methyl.

            ### How to Use This Application:
            - Navigate to the 'Detect Disease' page.
            - Select an image of a tea leaf from the sidebar.
            - View the identified disease and leaf features.

            **© Phani Manoj**
            """)
        else:
            st.warning("Please login to access this page.")

    elif page == "Detect Disease":
        if st.session_state.get('logged_in'):
            st.title("Tea Leaf Disease Detection")
            
            # Add an "About" button
            if st.button('About'):
                st.markdown("""
                ## Tea Leaf Diseases
                Tea leaves can be affected by various diseases, which can impact the quality and yield of tea production. Some common tea leaf diseases include:
                - **Algal leaf**: To cure agal leaf disease in tea leaves, use a fungicide composition such as copper oxychloride (50% WP) or hexaconazole (5% SC), applying as per recommended dosage for effective control. Always follow label instructions for safe and effective application.
                - **Anthracnose**: To cure anthracnose leaf disease in tea leaves, use a fungicide composition like mancozeb (75% WP) or copper hydroxide (77% WP), applied according to recommended dosages. Ensure to follow label instructions and safety guidelines for effective control.
                - **bird eye spot**: To cure bird's eye spot disease in tea leaves, use a fungicide composition such as copper oxychloride (50% WP) or carbendazim (50% WP), applied at the recommended dosage. Follow label instructions and safety guidelines for effective and safe application.
                - **brown blight**: To cure brown blight leaf disease in tea leaves, use a fungicide composition such as mancozeb (75% WP) or carbendazim (50% WP), applied at the recommended dosage. Follow label instructions and safety guidelines for effective and safe application.
                - **gray light**: To cure gray blight (agal leaf disease) in tea leaves, use a fungicide composition such as copper oxychloride (50% WP) or chlorothalonil (75% WP), applied at the recommended dosage. Ensure to follow label instructions and safety guidelines for effective control.
                - **red leaf spot**: To cure red leaf spot disease in tea leaves, use a fungicide composition such as copper oxychloride (50% WP) or mancozeb (75% WP), applied at the recommended dosage. Follow label instructions and safety guidelines for effective and safe application.
                - **White spot**: To cure white spot disease in tea leaves, use a fungicide composition such as hexaconazole (5% SC) or thiophanate-methyl (70% WP), applied at the recommended dosage. Follow label instructions and safety guidelines for effective and safe application.

                **© Phani Manoj**
                """)
                st.stop()
            
            # Create a sidebar for selecting an image
            st.sidebar.title("Select an image")
            
            # Function to load images and their labels
            @st.cache_data
            def load_images(image_dir):
                data = []
                for disease_folder in os.listdir(image_dir):
                    disease_path = os.path.join(image_dir, disease_folder)
                    if os.path.isdir(disease_path):
                        for image_file in os.listdir(disease_path):
                            image_path = os.path.join(disease_path, image_file)
                            if os.path.isfile(image_path):
                                data.append((image_path, disease_folder))
                return data

            # Function to get leaf features
            def get_leaf_features(image_path):
                image = cv2.imread(image_path)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                if contours:
                    c = max(contours, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(c)
                    area = cv2.contourArea(c)
                    perimeter = cv2.arcLength(c, True)
                    aspect_ratio = float(w) / h
                    return w, h, area, perimeter, aspect_ratio
                else:
                    return None, None, None, None, None

            # Path to your dataset directory
            image_dir = 'C:/Users/phani/OneDrive/Desktop/tea_sickness_dataset'  # Replace with your dataset directory path

            # Load images
            data = load_images(image_dir)

            # Display images and their labels in the sidebar
            selected_image = st.sidebar.selectbox(
                "Image List",
                [os.path.basename(image[0]) for image in data]
            )
            
            # Find the selected image path and its disease
            selected_image_path = None
            selected_disease = None
            for image_path, disease in data:
                if os.path.basename(image_path) == selected_image:
                    selected_image_path = image_path
                    selected_disease = disease
                    break
            
            # Display the selected image and its disease label
            if selected_image_path:
                image = Image.open(selected_image_path)
                st.image(image, caption=f'Selected Image: {selected_image}', use_column_width=True)
                st.write(f"**Disease:** {selected_disease}")
                
                # Get leaf features
                width, height, area, perimeter, aspect_ratio = get_leaf_features(selected_image_path)
                
                if width is not None:
                    st.write(f"**Leaf Width:** {width} pixels")
                    st.write(f"**Leaf Height:** {height} pixels")
                    st.write(f"**Leaf Area:** {area} pixels²")
                    st.write(f"**Leaf Perimeter:** {perimeter} pixels")
                    st.write(f"**Aspect Ratio:** {aspect_ratio:.2f}")
                else:
                    st.write("Could not extract leaf features.")
                st.markdown("""**© Phani Manoj**""")
        else:
            st.warning("Please login to access this page.")

if __name__ == "__main__":
    main()
