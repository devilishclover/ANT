import os
import tkinter as tk
from tkinter import messagebox, simpledialog
from tkinter import PhotoImage
from pygame import mixer
import threading
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
from pydub import AudioSegment
import whisper
from ollama import chat


def ensure_folders():
    for folder in ("Recordings", "Transcripts", "Notes"):
        os.makedirs(folder, exist_ok=True)


def transcribe_audio(audio_file):
    model = whisper.load_model("turbo")
    result = model.transcribe(audio_file)

    base_name = os.path.splitext(os.path.basename(audio_file))[0]
    transcript_path = f"Transcripts/{base_name}_transcript.txt"
    with open(transcript_path, "w", encoding="utf-8") as file:
        file.write(result["text"])

    messagebox.showinfo("Success", f"Transcript saved as {transcript_path}")
    return transcript_path


def generate_notes(transcript_file):
    with open(transcript_file, "r", encoding="utf-8") as file:
        content = file.read()

    prompt = f"""
        You are my personal AI note-taking assistant for university lectures. 
        Your task is to help me create clear, concise, and well-organized notes. 
        You will be given the entire transcript from the lecture.
        Organize the content into a logical structure with main topics and subtopics.
        Create brief summaries for complex ideas.
        Create mnemonics or memory aids for difficult-to-remember information.
        Identify any formulas, equations, or statistical data, and format them clearly.
        Create a brief glossary of new terms introduced in the lecture.
        Summarize the main takeaways at the end of each major section.
        Please format the notes in a visually appealing manner, using appropriate headings, subheadings, and spacing.
        THE FOLLOWING IS THE LECTURE TRANSCRIPT:
        {content}
        """
    response = chat(model='ALIENTELLIGENCE/contentsummarizer', messages=[{'role': 'user', 'content': prompt}])

    base_name = os.path.splitext(os.path.basename(transcript_file))[0]
    notes_path = f"Notes/{base_name}_notes.txt"
    with open(notes_path, "w", encoding="utf-8") as file:
        file.write(response['message']['content'])

    messagebox.showinfo("Success", f"Notes saved as {notes_path}")
    return notes_path


def ask_question(notes_file):
    with open(notes_file, 'r') as file:
        notes = file.read()

    question = simpledialog.askstring("Ask Question", "Enter your question:")
    if question:
        prompt = f"""
                Assume all information in the transcript is correct. Do not assume anything or add any information that is not in the lecture.
                Based on the following lecture transcript, please answer the question below:
                LECTURE NOTES:
                {notes}

                QUESTION:
                {question}
                """
        response = chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
        messagebox.showinfo("Answer", response['message']['content'])


class RecorderApp:
    def __init__(self, root, player):
        self.root = root
        self.player = player
        self.is_recording = False
        self.audio_data = []
        self.fs = 44100

        self.record_btn = tk.Button(root, text="Record", bg="green", command=self.toggle_recording)
        self.record_btn.grid(row=0, column=0)

        self.transcribe_btn = tk.Button(root, text="Transcribe", bg="blue", command=self.transcribe)
        self.transcribe_btn.grid(row=0, column=1)

        self.notes_btn = tk.Button(root, text="Make Notes", bg="orange", command=self.make_notes)
        self.notes_btn.grid(row=0, column=2)

        self.question_btn = tk.Button(root, text="Ask", bg="purple", command=self.ask_question)
        self.question_btn.grid(row=0, column=3)

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.is_recording = True
        self.audio_data = []
        self.record_btn.config(text="Stop", bg="red")
        threading.Thread(target=self.record).start()

    def record(self):
        with sd.InputStream(samplerate=self.fs, channels=1, callback=self.audio_callback):
            while self.is_recording:
                sd.sleep(100)

    def audio_callback(self, indata, *_):
        self.audio_data.append(indata.copy())

    def stop_recording(self):
        self.is_recording = False
        self.record_btn.config(text="Record", bg="green")

        if self.audio_data:
            file_name = simpledialog.askstring("Save", "Enter recording name:")
            if file_name:
                self.save_recording(file_name)

    def save_recording(self, file_name):
        audio = np.concatenate(self.audio_data, axis=0)
        wav_path = f"Recordings/{file_name}.wav"
        mp3_path = f"Recordings/{file_name}.mp3"

        write(wav_path, self.fs, audio)
        AudioSegment.from_wav(wav_path).export(mp3_path, format="mp3")
        os.remove(wav_path)

        messagebox.showinfo("Saved", f"Recording saved as {mp3_path}")

    def transcribe(self):
        selected = self.player.get_selected(self.player.recordings)
        if selected:
            transcribe_audio(f"Recordings/{selected}")
            self.player.refresh()

    def make_notes(self):
        selected = self.player.get_selected(self.player.transcripts)
        if selected:
            generate_notes(f"Transcripts/{selected}")
            self.player.refresh()

    def ask_question(self):
        selected = self.player.get_selected(self.player.notes)
        if selected:
            ask_question(f"Notes/{selected}")


