import streamlit as st
from google import genai
from key import TOKEN

try:
    API_KEY = st.secrets["TOKEN"]
except KeyError:
    API_KEY = TOKEN

st.set_page_config(page_title="AI Campaign Generator", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("AI Campaign Generator")
st.write("Fill out the details below to generate a campaign.")

with st.form("campaign_builder"):
    st.subheader("Campaign Builder")
    product_desc = st.text_area("1. Describe your product or event:")
    target_audience = st.text_input("2. Target Audience:")
    platform = st.selectbox("3. Posting Platform:", ["Instagram", "LinkedIn", "Twitter / X", "YouTube", "Facebook"])
    submit_button = st.form_submit_button("Generate Campaign")

if submit_button:
    if not product_desc or not target_audience:
        st.warning("Please fill out the product and audience fields!")
    else:
        combined_prompt = f"Make a {platform} post for this product/event: '{product_desc}'. The target audience is: '{target_audience}'."
        
        st.session_state.messages.append({
            "role": "user", 
            "content": combined_prompt,
            "product": product_desc 
        })

        try:
            client = genai.Client(api_key=API_KEY)
            
            with st.spinner("Writing the caption..."):
                caption_generator = f"Write an engaging {platform} post for: '{product_desc}'. Audience: '{target_audience}'. Include a catchy hook, emojis, and hashtags."
                caption_response = client.models.generate_content(model='gemini-2.5-flash', contents=caption_generator)
                final_caption = caption_response.text
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_caption
            })
            
        except Exception as e:
            st.error(f"Oops, something went wrong: {e}")

st.markdown("---")
st.subheader("Campaign Feed")

if not st.session_state.messages:
    st.info("Your campaigns will appear here.")
else:
    for msg in reversed(st.session_state.messages): 
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])
        elif msg["role"] == "user":
            with st.chat_message("user"):
                st.write(f"*Brief:* {msg['content']}")

st.sidebar.title("Campaign History")
st.sidebar.write("Your recent requests in this session:")
st.sidebar.markdown("---")

if not st.session_state.messages:
    st.sidebar.caption("No campaigns. Fill out the form")
else:
    for i, msg in enumerate(st.session_state.messages):
        if msg["role"] == "user":
            st.sidebar.markdown(f"*Product:* {msg['product'][:25]}...")