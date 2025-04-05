import os
import base64
import requests
from openai import OpenAI
from typing import Optional

class OpenAIClient:
    """Client for interacting with OpenAI APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI client with provided API key or from environment"""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided and OPENAI_API_KEY environment variable not set")
        
        # Create client with new OpenAI SDK
        self.client = OpenAI(api_key=self.api_key)
    
    def deghiblify_image(self, image_path: str) -> str:
        """
        Transform Ghibli-style anime image to realistic human
        
        Args:
            image_path: Path to the image file
            
        Returns:
            URL to the generated image
        """
        # Read and encode the image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Use GPT-4o (the latest model with vision capabilities)
        vision_response = self.client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert in character realism and visual storytelling. "
                    "Your task is to faithfully transform characters drawn in Studio Ghibli's art style into lifelike human portraits, suitable for realistic generation using DALL-E. "
                    "Focus on capturing the emotional essence, personality, and signature traits of the character while translating anime-style elements (e.g., hair, eyes, facial structure, clothing) into natural human features. "
                    "Be descriptive about age, facial expressions, ethnic appearance, hairstyle, skin texture, clothing material, and atmosphere—while staying true to the original Ghibli aesthetic and mood."
                )
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyze the Studio Ghibli artwork and describe in detail how the character would appear as a realistic human. "
                            "Include defining features necessary to reconstruct the character in photorealistic form with DALL-E. "
                            "Avoid anime-style language; instead, describe the character as a real person someone might meet in the real world. "
                            "Maintain the artistic soul and emotional nuance of the original piece."
                        )
                    },
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}}
                ]
            }
        ],
        max_tokens=700
    )

        
        # Extract the character description
        character_description = vision_response.choices[0].message.content
        
        # Now use DALL-E to generate a realistic version based on the description
        dalle_prompt = f"Create a photorealistic portrait of a human version of this character: {character_description}. Make it look like a high-quality photograph, not anime style."
        
        dalle_response = self.client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        # Return the URL of the generated image
        return dalle_response.data[0].url