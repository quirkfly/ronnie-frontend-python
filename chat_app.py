import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Job Assistant", page_icon="🤖", layout="wide")
st.title("🤖 AI Job Hunting Assistant")

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "uploaded_resume_name" not in st.session_state:
    st.session_state["uploaded_resume_name"] = None

if "profile" not in st.session_state:
    st.session_state["profile"] = None

# ---- Upload resume ----
st.header("📄 Upload your LinkedIn PDF resume (optional)")
uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    # Only call upload_profile if the file is different from previously uploaded
    if st.session_state["uploaded_resume_name"] != uploaded_file.name:
        with st.spinner("Uploading and parsing your resume..."):
            response = requests.post(
                f"{API_URL}/upload_profile",
                files={'file': (uploaded_file.name, uploaded_file.getvalue(), 'application/pdf')}
            )
        if response.ok:
            profile = response.json().get("profile", {})
            st.session_state["uploaded_resume_name"] = uploaded_file.name
            st.session_state["profile"] = profile
            st.success("✅ Resume parsed successfully!")
        else:
            st.error("❌ Failed to upload or parse resume.")
    else:
        # Resume already uploaded, show success and profile
        st.success("✅ Resume already uploaded.")
        if st.session_state["profile"]:
            with st.expander("📋 View extracted profile JSON"):
                st.json(st.session_state["profile"])

# ---- Chat ----
st.header("💬 Chat with your AI assistant")

# Show chat history
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(f"🧑‍💻 **You:** {msg['content']}")
    else:
        st.markdown(f"🤖 **AI:** {msg['content']}")

query = st.text_input("Type your question about jobs:")
top_k = st.slider("Number of jobs to consider (top_k):", min_value=1, max_value=10, value=3)

col1, col2 = st.columns([1,1])

with col1:
    if st.button("Send"):
        if query.strip():
            # Add user message to history
            st.session_state["messages"].append({"role": "user", "content": query})

            # Send chat history and top_k to backend chat endpoint
            payload = {"history": st.session_state["messages"], "top_k": top_k}
            st.write("DEBUG payload:", json.dumps(payload, indent=2))
            resp = requests.post(f"{API_URL}/chat", json=payload)

            if resp.ok:
                data = resp.json()
                ai_reply = data.get("answer", "Sorry, I didn't get a response.")

                # Add AI reply to history
                st.session_state["messages"].append({"role": "assistant", "content": ai_reply})

                st.rerun()  # refresh to show new messages
            else:
                st.error(f"❌ Failed to get answer from AI. Status code: {resp.status_code}")
        else:
            st.warning("Please enter a question.")

with col2:
    if st.button("🧹 Clear chat"):
        st.session_state["messages"] = []
        st.experimental_rerun()

st.caption("Built with Streamlit + FastAPI + OpenAI ✨")
