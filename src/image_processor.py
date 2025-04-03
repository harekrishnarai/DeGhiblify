import os
import requests
from PIL import Image
from io import BytesIO
import base64
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import IMAGE_OUTPUT_SIZE

class ImageProcessor:
    @staticmethod
    def load_image(image_path):
        """Load an image from a file path."""
        return Image.open(image_path)
    
    @staticmethod
    def resize_image(image, size=IMAGE_OUTPUT_SIZE):
        """Resize an image to the specified dimensions."""
        return image.resize(size)
    
    @staticmethod
    def save_image(image, output_path):
        """Save an image to the specified path."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        image.save(output_path)
        return output_path
    
    @staticmethod
    def download_image_from_url(url, output_path=None):
        """Download an image from a URL and optionally save it."""
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        
        if output_path:
            return ImageProcessor.save_image(image, output_path)
        return image
    
    @staticmethod
    def image_to_base64(image):
        """Convert a PIL Image to base64 string."""
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    @staticmethod
    def base64_to_image(base64_string):
        """Convert a base64 string to PIL Image."""
        image_data = base64.b64decode(base64_string)
        return Image.open(BytesIO(image_data))