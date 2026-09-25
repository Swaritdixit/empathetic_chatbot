import json
import os

import streamlit as st
from groq import Groq


# ============================================================
# Page configuration
# ============================================================
st.set_page_config(
    page_title="Empathetic Chatbot",
    page_icon="💙",
    layout="centered",
)


# ============================================================
# Configuration
# ============================================================
MODEL = "openai/gpt-oss-20b"
EMOTIONS = [
    "joy",
    "sadness",
    "anger",
    "fear",
    "surprise",
    "trust",
    "disgust",
    "anticipation",
]

EMPATHY_INSTRUCTIONS = {
    "joy": "Be warm and positive while matching the user's happiness.",
    "sadness": "Be comforting, validating, gentle, and reassuring.",
    "anger": "Stay calm, validate the frustration, and avoid sounding judgmental.",
    "fear": "Be gentle and reassuring without dismissing the user's concern.",
    "surprise": "Respond with curiosity and understanding.",
    "trust": "Be supportive, friendly, and encouraging.",
    "disgust": "Respond respectfully and calmly without amplifying negativity.",
    "anticipation": "Be encouraging and optimistic while staying realistic.",
}

SYSTEM_PROMPT = """
You are an empathetic conversational assistant.

Your job has two parts:
1. Infer the emotional state expressed by the user's current message.
2. Write one short, natural, empathetic reply.

Important rules:
- Analyze only the current user message.
- Do not claim to be a therapist, doctor, or human.
- Do not diagnose mental-health conditions.
- Do not invent facts about the user.
- Acknowledge the user's feeling before giving advice when appropriate.
- Keep the reply concise: normally 1-3 sentences.
- If the message is casual or neutral, respond naturally rather than forcing an emotional interpretation.
- Emotion scores must be numbers from 0 to 1 and should approximately sum to 1.
""".strip()


# ============================================================
# Secrets / API client
# ============================================================
def get_groq_api_key():
    """Read the Groq API key from Streamlit secrets or an environment variable."""
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            return key
    except Exception:
        pass

    return os.getenv("GROQ_API_KEY")


@st.cache_resource

def get_client():
    key = get_groq_api_key()
    if not key:
        return None
    return Groq(api_key=key)


# ============================================================
# AI inference
# ============================================================
def analyze_and_reply(client, user_message):
    """Return emotion scores, dominant emotion, and an empathetic reply."""
    schema = {
        "type": "object",
        "properties": {
            "emotion_scores": {
                "type": "object",
                "properties": {
                    emotion: {"type": "number"} for emotion in EMOTIONS
                },
                "required": EMOTIONS,
                "additionalProperties": False,
            },
            "dominant_emotion": {
                "type": "string",
                "enum": EMOTIONS,
            },
            "confidence": {
                "type": "number",
            },
            "reply": {
                "type": "string",
            },
        },
        "required": ["emotion_scores", "dominant_emotion", "confidence", "reply"],
        "additionalProperties": False,
    }

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Analyze this message and generate the empathetic reply.\n\n"
                    f"User message: {user_message}\n\n"
                    "Use this response style guidance for the dominant emotion:\n"
                    + "\n".join(
                        f"- {emotion}: {instruction}"
                        for emotion, instruction in EMPATHY_INSTRUCTIONS.items()
                    )
                ),
            },
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "empathetic_chat_response",
                "strict": True,
                "schema": schema,
            },
        },
        max_completion_tokens=400,
        reasoning_effort="low",
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("The model returned an empty response.")

    result = json.loads(content)

    # Defensive cleanup in case a value is slightly outside the expected range.
    scores = {
        emotion: max(0.0, min(1.0, float(result["emotion_scores"].get(emotion, 0.0))))
        for emotion in EMOTIONS
    }

    dominant = result["dominant_emotion"]
    confidence = max(0.0, min(1.0, float(result["confidence"])))
    reply = str(result["reply"]).strip()

    if not reply:
        reply = "I hear you. Thanks for sharing that with me."

    return scores, dominant, confidence, reply


# ============================================================
# UI
# ============================================================
st.title("💙 Empathetic Chatbot")
st.caption("Emotion-aware conversational AI powered by Groq")

with st.sidebar:
    st.header("About")
    st.write(
        "This chatbot analyzes the emotion expressed in the current message "
        "and generates a short response designed to match that emotional context."
    )

    st.divider()
    st.subheader("Detected emotions")
    st.write(", ".join(emotions.title() for emotions in EMOTIONS))

    st.divider()
    st.caption(
        "This is an AI demonstration, not a replacement for professional medical "
        "or mental-health care."
    )

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# Initialize conversation state.
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and "analysis" in message:
            analysis = message["analysis"]
            st.caption(
                f"Detected emotion: **{analysis['dominant'].title()}** "
                f"({analysis['confidence'] * 100:.0f}% confidence)"
            )


# API key check.
client = get_client()
if client is None:
    st.info(
        "Add your `GROQ_API_KEY` in Streamlit Cloud → Advanced settings → "
        "Secrets, then reload the app."
    )


# Chat input.
user_message = st.chat_input("Tell me how you're feeling...")

if user_message:
    user_message = user_message.strip()

    if not user_message:
        st.stop()

    if len(user_message) > 4000:
        st.error("Please keep your message under 4000 characters.")
        st.stop()

    if client is None:
        st.error("Groq API key is not configured yet.")
        st.stop()

    st.session_state.messages.append(
        {"role": "user", "content": user_message}
    )

    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("Understanding your message..."):
            try:
                scores, dominant, confidence, reply = analyze_and_reply(
                    client, user_message
                )

                st.markdown(reply)
                st.caption(
                    f"Detected emotion: **{dominant.title()}** "
                    f"({confidence * 100:.0f}% confidence)"
                )

                with st.expander("Emotion analysis"):
                    for emotion in sorted(
                        scores, key=scores.get, reverse=True
                    ):
                        st.write(f"**{emotion.title()}** — {scores[emotion]:.2f}")
                        st.progress(int(scores[emotion] * 100))

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": reply,
                        "analysis": {
                            "dominant": dominant,
                            "confidence": confidence,
                            "scores": scores,
                        },
                    }
                )

            except Exception as exc:
                error_message = str(exc)
                st.error(
                    "I couldn't process that message right now. "
                    "Please try again in a moment."
                )
                with st.expander("Technical details"):
                    st.code(error_message)
