import os
import base64
from openai import OpenAI
from typing import Optional

class OpenAIClient:
    """Client for interacting with OpenAI APIs."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI client with provided API key or from environment.

        Args:
            api_key (Optional[str]): OpenAI API key. If not provided, it is read from the environment variable 'OPENAI_API_KEY'.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("No API key provided and OPENAI_API_KEY environment variable not set.")
        
        self.client = OpenAI(api_key=self.api_key)

    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode an image file to base64 string.

        Args:
            image_path (str): Path to the image file.
        
        Returns:
            str: Base64-encoded string of the image.
        """
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _get_realistic_description_from_gpt4o(self, base64_image: str) -> str:
        """
        Use GPT-4o to generate a realistic description of the anime character.

        Args:
            base64_image (str): Base64-encoded image string.
        
        Returns:
            str: Realistic character description.
        """
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in character realism transformation. Convert anime-style characters "
                        "into photorealistic versions while preserving key features like face shape, hairstyle, and expression. "
                        "Avoid anime-related language. The goal is to generate a vivid, realistic human description."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Describe how this character would look as a real human. Maintain the same gender, age, hairstyle, "
                                "and outfit details. Avoid mentioning anime or cartoon elements."
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=700
        )
        return response.choices[0].message.content.strip()

    def _generate_dalle_image(self, description: str) -> str:
        """
        Use DALL·E 3 to generate a photorealistic image based on description.

        Args:
            description (str): Humanized character description.
        
        Returns:
            str: URL of the generated image.
        """
        prompt = (
            f"Photorealistic studio portrait of a person: {description}. "
            "The person should resemble the face, hairstyle, and outfit in the reference, "
            "but look like a real human. No anime or fantasy styling."
        )

        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        return response.data[0].url

    def deghiblify_image(self, image_path: str) -> str:
        """
        Transform a Ghibli-style anime character image into a realistic human version.

        Args:
            image_path (str): Path to the input image.
        
        Returns:
            str: URL to the generated realistic portrait.
        """
        base64_image = self._encode_image_to_base64(image_path)
        description = self._get_realistic_description_from_gpt4o(base64_image)
        generated_image_url = self._generate_dalle_image(description)
        return generated_image_url


# Example usage:
# if __name__ == "__main__":
#     client = OpenAIClient(api_key="your-api-key-here")  # or set OPENAI_API_KEY in environment
#     output_url = client.deghiblify_image("image.png")   # Replace with your image path
#     print("✅ Generated Image URL:", output_url)
