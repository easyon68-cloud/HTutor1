import sys
!pip install streamlit
!pip install openai
!pip install reportlab
import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# App title
st.title("Ncert and Cbse class 11th and 12th standard problem solving tutor")

# Subject selector
subject = st.selectbox(
    "Select your subject:",
    ["Physics", "Chemistry", "Mathematics", "Biology", "English"]
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                f"You are an expert NCERT/CBSE tutor for Class 11th and 12th students. "
                f"Answer only from the official NCERT syllabus of {subject}. "
                f"At the end of each answer, include a relevant NCERT chapter name or topic suggestion, "
                f"for example: 'This concept is covered in Class 12 {subject}, Chapter 5 – Magnetism and Matter.' "
                f"Explain everything step-by-step, clearly, and educationally."
            )
        }
    ]

# Display chat history
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# GPT-5 Turbo response function
def get_response():
    response = client.chat.completions.create(
        model="gpt-5-turbo",
        messages=st.session_state.messages
    )
    return response.choices[0].message.content

# User input box
user_input = st.chat_input(f"Ask your {subject} question...")

# Process chat
if user_input:
    # User message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant reply
    assistant_reply = get_response()
    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)

# PDF Export function
def export_chat_to_pdf(messages):
    pdf_buffer = io.BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "NCERT/CBSE Chat Transcript")
    y -= 30
    c.setFont("Helvetica", 11)

    for msg in messages:
        if msg["role"] == "system":
            continue
        role = "You" if msg["role"] == "user" else "Tutor"
        text = f"{role}: {msg['content']}"
        wrapped_text = []
        for line in text.split("\n"):
            while len(line) > 90:
                wrapped_text.append(line[:90])
                line = line[90:]
            wrapped_text.append(line)
        for line in wrapped_text:
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 11)
            c.drawString(50, y, line)
            y -= 15
        y -= 10

    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

# Sidebar PDF download option
st.sidebar.subheader("🧾 Export Options")
if st.sidebar.button("Download Chat as PDF"):
    pdf_file = export_chat_to_pdf(st.session_state.messages)
    st.sidebar.download_button(
        label="📥 Click here to save PDF",
        data=pdf_file,
        file_name="NCERT_Tutor_Chat.pdf",
        mime="application/pdf"
    )
