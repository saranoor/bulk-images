import streamlit as st
import backend

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Image Prompt Studio",
    page_icon="🎨",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'DM Serif Display', serif;
    }

    /* Dark studio feel */
    .stApp {
        background: #0f0f0f;
        color: #e8e0d5;
    }

    /* Chat messages */
    .user-bubble {
        background: #1e1e1e;
        border: 1px solid #333;
        border-radius: 12px 12px 4px 12px;
        padding: 12px 16px;
        margin: 8px 0;
        max-width: 75%;
        margin-left: auto;
        color: #e8e0d5;
        font-size: 0.92rem;
    }
    .assistant-label {
        font-family: 'DM Serif Display', serif;
        color: #c9a86c;
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .image-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 12px;
        margin: 10px 0 20px 0;
    }
    .image-card {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #2a2a2a;
    }
    .prompt-counter {
        font-size: 0.78rem;
        color: #666;
        text-align: right;
        margin-top: 4px;
    }
    /* Input area */
    .stTextArea textarea {
        background: #1a1a1a !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
        color: #e8e0d5 !important;
        font-family: 'DM Sans', sans-serif !important;
    }
    .stButton > button {
        background: #c9a86c !important;
        color: #0f0f0f !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        padding: 0.5rem 1.5rem !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover {
        opacity: 0.85 !important;
    }
    .stButton > button:disabled {
        opacity: 0.4 !important;
    }
    .divider {
        border: none;
        border-top: 1px solid #222;
        margin: 16px 0;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #0a0a0a !important;
        border-right: 1px solid #1e1e1e;
    }
    .session-stat {
        background: #1a1a1a;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 6px 0;
        font-size: 0.85rem;
        color: #999;
    }
    .session-stat span {
        color: #c9a86c;
        font-weight: 500;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = (
        []
    )  # list of {"role": "user"|"assistant", "prompts": [...], "images": [...]}
if "total_images" not in st.session_state:
    st.session_state.total_images = 0
if "generating" not in st.session_state:
    st.session_state.generating = False

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎨 Image Studio")
    st.markdown("---")

    st.markdown("### Settings")
    img_size = st.selectbox(
        "Image size", ["512×512", "768×512", "512×768", "1024×1024"], index=0
    )
    w, h = map(int, img_size.replace("×", "x").split("x"))

    st.markdown("---")
    st.markdown("### Session")
    st.markdown(
        f'<div class="session-stat">Batches generated: <span>{len([m for m in st.session_state.messages if m["role"] == "assistant"])}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="session-stat">Total images: <span>{st.session_state.total_images}</span></div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")
    if st.button("🗑 Clear chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.total_images = 0
        st.rerun()

    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.75rem;color:#444;">Enter 5–10 prompts, one per line. Each prompt generates one image.</p>',
        unsafe_allow_html=True,
    )

# ── Main area ─────────────────────────────────────────────────────────────────
st.markdown("# James Image Prompt Studio")
st.markdown(
    '<p style="color:#666;margin-top:-12px;">Type 5–10 image prompts below and generate them all at once.</p>',
    unsafe_allow_html=True,
)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Chat history ──────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        prompts_display = "\n".join(f"{i+1}. {p}" for i, p in enumerate(msg["prompts"]))
        st.markdown(
            f'<div class="user-bubble">{prompts_display}</div>', unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="assistant-label">✦ Generated Images</div>',
            unsafe_allow_html=True,
        )
        cols = st.columns(min(len(msg["images"]), 4))
        for idx, (img, prompt) in enumerate(zip(msg["images"], msg["prompts"])):
            with cols[idx % 4]:
                if img is not None:
                    st.image(
                        img,
                        caption=prompt[:50] + ("…" if len(prompt) > 50 else ""),
                        use_container_width=True,
                    )
                else:
                    st.error(f"Failed: {prompt[:40]}")
        st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ── Input area ────────────────────────────────────────────────────────────────
st.markdown("### Your prompts")
raw_input = st.text_area(
    label="prompts",
    placeholder="A misty mountain range at golden hour\nA cyberpunk cat in neon-lit alley\nVintage library with floating books\n...",
    height=200,
    label_visibility="collapsed",
)

# Parse and validate
prompts = [p.strip() for p in raw_input.strip().splitlines() if p.strip()]
count = len(prompts)

col_info, col_btn = st.columns([3, 1])
with col_info:
    if count == 0:
        st.markdown(
            '<p class="prompt-counter">Enter 5–10 prompts, one per line</p>',
            unsafe_allow_html=True,
        )
    elif count < 2:
        st.markdown(
            f'<p class="prompt-counter" style="color:#e07070;">{count} prompt{"s" if count!=1 else ""} — need at least 5</p>',
            unsafe_allow_html=True,
        )
    elif count > 10:
        st.markdown(
            f'<p class="prompt-counter" style="color:#e07070;">{count} prompts — max 10 allowed</p>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<p class="prompt-counter" style="color:#7ab87a;">✓ {count} prompts ready</p>',
            unsafe_allow_html=True,
        )

with col_btn:
    can_generate = 2 <= count <= 10 and not st.session_state.generating
    generate_clicked = st.button(
        "✦ Generate", disabled=not can_generate, use_container_width=True
    )

# ── Generation ────────────────────────────────────────────────────────────────
if generate_clicked and can_generate:
    st.session_state.messages.append({"role": "user", "prompts": prompts})
    st.session_state.generating = True

    st.markdown(
        '<div class="assistant-label">✦ Generating…</div>', unsafe_allow_html=True
    )
    progress = st.progress(0, text="Starting…")

    images = []
    for i, prompt in enumerate(prompts):
        progress.progress((i) / count, text=f"Generating {i+1}/{count}: {prompt[:40]}…")
        img = backend.generate_image(
            prompt, filename=f"image_{i}.png", width=w, height=h
        )
        images.append(img)

    progress.progress(1.0, text="Done!")
    progress.empty()

    st.session_state.messages.append(
        {"role": "assistant", "images": images, "prompts": prompts}
    )
    st.session_state.total_images += len([img for img in images if img is not None])
    st.session_state.generating = False
    st.rerun()
