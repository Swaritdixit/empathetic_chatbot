# 💙 Empathetic Chatbot

An emotion-aware conversational AI application that analyzes the emotional state expressed in a user's message and generates a short, context-aware empathetic response.

The application uses **Groq's API with `openai/gpt-oss-20b`** to perform emotion analysis and response generation through a structured JSON response.

🔗 **Live Demo:** https://empatheticchatbot-kuytrk9wk2eqqgr3nk9nmh.streamlit.app/

---

## ✨ Features

### 💬 Empathetic Conversation

- Natural conversational interface
- Short, context-aware responses
- Maintains conversation history during the session
- Streamlit chat interface
- Clear conversation functionality

### 🧠 Emotion Detection

The chatbot analyzes the emotion expressed in the user's current message.

It supports eight primary emotions:

- Joy
- Sadness
- Anger
- Fear
- Surprise
- Trust
- Disgust
- Anticipation

For every message, the system produces:

- Emotion scores
- Dominant emotion
- Confidence score
- Empathetic response

---

### 📊 Emotion Analysis

Users can expand the **Emotion Analysis** section to view the model's estimated score for each emotion.

Example:

```text
Joy          0.05
Sadness      0.72
Anger        0.08
Fear         0.10
Surprise     0.01
Trust        0.02
Disgust      0.01
Anticipation 0.01
```

The dominant emotion is displayed together with the model's confidence.

---

### 🎯 Emotion-Aware Response Generation

The response style is adapted according to the detected dominant emotion.

```text
Detected Emotion
       │
       ▼
Emotion-Specific Guidance
       │
       ▼
LLM Response Generation
       │
       ▼
Empathetic Reply
```

Examples of response behavior:

| Emotion | Response Style |
|---|---|
| Joy | Warm and positive |
| Sadness | Comforting and reassuring |
| Anger | Calm and validating |
| Fear | Gentle and reassuring |
| Surprise | Curious and understanding |
| Trust | Supportive and encouraging |
| Disgust | Respectful and calm |
| Anticipation | Encouraging and realistic |

---

## 🧠 How It Works

The application uses a single structured LLM inference pipeline.

```text
                User Message
                     │
                     ▼
             Streamlit Interface
                     │
                     ▼
             Groq API Request
                     │
                     ▼
          openai/gpt-oss-20b
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
   Emotion Analysis       Response Generation
          │                     │
          ├── Emotion Scores    │
          ├── Dominant Emotion  │
          └── Confidence        │
                                │
          └──────────┬──────────┘
                     ▼
              Structured JSON
                     │
                     ▼
             Streamlit UI
```

The model is instructed to analyze **only the current user message** rather than making assumptions about the user's background or previous messages.

---

## 🔬 Structured Model Output

Instead of relying on free-form model output, the application requests a structured JSON response.

The expected schema contains:

```json
{
  "emotion_scores": {
    "joy": 0.0,
    "sadness": 0.0,
    "anger": 0.0,
    "fear": 0.0,
    "surprise": 0.0,
    "trust": 0.0,
    "disgust": 0.0,
    "anticipation": 0.0
  },
  "dominant_emotion": "sadness",
  "confidence": 0.85,
  "reply": "I understand that this feels difficult. I'm glad you shared it."
}
```

This makes the output easier for the application to validate and display.

---

## 🛡️ Defensive Output Handling

The application performs additional validation after receiving the model response.

Emotion scores and confidence values are constrained to the range:

```text
0.0 ≤ value ≤ 1.0
```

The application also checks for:

- Empty model responses
- Missing emotion values
- Invalid confidence values
- Empty generated replies

This reduces the chance of malformed model output breaking the application.

---

## 🔐 API Key Management

The Groq API key is **not hardcoded into the application**.

The application first attempts to read:

```text
GROQ_API_KEY
```

from Streamlit Secrets and falls back to an environment variable when running locally.

For Streamlit Cloud:

```text
Streamlit Cloud
      │
      ▼
Advanced Settings
      │
      ▼
Secrets
      │
      ▼
GROQ_API_KEY
```

API credentials should never be committed to GitHub.

---

## 💬 Conversation State

Conversation history is maintained using Streamlit session state.

```text
User Message
     │
     ▼
st.session_state.messages
     │
     ▼
Chat History
     │
     ▼
Streamlit Chat Interface
```

The **Clear Conversation** button removes the current session's stored messages.

The conversation is session-based and is not persisted to a database.

---

## 🧩 Prompt Design

The system prompt establishes several behavioral constraints for the chatbot.

The model is instructed to:

- Analyze the current message
- Identify the emotional state
- Generate a short empathetic response
- Avoid diagnosing mental-health conditions
- Avoid claiming to be a therapist or doctor
- Avoid inventing facts about the user
- Acknowledge feelings before giving advice when appropriate
- Keep responses concise
- Avoid forcing an emotional interpretation on neutral messages

This prompt-based design helps separate **emotion analysis** from the style of the generated response.

---

## 🏗️ Project Structure

