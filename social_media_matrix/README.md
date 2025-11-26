### Step 1: Set Up Your Project Directory

1. **Create a new directory for your Streamlit project**:
   ```bash
   mkdir my_streamlit_app
   cd my_streamlit_app
   ```

2. **Create the `.streamlit` folder**:
   ```bash
   mkdir .streamlit
   ```

### Step 2: Create the `secrets.toml` File

1. **Inside the `.streamlit` folder, create a file named `secrets.toml`**:
   ```bash
   touch .streamlit/secrets.toml
   ```

2. **Open `secrets.toml` in a text editor and add your secrets**. Here’s an example of what the contents might look like:
   ```toml
   [database]
   user = "your_username"
   password = "your_password"
   host = "localhost"
   port = 5432
   dbname = "your_database"

   [api]
   key = "your_api_key"
   ```

### Step 3: Create a Basic Streamlit App

1. **Create a new Python file for your Streamlit app**:
   ```bash
   touch app.py
   ```

2. **Open `app.py` in a text editor and add some basic Streamlit code**:
   ```python
   import streamlit as st

   # Load secrets
   db_user = st.secrets["database"]["user"]
   db_password = st.secrets["database"]["password"]
   api_key = st.secrets["api"]["key"]

   st.title("My Streamlit App")
   st.write("Database User:", db_user)
   st.write("API Key:", api_key)
   ```

### Step 4: Run Your Streamlit App

1. **Make sure you have Streamlit installed**. If you haven't installed it yet, you can do so using pip:
   ```bash
   pip install streamlit
   ```

2. **Run your Streamlit app**:
   ```bash
   streamlit run app.py
   ```

### Summary

You now have a basic Streamlit project set up with a `.streamlit` folder containing a `secrets.toml` file for managing your secrets. You can expand on this by adding more functionality to your app and managing additional secrets as needed.