import json
import os
import time
from datetime import datetime

import streamlit as st
from streamlit_autorefresh import st_autorefresh
from google import genai


# =========================================================
# APP CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="StudyMate AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "studymate_data.json"

# Use a model available to your Gemini API key.
MODEL_NAME = "gemini-2.5-flash"

FOCUS_DURATION = 40 * 60  # 40 minutes, in seconds


# =========================================================
# INTELLIGENT BOOK BRAND MARK
# =========================================================
BOOK_LOGO = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"
     role="img" aria-label="StudyMate AI intelligent book logo">
  <defs>
    <linearGradient id="bookGradient" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#38E6A3"/>
      <stop offset="100%" stop-color="#087F5B"/>
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <circle cx="60" cy="60" r="54" fill="#10251F"
          stroke="#C9A96E" stroke-opacity=".55"/>
  <g fill="none" stroke="url(#bookGradient)" stroke-width="4"
     stroke-linecap="round" stroke-linejoin="round">
    <path d="M60 46 C48 36 34 36 23 41 L23 78
             C36 73 49 75 60 85 Z"/>
    <path d="M60 46 C72 36 86 36 97 41 L97 78
             C84 73 71 75 60 85 Z"/>
    <path d="M60 46 L60 85"/>
    <path d="M32 51 L46 51 M32