```text
empathetic_chatbot/
│
├── app.py
│
├── DailyDialog/
│   ├── train.csv
│   ├── validation.csv
│   ├── test.csv
│   └── combined_plutchik_emotion_dataset.csv
│
├── EmpatheticDialogues/
│   ├── train.csv
│   ├── valid.csv
│   └── test.csv
│
├── MELD/
│   ├── train_sent_emo.csv
│   ├── dev_sent_emo.csv
│   └── test_sent_emo.csv
│
├── plutchik_primary_multi_emotion_dataset.csv
│
├── Untitled.ipynb
├── requirements.txt
├── package.json
├── package-lock.json
└── README.md
```

> `node_modules/` should not be committed to the repository and is omitted from the project structure above.

---

## 📚 Datasets

The repository contains multiple conversational emotion datasets used during experimentation and development.

### DailyDialog

A conversational dataset containing dialogue examples with emotion-related annotations.

### EmpatheticDialogues

A dataset focused on conversations involving empathetic responses and emotional situations.

### MELD

A multimodal emotion recognition dataset derived from conversational interactions, with emotion annotations.

### Plutchik-Based Emotion Dataset

The project also contains a dataset organized around the eight primary emotions used by the application:

```text
Joy
Sadness
Anger
Fear
Surprise
Trust
Disgust
Anticipation
```

These datasets support the project's experimentation around emotion recognition and empathetic dialogue generation.

---

## 🤖 Current Inference Architecture

The current deployed application does **not train a custom neural network during inference**.

Instead, it uses a hosted large language model through the Groq API.

```text
                    ┌─────────────────────┐
                    │     Streamlit       │
                    │     Application     │
                    └──────────┬──────────┘
                               │
                               ▼
                       ┌───────────────┐
                       │   Groq API    │
                       └───────┬───────┘
                               │
                               ▼
                     ┌───────────────────┐
                     │ openai/gpt-oss-20b│
                     └─────────┬─────────┘
                               │
                               ▼
                     Structured JSON
                               │
                               ▼
                       Streamlit UI
```

This architecture keeps the application lightweight while allowing the model to perform both emotion analysis and response generation.

---

## 🛠️ Technology Stack

| Area | Technology |
|---|---|
| Language | Python |
| UI | Streamlit |
| LLM API | Groq |
| Model | `openai/gpt-oss-20b` |
| Structured Output | JSON Schema |
| Session State | Streamlit Session State |
| Datasets | DailyDialog, EmpatheticDialogues, MELD |
| Deployment | Streamlit Cloud |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip
- Groq API key

---

### 1. Clone the Repository

```bash
git clone https://github.com/Swaritdixit/empathetic_chatbot.git
cd empathetic_chatbot
```

---

### 2. Create a Virtual Environment

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

The main dependencies are:

```text
streamlit
groq
```

---

### 4. Configure the Groq API Key

For local development:

#### Windows

```bash
set GROQ_API_KEY=your_api_key
```

#### Linux / macOS

```bash
export GROQ_API_KEY=your_api_key
```

Alternatively, configure the key through Streamlit Secrets.

---

### 5. Run the Application

```bash
streamlit run app.py
```

The application will be available at the local Streamlit URL shown in the terminal.

---

## 🌐 Deployment

The application is deployed using **Streamlit Cloud**.

### Live Demo

🔗 **https://empatheticchatbot-kuytrk9wk2eqqgr3nk9nmh.streamlit.app/**

The deployed application retrieves the Groq API key through Streamlit Secrets.

---

## ⚠️ Responsible AI Considerations

This application is an AI demonstration and is **not a replacement for professional medical or mental-health care**.

The system is explicitly instructed to:

- Avoid mental-health diagnosis
- Avoid claiming professional credentials
- Avoid inventing personal information
- Respond empathetically
- Keep responses concise

Emotion detection is an AI-generated interpretation and should not be treated as a definitive measurement of a person's emotional state.

---

## 📌 Current Limitations

- Emotion detection depends on the underlying LLM.
- Emotion scores are model-generated estimates.
- The application analyzes the current message rather than maintaining a persistent user profile.
- Conversations are stored only in the current Streamlit session.
- No database-backed conversation history is implemented.
- The chatbot does not use a custom fine-tuned model in the deployed inference pipeline.
- Internet connectivity is required for Groq API inference.

---

## 🔮 Future Improvements

- Fine-tune an emotion classification model using the available datasets
- Compare traditional ML and transformer-based emotion classifiers
- Add conversation-level emotion tracking
- Add emotion trends over a conversation
- Add persistent conversation history
- Add retrieval-augmented response generation
- Evaluate emotion classification using accuracy, precision, recall, and F1-score
- Compare model-generated emotion predictions with dataset labels
- Add multilingual emotion detection
- Add stronger safety handling for high-risk conversations
- Add configurable response styles
- Add model benchmarking and latency monitoring

---

## 🎯 What I Learned

Through this project, I worked with:

- Conversational AI
- Emotion recognition
- Prompt engineering
- Structured LLM outputs
- JSON Schema
- Groq API integration
- Streamlit
- Session state management
- Conversational datasets
- Empathetic response generation
- Defensive validation of LLM outputs
- AI application deployment
- Responsible AI considerations

---

## 👨‍💻 Author

**Swarit Dixit**

B.Tech Electronics & Communication Engineering  
IIT Bhilai

- 💻 GitHub: https://github.com/Swaritdixit
- 💼 LinkedIn: https://www.linkedin.com/in/swarit-dixit-b907b8309/
