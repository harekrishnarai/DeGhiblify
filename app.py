import os
import streamlit as st
import tempfile
from PIL import Image
from io import BytesIO
import sys
import base64
import time
import random
import re

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix imports - remove DeGhiblify prefix since we're already in that directory
from src.openai_client import OpenAIClient
from src.image_processor import ImageProcessor
from src.utils import generate_output_filename, handle_api_error
from config.settings import OPENAI_API_KEY, DEBUG_MODE

# Hide deployment configs
st.set_option('client.showErrorDetails', False)

# Create assets directory if it doesn't exist
assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
os.makedirs(assets_dir, exist_ok=True)

# Configuration and page setup
st.set_page_config(
    page_title="DeGhiblify",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Replace the animated particles (alternative approach if above doesn't work)
def add_bg_animation():
    """Add a simpler background animation that won't cause rendering issues"""
    st.markdown("""
    <style>
    @keyframes pulse {
        0% { transform: scale(1); opacity: 0.2; }
        50% { transform: scale(1.05); opacity: 0.3; }
        100% { transform: scale(1); opacity: 0.2; }
    }
    
    .bg-animation {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        pointer-events: none;
    }
    
    .bg-circle {
        position: absolute;
        border-radius: 50%;
        background: radial-gradient(circle, var(--circle-color) 0%, transparent 70%);
        animation: pulse var(--duration) infinite ease-in-out;
        animation-delay: var(--delay);
    }
    </style>
    
    <div class="bg-animation">
        <div class="bg-circle" style="--circle-color: rgba(59, 130, 246, 0.2); width: 500px; height: 500px; top: 20%; left: 10%; --duration: 10s; --delay: 0s;"></div>
        <div class="bg-circle" style="--circle-color: rgba(139, 92, 246, 0.2); width: 400px; height: 400px; top: 60%; left: 75%; --duration: 12s; --delay: 2s;"></div>
        <div class="bg-circle" style="--circle-color: rgba(79, 70, 229, 0.2); width: 350px; height: 350px; top: 10%; left: 80%; --duration: 8s; --delay: 1s;"></div>
    </div>
    """, unsafe_allow_html=True)

# Use this simpler animation instead of the particle system
add_bg_animation()

# Apply dark mode styling
st.markdown('''
<style>
    /* Dark mode theme */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
        transition: all 0.2s ease;
    }
    
    .stApp {
        background-color: #0f172a;
        color: #e2e8f0;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        letter-spacing: 0.5px;
    }
    
    h1 {
        font-size: 2.5rem !important;
    }
    
    p, div, span, label {
        color: #cbd5e1 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    
    /* Input fields */
    input[type="text"], 
    input[type="password"], 
    input[type="email"], 
    input[type="number"],
    input[type="date"],
    textarea,
    select {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border: 1px solid #475569 !important;
        border-radius: 8px !important;
    }
    
    /* Button styling */
    .stButton > button {
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
    }
    
    .stButton > button[data-baseweb="button"] {
        background-color: #3b82f6 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #1e293b !important;
        color: #e2e8f0 !important;
        border-radius: 8px !important;
    }
    
    .streamlit-expanderContent {
        background-color: #1e293b !important;
        border-top: none !important;
    }
    
    /* FileUploader styling */
    [data-testid="stFileUploader"] {
        background-color: #1e293b !important;
        border-radius: 8px !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #3b82f6 !important;
    }
    
    /* Divider */
    hr {
        border-color: #334155 !important;
    }
    
    /* Animation for app loading */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .main {
        animation: fadeIn 0.5s ease-out forwards;
    }
    
    /* Glow effects */
    .glow-text {
        text-shadow: 0 0 10px rgba(59, 130, 246, 0.5), 0 0 20px rgba(59, 130, 246, 0.3);
    }
    
    .glow-box {
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
    }
</style>
''', unsafe_allow_html=True)

# Define custom card component for dark mode
def custom_card(content, title=None, key=None):
    card_container = st.container()
    with card_container:
        st.markdown('''
        <style>
        .dark-card {
            background-color: #1e293b;
            border-radius: 16px;
            padding: 20px 25px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
            margin-bottom: 24px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-left: 4px solid #3b82f6;
            position: relative;
            overflow: hidden;
        }
        .dark-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4), 0 0 15px rgba(59, 130, 246, 0.3);
        }
        .dark-card-title {
            font-weight: 600;
            font-size: 1.2rem;
            margin-bottom: 16px;
            color: #e2e8f0 !important;
            border-bottom: 1px solid #334155;
            padding-bottom: 8px;
        }
        .dark-card-accent {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 2px;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        }
        </style>
        ''', unsafe_allow_html=True)
        
        title_html = f'<div class="dark-card-title">{title}</div>' if title else ''
        st.markdown(f'<div class="dark-card"><div class="dark-card-accent"></div>{title_html}{content}</div>', unsafe_allow_html=True)
    return card_container

# Enhanced image card with before/after effects for dark mode
def image_card(image, caption, type="before"):
    img_bytes = BytesIO()
    image.save(img_bytes, format='PNG')
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode()
    
    # Different styling for before vs after images
    if type == "before":
        card_color = "#3b82f6"
        accent_gradient = "linear-gradient(90deg, #3b82f6, #60a5fa)"
        badge_text = "ORIGINAL"
        badge_color = "rgba(59, 130, 246, 0.9)"
    else:
        card_color = "#8b5cf6"
        accent_gradient = "linear-gradient(90deg, #8b5cf6, #a78bfa)"
        badge_text = "TRANSFORMED"
        badge_color = "rgba(139, 92, 246, 0.9)"
    
    st.markdown(f'''
    <style>
    .dark-img-card-{type} {{
        position: relative;
        background-color: #1e293b;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        overflow: hidden;
        border-left: 3px solid {card_color};
        margin-bottom: 24px;
    }}
    .dark-img-card-{type}:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4), 0 0 15px rgba(59, 130, 246, 0.3);
    }}
    .dark-accent-line-{type} {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: {accent_gradient};
    }}
    .dark-img-container-{type} {{
        position: relative;
        width: 100%;
        overflow: hidden;
        border-radius: 8px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }}
    .dark-img-badge-{type} {{
        position: absolute;
        top: 15px;
        right: 15px;
        background: {badge_color};
        color: white;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 5px 10px;
        border-radius: 30px;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.2);
        letter-spacing: 0.5px;
    }}
    .dark-img-caption-{type} {{
        text-align: center;
        padding: 16px 0 5px 0;
        font-weight: 500;
        color: #e2e8f0 !important;
        font-size: 1.05rem;
    }}
    </style>
    
    <div class="dark-img-card-{type}">
        <div class="dark-accent-line-{type}"></div>
        <div class="dark-img-container-{type}">
            <img src="data:image/png;base64,{img_base64}" style="width: 100%; display: block;" />
            <div class="dark-img-badge-{type}">{badge_text}</div>
        </div>
        <div class="dark-img-caption-{type}">{caption}</div>
    </div>
    ''', unsafe_allow_html=True)

# Animated button for dark mode
def animated_button(label, key, icon=None, is_primary=True, disabled=False):
    return st.button(
        f"✨ {label}" if icon else label,
        key=key,
        type="primary" if is_primary else "secondary",
        disabled=disabled,
        use_container_width=True,
    )

# Add this function to validate OpenAI API keys
def is_valid_openai_key(api_key):
    """Validate if the provided string matches OpenAI API key format"""
    # OpenAI keys typically start with 'sk-' followed by alphanumeric characters
    # and are typically around 51 characters in length
    #pattern = r'^sk-[a-zA-Z0-9]{48,52}$'
    return True

# App header with animated hero section - dark mode version
st.markdown('''
<div style="text-align: center; padding: 40px 20px; animation: fadeIn 0.8s ease-out;">
    <h1 style="font-size: 3rem !important; margin-bottom: 15px; color: #3b82f6; font-weight: 700;">
        <span style="color: #8b5cf6;">✨</span> DeGhiblify
    </h1>
    <p style="font-size: 1.3rem; max-width: 700px; margin: 0 auto 30px auto; color: #94a3b8 !important;">
        Transform Studio Ghibli characters into photorealistic humans using AI magic
    </p>
    <div style="width: 100px; height: 3px; background: linear-gradient(90deg, #3b82f6, #8b5cf6); margin: 0 auto;"></div>
</div>
''', unsafe_allow_html=True)

# Custom sidebar - dark mode
with st.sidebar:
    st.markdown('''
    <div style="text-align: center; margin-bottom: 20px;">
        <h3 class="glow-text" style="margin-bottom: 10px;">✨ Settings</h3>
        <div style="width: 50px; height: 2px; background: linear-gradient(90deg, #3b82f6, #8b5cf6); margin: 0 auto 20px auto;"></div>
    </div>
    ''', unsafe_allow_html=True)
    
    # API Key input with dark mode styling
    st.markdown('<p style="font-weight: 500; margin-bottom: 8px; color: #e2e8f0;">OpenAI API Key</p>', unsafe_allow_html=True)
    api_key = st.text_input(
        "Enter your key",
        value=OPENAI_API_KEY if OPENAI_API_KEY != "your_openai_api_key_here" else "",
        type="password",
        label_visibility="collapsed"
    )

    # Validate the API key
    is_valid_key = False
    if not api_key:
        st.markdown('''
        <div style="background-color: rgba(251, 191, 36, 0.1); border-left: 3px solid #f59e0b; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <p style="margin: 0; display: flex; align-items: center; color: #fbbf24 !important;">
                <span style="margin-right: 10px; font-size: 1.2rem;">⚠️</span>
                Please enter your OpenAI API key
            </p>
        </div>
        ''', unsafe_allow_html=True)
    elif not is_valid_openai_key(api_key):
        st.markdown('''
        <div style="background-color: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <p style="margin: 0; display: flex; align-items: center; color: #ef4444 !important;">
                <span style="margin-right: 10px; font-size: 1.2rem;">❌</span>
                Invalid API key format. Should start with sk- followed by ~50 characters.
            </p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        is_valid_key = True
        st.markdown('''
        <div style="background-color: rgba(34, 197, 94, 0.1); border-left: 3px solid #22c55e; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <p style="margin: 0; display: flex; align-items: center; color: #22c55e !important;">
                <span style="margin-right: 10px; font-size: 1.2rem;">✅</span>
                API key format is valid
            </p>
        </div>
        ''', unsafe_allow_html=True)
    
    st.divider()
    
    # About section - dark mode
    custom_card('''
    <p style="margin-top: 0; color: #cbd5e1 !important;">
        DeGhiblify uses OpenAI's advanced AI models to transform Ghibli-style 
        anime characters into realistic human portraits while preserving the 
        character's essence.
    </p>
    <p style="margin-bottom: 0; color: #cbd5e1 !important;">
        Upload a Ghibli-style image to get started.
    </p>
    ''', title="About")
    
    # How it works section - dark mode
    custom_card('''
    <ol style="padding-left: 20px; margin-top: 0; margin-bottom: 0; color: #cbd5e1 !important;">
        <li style="margin-bottom: 10px;">The app analyzes your anime character using GPT-4 Vision</li>
        <li style="margin-bottom: 10px;">It creates a detailed description of the character</li>
        <li>DALL-E generates a realistic human based on the description</li>
    </ol>
    ''', title="How It Works")
    
    # Examples section - dark mode
    custom_card('''
    <p style="margin-top: 0; margin-bottom: 10px; color: #cbd5e1 !important;">Try DeGhiblify with characters like:</p>
    <ul style="padding-left: 20px; margin-top: 0; margin-bottom: 0; color: #cbd5e1 !important;">
        <li>Princess Mononoke</li>
        <li>Howl from Howl's Moving Castle</li>
        <li>Chihiro from Spirited Away</li>
        <li>Nausicaä</li>
        <li>Totoro (as a human)</li>
    </ul>
    ''', title="Try These Characters")

# Main content with two columns
col1, col2 = st.columns([1, 1])

with col1:
    custom_card('''
    <p style="margin-top: 0; color: #cbd5e1 !important;">
        Upload a Ghibli-style character image below. The AI works best with clear, front-facing character portraits.
    </p>
    ''', title="1. Upload Your Ghibli Character")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        image_card(image, caption="Your Ghibli Character", type="before")
        
        # Process button
        process_button = animated_button(
            "Transform to Human", 
            key="transform_btn", 
            disabled=not (api_key and is_valid_key)
        )

with col2:
    custom_card('''
    <p style="margin-top: 0; color: #cbd5e1 !important;">
        The AI-generated photorealistic interpretation will appear here after processing.
    </p>
    ''', title="2. See the Human Transformation")
    
    # Process the image when button is clicked
    if uploaded_file is not None and 'process_button' in locals() and process_button:
        # Create a single placeholder for status updates
        progress_placeholder = st.empty()
        status_placeholder = st.empty()
        
        # Initialize progress bar
        progress_bar = progress_placeholder.progress(0)
        
        # Define status messages
        status_messages = {
            0: "Reading your image...",
            20: "Analyzing Ghibli character...",
            40: "Creating detailed description...",
            60: "Generating human interpretation...",
            80: "Polishing final details..."
        }
        
        # Update progress with fewer steps
        for i in range(0, 101, 5):  # Step by 5 instead of 1
            progress_bar.progress(i)
            
            # Update status message based on progress thresholds
            for threshold, message in status_messages.items():
                if i >= threshold and i < threshold + 20:
                    status_placeholder.markdown(f"<p style='text-align:center; color: #94a3b8 !important;'>{message}</p>", unsafe_allow_html=True)
                    break
            
            # Sleep less for better responsiveness
            time.sleep(0.1)
        
        # Clear status for results
        status_placeholder.empty()
        
        with st.spinner("Finalizing your transformation..."):
            try:
                # Save uploaded file to a temp file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                temp_file.write(uploaded_file.getvalue())
                temp_file.close()
                
                # Initialize the OpenAI client
                openai_client = OpenAIClient(api_key=api_key)
                
                # Transform the image
                result_url = openai_client.deghiblify_image(image_path=temp_file.name)
                
                # Download the result
                result_image = ImageProcessor.download_image_from_url(result_url)
                
                # Display success message
                st.markdown('''
                <div style="background-color: rgba(34, 197, 94, 0.1); border-left: 3px solid #22c55e; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="margin: 0; display: flex; align-items: center; color: #22c55e !important;">
                        <span style="margin-right: 10px; font-size: 1.2rem;">✅</span>
                        Transformation complete!
                    </p>
                </div>
                ''', unsafe_allow_html=True)
                
                # Display the result
                image_card(result_image, caption="AI-Generated Human Version", type="after")
                
                # Add comparison feature
                with st.expander("📊 View Before/After Comparison"):
                    cols = st.columns(2)
                    with cols[0]:
                        st.markdown("<h4 style='text-align: center; color: #3b82f6;'>Original</h4>", unsafe_allow_html=True)
                        st.image(image, use_column_width=True)
                    with cols[1]:
                        st.markdown("<h4 style='text-align: center; color: #8b5cf6;'>Transformed</h4>", unsafe_allow_html=True)
                        st.image(result_image, use_column_width=True)
                
                # Prepare download
                result_bytes = BytesIO()
                result_image.save(result_bytes, format='PNG')
                download_filename = generate_output_filename(uploaded_file.name)
                
                # Container for download button
                download_container = st.container()
                with download_container:
                    st.markdown('''
                    <div style="background-color: #1e293b; border-radius: 12px; padding: 20px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); text-align: center; margin-top: 10px;" class="glow-box">
                        <p style="margin-top: 0; margin-bottom: 15px; font-weight: 500; color: #e2e8f0 !important;">Download your transformed image:</p>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    st.download_button(
                        label="📥 Download Image",
                        data=result_bytes.getvalue(),
                        file_name=download_filename,
                        mime="image/png",
                        key="download_btn"
                    )
                
                # Clean up temp file
                os.unlink(temp_file.name)
                
            except Exception as e:
                error_message = handle_api_error(e)
                st.markdown(f'''
                <div style="background-color: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                    <p style="margin: 0; display: flex; align-items: center; color: #ef4444 !important;">
                        <span style="margin-right: 10px; font-size: 1.2rem;">❌</span>
                        {error_message}
                    </p>
                </div>
                ''', unsafe_allow_html=True)
                
                if DEBUG_MODE:
                    st.exception(e)

# Footer - dark mode
st.markdown('''
<div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #1e293b; 
    border-radius: 12px; backdrop-filter: blur(10px); box-shadow: 0 5px 15px rgba(0,0,0,0.2);" class="glow-box">
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 10px;">
        <div style="width: 40px; height: 2px; background-color: #334155;"></div>
        <span style="color: #3b82f6; font-size: 1.5rem;">✨</span>
        <div style="width: 40px; height: 2px; background-color: #334155;"></div>
    </div>
    <p style="font-size: 0.9rem; margin-bottom: 0; color: #94a3b8 !important;">
        Made with <span style="color: #ef4444;">❤️</span> using 
        <span style="font-weight: 600; color: #3b82f6;">OpenAI</span> and 
        <span style="font-weight: 600; color: #3b82f6;">Streamlit</span>
    </p>
</div>
''', unsafe_allow_html=True)