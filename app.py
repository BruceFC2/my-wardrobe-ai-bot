import streamlit as st
import google.generativeai as genai
import json
from datetime import datetime

# Configure your Gemini API Key
# In production, secure this via Streamlit Secrets (st.secrets["GEMINI_API_KEY"])
genai.configure(api_key="YOUR_GEMINI_API_KEY")

st.set_page_config(page_title="AI Wardrobe Rotator", page_icon="👔", layout="centered")

# Initialize your exact wardrobe in the app's memory (Session State)
if "wardrobe" not in st.session_state:
    st.session_state.wardrobe = {
        "tops": ["White tee", "Black tee", "Grey polo", "Short sleeve button-neck 1", "Short sleeve button-neck 2", "Big white vest", "Medium vest 1", "Medium vest 2", "Singlet 1", "Singlet 2", "Singlet 3", "Singlet 4", "White shirt 1", "White shirt 2", "White shirt 3"],
        "bottoms": ["Cargo shorts", "Black Trousers 1", "Black Trousers 2", "White Joggers", "Black Joggers", "Milk Shorts", "Short short"],
        "traditional": ["Senator attire", "Short sleeve senator attire"],
        "outerwear": ["Jersey"],
        "shoes": ["Black shoes 1", "Black shoes 2", "Slides 1", "Slides 2"],
        "accessories": ["Belt", "Black cap", "Smart watch", "Chrome heart glasses"],
        "undergarments": ["Boxers 1", "Boxers 2", "Boxers 3", "Boxers 4", "Socks 1", "Socks 2", "Socks 3"]
    }

# Track history to manage rotation
if "history" not in st.session_state:
    st.session_state.history = []

st.title("👔 My AI Wardrobe Rotator")
st.write("Input your vibe, and let the bot pull the perfect rotation from your clean clothes.")

---

# UI Section 1: Daily Inputs
st.subheader("1. What's the Move Today?")
occasion = st.text_input("Occasion / Activity", placeholder="e.g., Studying at home, Exam hall tomorrow, Casual hangout...")
vibe = st.text_input("Vibe Preference (Optional)", placeholder="e.g., Ultra-comfortable, sharp, stealth wealth...")

# UI Section 2: Quick Inventory Check (To exclude items in the laundry)
with st.expander("🧺 Manage Clean Inventory (Uncheck if in the laundry)"):
    st.write("The bot will only pick checked items.")
    available_inventory = {}
    
    for category, items in st.session_state.wardrobe.items():
        st.markdown(f"**{category.title()}**")
        available_inventory[category] = []
        # Display items as checkboxes side-by-side
        cols = st.columns(3)
        for idx, item in enumerate(items):
            col = cols[idx % 3]
            is_clean = col.checkbox(item, value=True, key=f"chk_{item}")
            if is_clean:
                available_inventory[category].append(item)

---

# UI Section 3: The Generator Engine
if st.button("🔄 Spin Wardrobe & Pick Outfit", type="primary"):
    if not occasion:
        st.warning("Please tell the bot what the occasion is first!")
    else:
        with st.spinner("Styling your look..."):
            # Construct the AI system prompt dynamically
            prompt = f"""
            You are a brilliant, personal stylist bot. Your job is to pick exactly ONE cohesive outfit combination from the user's available clean items.
            
            Context for Today:
            - Occasion: {occasion}
            - Vibe: {vibe if vibe else 'Balanced'}
            
            Available Clean Inventory JSON:
            {json.dumps(available_inventory, indent=2)}
            
            Recent Outfit History (Avoid picking these exact combos if possible to maintain rotation):
            {json.dumps(st.session_state.history[-3:], indent=2)}
            
            Rules:
            1. You can ONLY pick items that exist in the clean inventory JSON list above.
            2. Output your response beautifully using Markdown. 
            3. Break it down by: Top, Bottom, Shoes, Accessories, and Undergarments (if applicable).
            4. Provide a 2-sentence explanation of *why* this works perfectly for the occasion.
            """
            
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                
                st.subheader("✨ Tonight's Pick")
                st.markdown(response.text)
                
                # Save to history to help rotation for the next spin
                st.session_state.history.append({"date": str(datetime.now().date()), "occasion": occasion})
                
            except Exception as e:
                st.error(f"Error connecting to AI engine: {e}")