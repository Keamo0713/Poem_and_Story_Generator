import streamlit as st
import json
import os
from datetime import datetime
from utils.api_handler import generate_story
from utils.validation import validate_inputs
from fpdf import FPDF

# Ensure directories exist
os.makedirs("outputs/generated_text", exist_ok=True)
os.makedirs("outputs/generated_pdf", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Stars Animation Function
def show_stars():
    stars_html = """
    <div id="stars-container" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 9999;"></div>
    <script>
        function createStar() {
            const container = document.getElementById('stars-container');
            const star = document.createElement('div');
            
            // Random size between 2px and 5px
            const size = Math.random() * 3 + 2;
            star.style.width = `${size}px`;
            star.style.height = `${size}px`;
            star.style.backgroundColor = '#d4af37';
            star.style.borderRadius = '50%';
            star.style.position = 'absolute';
            
            // Random starting position
            star.style.left = `${Math.random() * 100}%`;
            star.style.top = `-10px`;
            
            // Random animation duration
            const duration = Math.random() * 3 + 2;
            star.style.animation = `fall ${duration}s linear infinite`;
            
            // Add keyframes dynamically
            const style = document.createElement('style');
            style.innerHTML = `
                @keyframes fall {
                    to {
                        transform: translateY(100vh);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
            
            container.appendChild(star);
            
            // Remove star after animation completes
            setTimeout(() => {
                star.remove();
                style.remove();
            }, duration * 1000);
        }
        
        // Create stars periodically
        setInterval(createStar, 100);
        
        // Initial stars
        for (let i = 0; i < 50; i++) {
            setTimeout(createStar, i * 100);
        }
    </script>
    """
    st.components.v1.html(stars_html, height=0)

# Page Configuration
st.set_page_config(
    page_title="Poem and Storycraft | AI-Powered Story Crafting Suite",
    layout="centered",
    page_icon="✒️",
    initial_sidebar_state="expanded"
)

# Custom PDF Generator
def create_pdf(content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=12)
    
    # Title
    pdf.set_font("Times", 'B', 16)
    pdf.cell(200, 10, txt="Your Literary Masterpiece", ln=True, align='C')
    pdf.ln(10)
    
    # Metadata
    pdf.set_font("Times", 'I', 12)
    pdf.cell(200, 10, txt=f"Protagonist: {protagonist}", ln=True)
    pdf.cell(200, 10, txt=f"Setting: {setting}", ln=True)
    pdf.cell(200, 10, txt=f"Type: {creation_type} | Genre: {genre} | Tone: {tone}", ln=True)
    pdf.ln(15)
    
    # Content
    pdf.set_font("Times", size=12)
    pdf.multi_cell(0, 10, txt=content)
    
    filepath = os.path.join("outputs", "generated_pdf", filename)
    pdf.output(filepath)
    return filepath

# Custom CSS with Background Image
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Montserrat:wght@300;400&display=swap');
    
    .stApp {
        background: linear-gradient(rgba(249, 245, 255, 0.85), rgba(240, 247, 255, 0.85)), 
                    url('https://images.unsplash.com/photo-1535905557558-afc4877a26fc?ixlib=rb-4.0.3&auto=format&fit=crop&w=1887&q=80');
        background-size: cover;
        background-attachment: fixed;
        background-position: center;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border: 1px solid #d4af37 !important;
        border-radius: 8px !important;
    }
    .stSelectbox>div>div>select {
        background-color: rgba(255, 255, 255, 0.9) !important;
    }
    .stRadio>div {
        background-color: rgba(255, 255, 255, 0.7) !important;
        border-radius: 10px;
        padding: 10px;
    }
    h1, h2, h3 {
        color: #3a2c1e !important;
        font-family: 'Playfair Display' !important;
    }
    .download-btn {
        background: linear-gradient(90deg, #5a4a3a 0%, #3a2c1e 100%) !important;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.title("✒️ Poem and Storycraft")
st.markdown("""
<div style="border-bottom: 1px solid #e0d6c2; margin-bottom: 2rem;"></div>
""", unsafe_allow_html=True)

# Load Prompts
def load_prompts():
    try:
        with open("prompts/story_prompts.json", "r") as f:
            prompts = json.load(f)
        
        # Ensure Poetry prompt exists
        if "Poetry" not in prompts:
            prompts["Poetry"] = {
                "default": "Compose a {tone} poem about {protagonist} in {setting}. Use {narrator} perspective. {special_requirement}",
                "romantic": "Write a romantic poem about {protagonist}'s longing in {setting}. Use vivid imagery and emotional language.",
                "epic": "Create an epic poem chronicling {protagonist}'s journey through {setting}. Use grand, heroic language."
            }
        return prompts
    except Exception as e:
        st.error(f"Error loading prompts: {e}")
        return {}

story_prompts = load_prompts()

# Creation Type Selection
creation_type = st.radio(
    "📝 What would you like to create?",
    ["Story", "Poem"],
    horizontal=True,
    index=0
)

# Main Input Form
with st.form("creation_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        if creation_type == "Poem":
            genre = st.selectbox(
                "🎼 Poem Style",
                ["default", "romantic", "epic", "haiku", "sonnet"],
                help="Select your preferred poetry style"
            )
        else:
            genre = st.selectbox(
                "📜 Story Genre",
                [g for g in story_prompts.keys() if g != "Poetry"],
                help="Select your story genre"
            )
        
        tone = st.selectbox(
            "🎭 Tone",
            ["Whimsical", "Dark", "Romantic", "Suspenseful", "Humorous", "Epic"],
            index=0
        )
    
    with col2:
        protagonist = st.text_input(
            "👑 Protagonist",
            placeholder="e.g., Lady Seraphina",
            help="Main character of your creation"
        )
        
        setting = st.text_input(
            "🌌 Setting",
            placeholder="e.g., A moonlit Venetian palazzo",
            help="Where your creation takes place"
        )
    
    narrator_type = st.selectbox(
        "🗣️ Narrative Perspective",
        ["First Person", "Second Person", "Third Person"],
        index=2
    )
    
    special_req = st.text_area(
        "💎 Special Requirements (Optional)",
        height=100,
        placeholder="Specific requests for your creation..."
    )
    
    submit_button = st.form_submit_button("✨ Craft My Masterpiece")

# Generation Logic
if submit_button and validate_inputs(protagonist, setting):
    with st.status("🔮 Creating your masterpiece...", expanded=True):
        # Get the appropriate prompt template
        if creation_type == "Poem":
            prompt_template = story_prompts["Poetry"].get(genre, story_prompts["Poetry"]["default"])
        else:
            prompt_template = story_prompts.get(genre, "Write a {tone} story about {protagonist} in {setting}")
        
        if isinstance(prompt_template, dict):
            prompt_template = prompt_template.get(tone.lower(), prompt_template["default"])
        
        prompt = prompt_template.format(
            protagonist=protagonist,
            setting=setting,
            tone=tone,
            narrator=narrator_type,
            special_requirement=special_req or ""
        )
        
        output = generate_story(prompt)
        
        if output:
            st.success("🎉 Your creation is ready!")
            show_stars()
            
            # Display output
            st.markdown(f"""
            <div style="
                background-color: rgba(255, 250, 243, 0.9);
                border-left: 4px solid #d4af37;
                padding: 1.5rem;
                border-radius: 0 8px 8px 0;
                margin: 1rem 0;
            ">
                {output}
            </div>
            """, unsafe_allow_html=True)
            
            # Save and download functionality
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{creation_type}_{genre}_{timestamp}"
            
            # Save text file
            text_path = f"outputs/generated_text/{filename}.txt"
            with open(text_path, "w") as f:
                f.write(output)
            
            # Create PDF
            pdf_path = create_pdf(output, f"{filename}.pdf")
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                with open(text_path, "rb") as f:
                    st.download_button(
                        "📥 Download Text",
                        f,
                        file_name=f"{filename}.txt",
                        use_container_width=True,
                        key="text_download"
                    )
            with col2:
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📥 Download PDF",
                        f,
                        file_name=f"{filename}.pdf",
                        use_container_width=True,
                        key="pdf_download"
                    )
            
            # Log the creation
            log_entry = f"{timestamp} | {creation_type} | {genre} | {tone}\n"
            with open("logs/creations.log", "a") as f:
                f.write(log_entry)

# Archive Section
with st.expander("📚 Creation Archive"):
    if os.path.exists("logs/creations.log"):
        with open("logs/creations.log", "r") as f:
            st.text(f.read())
    else:
        st.info("No creations archived yet")

# Footer
st.markdown("""
<div style="border-top: 1px solid #e0d6c2; margin-top: 2rem; padding-top: 1rem; text-align: center; font-family: 'Montserrat'; color: #5a4a3a;">
    Poem and Storycraft ✒️ | Crafted with ♥ for elite storytellers and poets by Keamogetsoe Sele
</div>
""", unsafe_allow_html=True)