class PlayerApp:
    def __init__(self, root):
        self.root = root
        mixer.init()

        self.recordings = self.create_playlist("Recordings", 0)
        self.transcripts = self.create_playlist("Transcripts", 1)
        self.notes = self.create_playlist("Notes", 2)

        tk.Button(root, text="Refresh", command=self.refresh).grid(row=2, column=3)
        tk.Button(root, text="Delete", command=self.delete_file).grid(row=2, column=4) 
        self.refresh()


    def create_playlist(self, label, col):
        playlist = tk.Listbox(self.root, width=30)
        playlist.grid(row=1, column=col)
        playlist.bind('<Double-1>', self.open_file)
        return playlist

    def refresh(self):
        for folder, playlist in zip(("Recordings", "Transcripts", "Notes"),
                                    (self.recordings, self.transcripts, self.notes)):
            playlist.delete(0, tk.END)
            for file in os.listdir(folder):
                playlist.insert(tk.END, file)

    def get_selected(self, playlist):
        selection = playlist.curselection()
        return playlist.get(selection[0]) if selection else None

    def open_file(self, event):
        selected = self.get_selected(event.widget)
        if selected:
            folder = "Recordings" if event.widget == self.recordings else (
                "Transcripts" if event.widget == self.transcripts else "Notes")

            file_path = os.path.join(folder, selected)

            print(f"Trying to open file at: {file_path}")

            if os.path.exists(file_path):
                try:
                    os.startfile(file_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open file: {e}")
            else:
                messagebox.showerror("Error", f"File not found: {file_path}")

    def delete_file(self):
        selected = self.get_selected(self.root.focus_get())
        if selected:
            folder = "Recordings" if self.root.focus_get() == self.recordings else (
                "Transcripts" if self.root.focus_get() == self.transcripts else "Notes")
            file_path = os.path.join(folder, selected)

            try:
                os.remove(file_path)
                messagebox.showinfo("Success", f"File deleted: {file_path}")
                self.refresh()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete file: {e}")

def set_dark_mode(root):
    root.tk_setPalette(background="#2e2e2e", foreground="white", activeBackground="#1c1c1c", activeForeground="white")

def set_light_mode(root):
    root.tk_setPalette(background="SystemButtonFace", foreground="black", activeBackground="SystemButtonFace", activeForeground="black")

def toggle_dark_mode(root):
    current_bg = root.cget("background")
    if current_bg == "#2e2e2e":
        set_light_mode(root)
    else:
        set_dark_mode(root)

def main():
    ensure_folders()

    root = tk.Tk()

    icon_path = "logo.ico" 
    root.iconbitmap(icon_path)

    root.title("A.N.T AI NOTE TAKER")

    #darkmode toggle
    dark_mode_btn = tk.Button(root, text="Dark Mode", command=lambda: toggle_dark_mode(root))
    dark_mode_btn.grid(row=0, column=5, sticky="e")

    player = PlayerApp(root)
    RecorderApp(root, player)
    root.mainloop()

if __name__ == "__main__":
    main()
