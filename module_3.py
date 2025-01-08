from TTS.api import TTS
import soundfile as sf 
import warnings
warnings.filterwarnings('ignore')

model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
# gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=["model_xtts/samples_en_sample.wav"])


def text_to_speech(text,output_path="others/output_from_TTS.wav"):
    # Synthesize the speech and capture the output audio data
    model.tts_to_file(text,
                file_path=output_path,
                speaker_wav="others/samples_en_sample.wav",
                language="en")
    
    
    return output_path
