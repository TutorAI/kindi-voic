### In this pipeline the following files work in the given way:
- config.py contains the API keys used in this pipeline.
- module_1.py contains the code for Audio-to-Text model, it takes the captured audio from the "others" folder and then generate text for that audio.
- module_2.py contains the code for Text-to-Text model. This model takes the output of the module_1 as input and then generate a response.
- module_3.py contains the code for Text-to-Audio model which takes the generated response from the module_2 and generate an audio for that which is stored in the "others" folder.


#### To run the API these commands are required:
- uvicorn app:app --reload: To start the api service.
- curl -X POST http://127.0.0.1:8000/start-recording: To start recording.
- curl -X POST http://127.0.0.1:8000/stop-recording: To stop recording.
- curl -X POST http://127.0.0.1:8000/process-audio: To process the recording for further processing and it also reads aloud the audio output that is generated automatically.
