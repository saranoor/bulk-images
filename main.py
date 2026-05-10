import os
import time
from xml.parsers.expat import model

# import google.generativeai as genai
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# Configure your API Key
client = genai.Client(api_key="AIzaSyBHoSzmOnbi-KI3CRe4gsHFpzpVXMJA2Vw")


def generate_image(
    prompt: str,
    filename: str,
    width: int = 1024,  # Gemini/Imagen usually prefers 1024x1024
    height: int = 1024,
    model_name: str = "imagen-3.0-generate-001",
    aspect_ratio: str = "1:1",
    retries: int = 1,
) -> Image.Image | None:
    """
    Generate an image using Google Gemini (Imagen) with an avatar reference.
    """

    # Load the avatar image
    avatar_image = "avatar.jpeg"
    try:
        print(f"[backend] Loading avatar image from {avatar_image}...")
        avatar_img = Image.open(avatar_image)
    except FileNotFoundError:
        print(f"[backend] Error: {avatar_image} not found.")
        return None

    for attempt in range(1, retries + 1):
        try:
            print(f"[backend] Attempt {attempt} to generate image with Gemini...")
            response = client.models.generate_content(
                model="gemini-3.1-flash-image-preview",
                contents=[prompt, avatar_img],
            )

            print("Processing response...")
            for part in response.parts:
                if part.text is not None:
                    print("[backend] Received text part from Gemini:")
                    print(part.text)
                elif part.inline_data is not None:
                    image = part.as_image()
                    image.save(f"{filename}")
                    return part.inline_data.data

        except Exception as e:
            print(f"[backend] Error on attempt {attempt}: {e}")
            if attempt < retries:
                time.sleep(2)
            else:
                return None

    return None


def generate_images_batch(
    prompts: list[str],
    width: int = 1024,
    height: int = 1024,
    progress_callback=None,
) -> list[Image.Image | None]:
    """
    Generate images for a list of prompts sequentially using Gemini.
    """
    results = []
    for i, prompt in enumerate(prompts):
        if progress_callback:
            print(
                f"[backend] Progress callback for prompt {i+1}/{len(prompts)}: {prompt[:40]}..."
            )
            progress_callback(i, len(prompts), prompt)
        fname = f"generated_{i}.png"
        img = generate_image(prompt, filename=fname, width=width, height=height)
        results.append(img)
    return results


# generate_image(
#     prompt="Create a 9:16 vertical image at 1080 x 1920 pixels. The character in the attached avatar image: with a worried and overwhelmed expression. Show the character staring at a large glowing green buy button while chaotic price candles rise around it. The buy button is the main focal point. Dark background color. The drawing has a pencil or crayon texture, with slightly rough, sketchy lines. Minimalist. High contrast. Clean composition. No clutter. Strong visual hierarchy.",
#     filename="image_0.png",
# )
