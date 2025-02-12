import streamlit as st
import boto3
import uvicorn
from fastapi import FastAPI, HTTPException
import threading
import requests
import random
from sql_agents.fix_syntax_agent import syntax_fix_graph
from sql_agents.standardize_agent import standardize_graph
from sql_agents.optimize_sql_agent import optimize_sql_graph
from sql_agents.create_sql_documentation_agent import document_sql_graph
import base64

# Set page configuration (must be the first Streamlit command)
st.set_page_config(page_title="ref[AI]ne | AHEAD", page_icon="💎", layout="wide")

# Custom CSS to style the app
st.markdown("""
    <style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    .stTextInput > div > div > input {
        background-color: #ffffff;
        color: #000000;
    }
    .stButton > button {
        background-color: #2c3e50;
        color: white;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
        width: 100%;
    }
    .stButton > button:hover {
        background-color: #3498db;  /* Change to your desired hover color */
        color: white;  /* Keep text color white on hover */
        transform: scale(1.05);  /* Slightly enlarge the button on hover */
        transition: transform 0.2s ease-in-out;  /* Smooth transition for the scale effect */
        border-color: white;
    }
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        padding: 20px;
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .header-logo img {
        width: 150px;
        height: auto;
        object-fit: contain;
    }
    .header-title {
        font-size: 24px;
        font-weight: bold;
        color: #2c3e50;
    }
    .header-subtitle {
        font-size: 14px;
        font-weight: normal;
        color: #7f8c8d;
    }
    .stAlert > div {
        color: #000000;
        background-color: #ffffff;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stTextArea > div > textarea {
        background-color: #ffffff;
        color: #000000;
        border-radius: 8px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .horizontal-container {
        display: flex;
        justify-content: space-between;
        gap: 20px;
    }
    .button-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        gap: 10px;
        margin: 20px;
    }
    .toggle-container {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .toggle {
        position: relative;
        display: inline-block;
        width: 60px;
        height: 34px;
    }
    .toggle input {
        opacity: 0;
        width: 0;
        height: 0;
    }
    .slider {
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #2c3e50;
        transition: .4s;
        border-radius: 34px;
    }
    .slider:before {
        position: absolute;
        content: "";
        height: 26px;
        width: 26px;
        left: 4px;
        bottom: 4px;
        background-color: #10a5de;
        transition: .4s;
        border-radius: 50%;
    }
    input:checked + .slider {
        background-color: #2c3e50;
    }
    input:checked + .slider:before {
        transform: translateX(26px);
    }
    </style>
    """, unsafe_allow_html=True)

# Path for logo
image_path = "logo.png"

# Logo and Title
with open(image_path, "rb") as image_file:
    logo_base64 = base64.b64encode(image_file.read()).decode("utf-8")

logo_html = f"""
<div class="header-container">
    <div class="header-logo">
        <img src="data:image/png;base64,{logo_base64}">
    </div>
    <div class="toggle-container">
        <label for="language-toggle">SQL</label>
        <label class="toggle">
            <input type="checkbox" id="language-toggle">
            <span class="slider"></span>
        </label>
        <label for="language-toggle">Python</label>
    </div>
</div>
"""

st.markdown(logo_html, unsafe_allow_html=True)

# Initialize AWS Bedrock Client
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-west-2')

# FastAPI App
app = FastAPI()

# FastAPI Endpoints
@app.post("/fix_syntax/")
async def fix_syntax(data: dict):
    sql_code = data.get("sql_code", "")
    if not sql_code:
        raise HTTPException(status_code=400, detail="SQL code is required")
    response = syntax_fix_graph.invoke({"user_input": sql_code})['response'].content
    return {"output": response}

@app.post("/standardize/")
async def standardize(data: dict):
    sql_code = data.get("sql_code", "")
    if not sql_code:
        raise HTTPException(status_code=400, detail="SQL code is required")
    response = standardize_graph.invoke({"user_input": sql_code})['response'].content
    return {"output": response}

@app.post("/optimize/")
async def optimize(data: dict):
    sql_code = data.get("sql_code", "")
    if not sql_code:
        raise HTTPException(status_code=400, detail="SQL code is required")
    response = optimize_sql_graph.invoke({"user_input": sql_code})['response'].content
    return {"output": response}


@app.post("/document/")
async def document(data: dict):
    sql_code = data.get("sql_code", "")
    if not sql_code:
        raise HTTPException(status_code=400, detail="SQL code is required")
    response = document_sql_graph.invoke({"user_input": sql_code})['response'].content
    return {"output": response}

# Start FastAPI Server in a Separate Thread
def run_fastapi():
    uvicorn.run(app, host="127.0.0.1", port=8502)  # Run on port 8502

threading.Thread(target=run_fastapi, daemon=True).start()

# Function to Call FastAPI from Streamlit
def fetch_from_api(endpoint, sql_code):
    try:
        response = requests.post(f"http://127.0.0.1:8502/{endpoint}/", json={"sql_code": sql_code})
        return response.json().get("output", "Error processing request")
    except Exception as e:
        return f"Error: {str(e)}"

# Horizontal layout for input and output boxes
with st.container():
    st.markdown('<div class="horizontal-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 0.4, 1])
    output_text = ""
    
    with col1:
        user_input = st.text_area("Input", height=350, key="input_text")
    with col2:
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        if st.button("Repair"):
            output_text = fetch_from_api("fix_syntax", user_input)
        if st.button("Standardize"):
            output_text = fetch_from_api("standardize", user_input)
        if st.button("Document"):
            output_text = fetch_from_api("document", user_input)
        if st.button("Optimize"):
            output_text = fetch_from_api("optimize", user_input)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.text_area("Output", output_text, height=350, key="output_text", disabled=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("About ref[AI]ne")
    st.markdown(
        """
        ref[AI]ne is an AI-powered tool for code quality. It offers:
        
        - Fixing Syntax Errors
        - Standardize Code
        - Generate Document
        - Code Optimization
        
        **Note:** This tool is designed to assist with code quality but is not a substitute for professional code review.
        """
    )
    st.warning("This is a demo application. The advice provided should not be considered as professional code review.")
    
    # Daily Coding Tip
    coding_tips = {
        "Name it like you mean it": "Use meaningful variable and function names. Your future self will thank you.",
        "DRY humor": "Keep your code DRY (Don't Repeat Yourself). Repetition is for comedians, not coders.",
        "Modular magic": "Write modular and reusable code. Think of it as LEGO for adults.",
        "Commentary corner": "Comment your code for better readability. It's like leaving breadcrumbs for the next developer.",
        "Backup bonanza": "Regularly back up your code. Because losing code is like losing your car keys—frustrating and avoidable.",
        "Git it together": "Use version control systems like Git. It's like having a time machine for your code.",
        "Performance pep talk": "Optimize your code for better performance. Slow code is like a snail in a race—nobody's cheering.",
        "Clean code club": "Keep your code clean and well-documented. Messy code is like a messy room—hard to find anything.",
        "Test fest": "Write unit tests to ensure code quality. It's like giving your code a health check-up.",
        "Dependency dance": "Regularly update your dependencies. Outdated dependencies are like expired milk—best avoided."
    }

    st.subheader("🌟 Daily Coding Tip")
    tip_key, tip_value = random.choice(list(coding_tips.items()))
    st.info(f"**{tip_key}**: {tip_value}")

# Footer
st.markdown("---")
st.markdown("Developed with 💙 | AHEAD | © 2025 ref[AI]ne")
