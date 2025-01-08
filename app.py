from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import sounddevice as sd
import scipy.io.wavfile as wav
import threading
import queue
import numpy as np
import os
from module_1 import speech_to_text
from module_2 import text_to_text
from module_3 import text_to_speech

import sounddevice as sd
import soundfile as sf

def play_audio(audio_file: str):
    # Read audio data from the file
    data, fs = sf.read(audio_file)
    
    # Play the audio using sounddevice
    sd.play(data, fs)
    
    # Wait until the audio finishes playing
    sd.wait()

SAMPLE_RATE = 44100
CHUNK_SIZE = 1024
OUTPUT_FILE = "others/Input_from_mic.wav"

app = FastAPI()

class AudioResponse(BaseModel):
    text: str
    output_audio_file: str

# Global state
audio_queue = queue.Queue()
stop_event = threading.Event()
frames = []

def reset_global_state():
    global audio_queue, stop_event, frames
    audio_queue = queue.Queue()
    stop_event = threading.Event()
    frames = []

def callback(indata, frames, time, status):
    if status:
        print(f"Status: {status}")
    audio_queue.put(indata.copy())

def process_audio():
    while not stop_event.is_set() or not audio_queue.empty():
        if not audio_queue.empty():
            data = audio_queue.get()
            frames.append(data)

def record_audio():
    reset_global_state()

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype=np.int16, callback=callback, blocksize=CHUNK_SIZE):
        processing_thread = threading.Thread(target=process_audio)
        processing_thread.start()

        stop_event.wait()  # Wait until the recording is stopped
        processing_thread.join()

    if frames:
        audio_data = np.concatenate(frames, axis=0)
        wav.write(OUTPUT_FILE, SAMPLE_RATE, audio_data)
        return OUTPUT_FILE
    else:
        return None

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI server!"}

@app.post("/start-recording")
def start_recording(background_tasks: BackgroundTasks):
    reset_global_state()
    background_tasks.add_task(record_audio)
    return {"status": "Recording started"}

@app.post("/stop-recording")
def stop_recording():
    stop_event.set()
    return {"status": "Recording stopped"}

@app.post("/process-audio")
def process_audio_file():
    audio_file = OUTPUT_FILE

    if not os.path.isfile(audio_file):
        raise HTTPException(status_code=404, detail="Audio file not found")

    try:
        text = speech_to_text(audio_file)
        processed_text = text_to_text(text)
        output_audio_file = text_to_speech(processed_text)
        
        # Play the processed audio
        play_audio(output_audio_file)
        
        return AudioResponse(text=text, output_audio_file=output_audio_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
