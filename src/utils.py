import os
import tempfile
from datetime import datetime

def load_env_variables():
    """Load environment variables from the .env file."""
    from dotenv import load_dotenv

    load_dotenv()

    return {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    }

def display_message(message):
    """Display a message in the Streamlit app."""
    import streamlit as st
    st.write(message)

def is_valid_image_file(file_path):
    """Check if a file is a valid image based on its extension."""
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
    file_ext = os.path.splitext(file_path)[1].lower()
    return file_ext in valid_extensions

def create_temp_file(file_content, suffix=".jpg"):
    """Create a temporary file with the given content."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.write(file_content)
    temp_file.close()
    return temp_file.name

def get_timestamp():
    """Get a formatted timestamp for file naming."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def generate_output_filename(original_filename=None, prefix="deghiblified"):
    """Generate a filename for the output image."""
    timestamp = get_timestamp()
    
    if original_filename:
        base_name, ext = os.path.splitext(os.path.basename(original_filename))
        return f"{prefix}_{base_name}_{timestamp}{ext}"
    
    return f"{prefix}_{timestamp}.jpg"

def handle_api_error(error):
    """Handle API errors with user-friendly messages."""
    error_str = str(error)
    
    if "API key" in error_str.lower():
        return "Invalid OpenAI API key. Please check your settings."
    elif "billing" in error_str.lower():
        return "OpenAI billing issue. Please check your OpenAI account."
    elif "rate limit" in error_str.lower():
        return "Rate limit exceeded. Please try again later."
    else:
        return f"An error occurred: {error_str}"