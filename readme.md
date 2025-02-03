# A.N.T AI NOTE TAKER

## Overview
A.N.T AI NOTE TAKER is a desktop application that allows users to record audio, transcribe it into text, generate structured lecture notes, and ask AI-based questions on the notes. This tool is ideal for students and professionals who need an efficient way to document and review spoken content.

## Features
- **Audio Recording**: Record lectures or meetings and save them in MP3 format.
- **Transcription**: Convert audio recordings into text using Whisper AI.
- **Automated Note Generation**: Generate structured, easy-to-read notes from transcriptions using AI.
- **Question Answering**: Ask AI questions based on the generated notes.
- **File Management**: Organize and manage recordings, transcripts, and notes within the application.
- **Dark Mode Support**: Toggle between dark and light themes for better usability.

## Installation
### Prerequisites
Ensure you have the following installed on your system:
- Python 3.8+
- Required Python libraries:
  ```sh
  pip install tkinter pygame sounddevice numpy scipy pydub openai-whisper ollama
  ```
-Ollama with ALIENTELLIGENCE/contentsummarizer and llama3.2

### Setup
1. Clone this repository or download the script.
2. Run the script using:
   ```sh
   python main.py
   ```

## Usage
1. **Recording Audio**
   - Click the "Record" button to start recording.
   - Click again to stop and save the recording.
2. **Transcribing Audio**
   - Select a recorded file from the list and click "Transcribe" to generate a text transcript.
3. **Generating Notes**
   - Select a transcript and click "Make Notes" to create structured lecture notes.
4. **Asking Questions**
   - Select a notes file and click "Ask" to input a question related to the lecture content.
5. **Managing Files**
   - Use the playlist to view, open, or delete recordings, transcripts, and notes.
6. **Dark Mode Toggle**
   - Click "Dark Mode" to switch between themes.

## Folder Structure
- `Recordings/` - Stores audio recordings (.mp3 files)
- `Transcripts/` - Stores transcribed text (.txt files)
- `Notes/` - Stores AI-generated structured notes (.txt files)

