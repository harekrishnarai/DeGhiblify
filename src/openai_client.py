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

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.api_key)

    def deghiblify_image(self, image_path: str) -> str:
        """
        Transform a Ghibli-style anime character image into a realistic human version.
        
        Args:
            image_path (str): Path to the image file.
            
        Returns:
            str: URL to the generated photorealistic image.
        """
        # Read and base64-encode the image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode("utf-8")

        # Step 1: Use GPT-4o with vision to describe the character in realistic human terms
        vision_response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in character realism transformation. Your job is to convert anime-style characters "
                        "into their most faithful, photorealistic versions while preserving recognizable features such as face shape, "
                        "hairstyle, and expression. Ensure the description remains natural and suitable for generating realistic portraits "
                        "with DALL·E or similar models. Do not describe the image as anime or cartoon."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Please describe what this anime-style character would look like as a real human. "
                                "Keep the age, gender, hairstyle, and clothing style close to the original. "
                                "Do not use anime-related terms. Provide a realistic, vivid description suitable for photorealistic rendering."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=700
        )

        # Extract character description
        character_description = vision_response.choices[0].message.content.strip()

        # Step 2: Use DALL·E 3 to generate realistic portrait
        dalle_prompt = (
            f"Photorealistic portrait of a person based on this description: {character_description}. "
            "The person should closely resemble the facial structure, hairstyle, and outfit in the reference image, "
            "but rendered as a realistic human in a natural studio portrait. No anime or fantasy elements."
        )

        dalle_response = self.client.images.generate(
            model="dall-e-3",
            prompt=dalle_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        # Return the URL to the generated image
        return dalle_response.data[0].url


# # Example usage:
# if __name__ == "__main__":
#     client = OpenAIClient(api_key="your-api-key-here")  # or set OPENAI_API_KEY in your env
#     output_url = client.deghiblify_image("image.png")   # replace with your image path
#     print("✅ Generated Image URL:", output_url)
