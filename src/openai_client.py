import os
import base64
from openai import OpenAI
from typing import Optional

class OpenAIClient:
    """Client for interacting with OpenAI APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI client with provided API key or from environment"""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided and OPENAI_API_KEY environment variable not set")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def deghiblify_image(self, image_path: str) -> str:
        """
        Transform Ghibli-style anime image into a realistic human photo
        
        Args:
            image_path: Path to the input image file
            
        Returns:
            URL of the generated photorealistic image
        """
        # Encode image as base64
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Step 1: Generate realistic description using GPT-4o with image input
        vision_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a visual realism expert. Your job is to help artists translate anime-style characters "
                        "into realistic human forms. Focus on humanizing the visual traits of the character while keeping their emotional tone. "
                        "Avoid anime tropes or exaggeration. Describe them like a person you’d see in real life."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "This character was illustrated in a Studio Ghibli-like anime art style. "
                                "Please describe in natural, photorealistic terms what they would look like as a real human: "
                                "their skin tone, hairstyle, age, ethnicity, clothing, facial features, and expression. "
                                "Avoid any cartoon or anime language. I want to recreate this person using a realistic image model."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=700
        )
        
        # Extract and clean up GPT-generated description
        character_description = vision_response.choices[0].message.content.strip()

        # Step 2: Use DALL·E to generate the photorealistic human image
        dalle_prompt = (
            f"Create a high-quality, photorealistic portrait of a real human based on this description: {character_description}. "
            "Make it look like a professional studio photograph. No anime or cartoon elements. Real lighting, textures, eyes, and skin."
        )

        dalle_response = self.client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        return dalle_response.data[0].url
