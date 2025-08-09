import streamlit as st
import fitz  # PyMuPDF
import google.generativeai as genai
import os

# ------------------- CONFIG -------------------
# Load your Google API key from environment variable or Streamlit secrets
API_KEY = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else os.getenv("GEMINI_API_KEY")
if not API_KEY:
    st.error("Google API key not found. Please set it in Streamlit secrets or environment variable.")
    st.stop()

# Configure Gemini API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

# ------------------- FUNCTIONS -------------------

def extract_text_from_pdf(file):
    text = ""
    pdf_doc = fitz.open(stream=file.read(), filetype="pdf")
    for page in pdf_doc:
        text += page.get_text("text") + "\n"
    return text.strip()

def chat_with_gemini(prompt, history):
    # Combine history and new prompt
    conversation = "\n".join(history + [f"User: {prompt}"])
    response = model.generate_content(conversation)
    return response.text

# ------------------- STREAMLIT UI -------------------
st.set_page_config(page_title="PDF Chat with Gemini", layout="wide")
st.title("📄 PDF Chat with Gemini")

if "history" not in st.session_state:
    st.session_state.history = []

uploaded_pdf = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_pdf:
    pdf_text = extract_text_from_pdf(uploaded_pdf)
    st.subheader("Extracted PDF Text")
    with st.expander("Show PDF Text"):
        st.write(pdf_text)

    user_input = st.text_area("Ask a question about the PDF")

    if st.button("Send") and user_input:
        answer = chat_with_gemini(pdf_text + "\n\n" + user_input, st.session_state.history)
        st.session_state.history.append(f"User: {user_input}")
        st.session_state.history.append(f"Gemini: {answer}")

for msg in st.session_state.history:
    if msg.startswith("User:"):
        st.markdown(f"**{msg}**")
    else:
        st.write(msg)