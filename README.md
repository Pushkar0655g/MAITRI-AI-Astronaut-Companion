# MAITRI – AI Companion for Astronaut Psychological Well-Being

🏆 Smart India Hackathon 2025 Finalist

## Overview
MAITRI is an offline AI companion designed to monitor and support astronaut mental health in isolated environments such as spacecraft.

It integrates:
- Speech emotion recognition
- Retrieval-Augmented Generation (RAG)
- Local LLM inference using Ollama
- Dockerized deployment

## Architecture
User Input → Emotion Analysis → Context Retrieval → Local LLM → Intelligent Response

## Tech Stack
- Python
- Ollama (Gemma)
- HuggingFace
- Docker
- RAG Architecture

## Setup

### Install Dependencies
pip install -r requirements.txt

### Install Ollama
Download from: https://ollama.com

Run:
ollama run gemma

### Build Knowledge Base
python build_index.py

### Run Application
python app.py

## Note
LLM models are not included in this repository.
Ollama must be installed locally.
