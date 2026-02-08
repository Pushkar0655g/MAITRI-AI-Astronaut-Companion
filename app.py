# app.py
import streamlit as st
from transformers import pipeline, SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
import torch
import scipy.io.wavfile as wav
import requests
import json
import numpy as np
from streamlit_mic_recorder import mic_recorder # <-- The new browser-based recorder

# --- CONFIGURATION & CONSTANTS ---
st.set_page_config(page_title="MAITRI - AI Companion", layout="centered")
st.image("https://i.imgur.com/v4p4S8D.png", width=150)
st.title("MAITRI - AI Astronaut Companion")
st.write("A voice-first, psychologically-aware companion for astronaut well-being.")

AUDIO_FILENAME = "temp_user_audio.wav"
OLLAMA_HOST = "http://host.docker.internal:11434"

# --- MODEL LOADING (Cached for performance) ---
@st.cache_resource
def load_models():
    """Loads all the required AI models."""
    vocal_emotion_detector = pipeline("audio-classification", model="superb/wav2vec2-base-superb-er")
    speech_to_text = pipeline("automatic-speech-recognition", model="openai/whisper-base")
    tts_processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    tts_model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    tts_vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
    speaker_embeddings = torch.zeros((1, 512)) # Use the reliable built-in voice
    
    return (vocal_emotion_detector, speech_to_text, 
            tts_processor, tts_model, tts_vocoder, speaker_embeddings)

# Unpack all loaded models
(vocal_emotion_detector, speech_to_text, 
 tts_processor, tts_model, tts_vocoder, speaker_embeddings) = load_models()

# --- SESSION STATE INITIALIZATION ---
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- HELPER FUNCTIONS ---
def generate_ai_response(user_prompt, vocal_emotion, chat_history_str):
    """Generates a response from the Ollama model."""
    system_prompt = f"""You are MAITRI, an AI companion for astronauts... [Your full prompt here]""" # Abridged
    full_prompt = f"{system_prompt}\n\nAstronaut: \"{user_prompt}\"\n\nMAITRI:"
    
    data = {"model": "gemma:2b", "prompt": full_prompt, "stream": False}
    try:
        response = requests.post(f"{OLLAMA_HOST}/api/generate", json=data)
        response.raise_for_status()
        return response.json()['response']
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Ollama: {e}."

def text_to_speech(text):
    """Converts text to playable audio bytes."""
    text = text[:550] 
    inputs = tts_processor(text=text, return_tensors="pt")
    speech = tts_model.generate_speech(inputs["input_ids"], speaker_embeddings, vocoder=tts_vocoder)
    return speech.numpy()

# --- UI LAYOUT ---
st.header("Voice Interaction")
st.write("Click the microphone to start recording, and click again to stop.")

# The new, browser-based microphone recorder
audio_info = mic_recorder(start_prompt="🎤 Speak", stop_prompt="⏹️ Stop", key='recorder')

if audio_info:
    # Get the audio data from the browser
    audio_bytes = audio_info['bytes']
    # Save the audio bytes to a file
    with open(AUDIO_FILENAME, "wb") as f:
        f.write(audio_bytes)

    with st.spinner("MAITRI is analyzing and thinking..."):
        user_prompt = speech_to_text(AUDIO_FILENAME)['text']
        vocal_results = vocal_emotion_detector(AUDIO_FILENAME)
        vocal_emotion = max(vocal_results, key=lambda x: x['score'])['label']
        
        chat_history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.chat_history])
        
        response = generate_ai_response(user_prompt, vocal_emotion, chat_history_str)
        audio_response_data = text_to_speech(response)
        
        st.session_state.chat_history.append({"role": "user", "content": f"{user_prompt} (Emotion: {vocal_emotion})"})
        st.session_state.chat_history.append({"role": "assistant", "content": response, "audio": audio_response_data})
        st.rerun()

st.header("Interaction Log")
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "audio" in message and message["audio"] is not None:
            st.audio(message["audio"], sample_rate=16000)