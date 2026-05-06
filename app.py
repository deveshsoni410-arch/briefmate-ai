import os

import streamlit as st
from google import genai


APP_TITLE = "BriefMate AI (Beta)"
MODEL_NAME = "gemini-2.5-flash-lite"


def get_api_key() -> str | None:
    """Read the API key from Streamlit secrets first, then the shell environment."""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    try:
        return st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY", api_key)
    except Exception:
        return api_key


@st.cache_resource
def get_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def run_prompt(client: genai.Client, prompt: str) -> str:
    response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
    return response.text or "No response generated."


st.set_page_config(page_title="Legal AI Assistant", page_icon=":scroll:", layout="centered")

st.title(APP_TITLE)
st.caption(
    "For legal research assistance only. This is not legal advice; consult a qualified lawyer before acting on it."
)

api_key = get_api_key()
if api_key and api_key.strip() in {"paste-your-google-api-key-here", "paste-your-gemini-api-key-here"}:
    api_key = None

if not api_key:
    st.warning(
        "Add your Gemini API key as GOOGLE_API_KEY in Streamlit secrets or your environment before generating responses."
    )
    st.stop()

client = get_client(api_key)

username = st.text_input("Enter your name")
if username:
    st.caption(f"Welcome, {username}.")

st.divider()

st.subheader("Legal Research")
query = st.text_input("Ask your legal question")

if st.button("Get Answer", type="primary"):
    if not query.strip():
        st.error("Please enter a legal question.")
    else:
        prompt = f"""
You are a legal research assistant for Indian law.

Answer with:
- Relevant law
- Case laws, if available
- A simple explanation
- A short caution if jurisdiction-specific advice is needed

Question:
{query}
"""
        with st.spinner("Researching..."):
            try:
                st.write(run_prompt(client, prompt))
            except Exception as exc:
                st.error(f"Could not generate an answer: {exc}")

st.divider()

st.subheader("Case Brief Generator")
case_text = st.text_area("Paste case or topic", height=180)

if st.button("Generate Brief"):
    if not case_text.strip():
        st.error("Please paste a case, judgment excerpt, or topic.")
    else:
        prompt = f"""
Create a legal case brief in Indian legal style.

Use these headings:
- Facts
- Issues
- Arguments, if identifiable
- Judgment
- Ratio decidendi
- Key takeaway

Text:
{case_text}
"""
        with st.spinner("Preparing brief..."):
            try:
                st.write(run_prompt(client, prompt))
            except Exception as exc:
                st.error(f"Could not generate a brief: {exc}")

st.divider()

st.subheader("Drafting")
draft_type = st.selectbox("Select draft", ["Petition", "Legal Notice"])
facts = st.text_area("Enter facts", height=180)

if st.button("Generate Draft"):
    if not facts.strip():
        st.error("Please enter the facts for the draft.")
    else:
        prompt = f"""
Draft a {draft_type} in Indian legal format.

Requirements:
- Use formal legal language
- Keep placeholders for court, parties, dates, addresses, and advocate details
- Organize the facts clearly
- Include prayer/relief for a petition or demand/response deadline for a legal notice

Facts:
{facts}
"""
        with st.spinner("Drafting..."):
            try:
                st.write(run_prompt(client, prompt))
            except Exception as exc:
                st.error(f"Could not generate a draft: {exc}")
