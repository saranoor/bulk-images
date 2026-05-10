import streamlit as st
from PIL import Image, ImageDraw
import io

st.set_page_config(page_title="Bulk Image Prompt Generator", layout="wide")

st.title("🖼️ Bulk Image Prompt Generator")
st.write("Paste multiple image prompts (one per line), then click **Generate Images**.")

prompts_text = st.text_area(
    "Image Prompts",
    placeholder="Image prompt 1...\nImage prompt 2...\nImage prompt 3...",
    height=200,
)

if st.button("Generate Images", type="primary"):
    prompts = [p.strip() for p in prompts_text.splitlines() if p.strip()]

    if not prompts:
        st.warning("Please enter at least one prompt.")
    else:
        progress = st.progress(0)
        status = st.empty()

        cols = st.columns(2)
        for i, prompt in enumerate(prompts):
            status.write(f"Generating image {i+1} of {len(prompts)}...")

            # Placeholder demo image (replace with your Python image-generation script/API call)
            img = Image.new("RGB", (768, 512), color="white")
            d = ImageDraw.Draw(img)
            d.text((20, 20), prompt[:100], fill="black")

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()

            with cols[i % 2]:
                st.image(img_bytes, caption=prompt, use_container_width=True)
                st.download_button(
                    label=f"Download Image {i+1}",
                    data=img_bytes,
                    file_name=f"generated_image_{i+1}.png",
                    mime="image/png",
                )

            progress.progress((i + 1) / len(prompts))

        status.success("All images generated successfully!")

st.markdown("---")
st.caption(
    "Client access: once deployed, open the app link in any browser and paste prompts to generate images."
)
