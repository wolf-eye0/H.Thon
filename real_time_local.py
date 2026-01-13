"""
real_time_translator.py
ONLY works on local desktop with microphone
"""
import whisper
import speech_recognition as sr
from gtts import gTTS
from language_script import GoogleTranslateNLP
import os
import threading

class RealTimeTranslator:
    def __init__(self):
        """Requires: microphone hardware"""
        self.whisper = whisper.load_model("base")
        self.translator = GoogleTranslateNLP()
        self.recognizer = sr.Recognizer()
        self.mic = sr.Microphone()  # ⚠️ Needs physical microphone
        
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        print("✓ Real-time translator ready (with microphone)")
    
    def continuous_translate(self):
        """
        REAL-TIME continuous translation
        Listens → Transcribes → Translates → Speaks
        """
        print("\n🎤 Listening continuously... (Ctrl+C to stop)\n")
        
        with self.mic as source:
            while True:
                try:
                    # Listen (REAL-TIME)
                    print("Listening...")
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=5)
                    
                    # Save temp audio
                    with open("temp.wav", "wb") as f:
                        f.write(audio.get_wav_data())
                    
                    # Transcribe
                    result = self.whisper.transcribe("temp.wav", language='ml')
                    original = result["text"].strip()
                    
                    if original:
                        print(f"📝 ML: {original}")
                        
                        # Translate
                        translation = self.translator.malayalam_to_english(original)
                        print(f"✅ EN: {translation}\n")
                        
                        # Speak (background)
                        threading.Thread(target=self._speak, args=(translation, 'en')).start()
                    
                    os.remove("temp.wav")
                    
                except sr.WaitTimeoutError:
                    pass
                except KeyboardInterrupt:
                    print("\n✅ Stopped")
                    break
    
    def _speak(self, text, lang):
        """Speak in background thread"""
        tts = gTTS(text=text, lang=lang)
        tts.save("reply.mp3")
        os.system("mpv reply.mp3 2>/dev/null")
        os.remove("reply.mp3")


if __name__ == "__main__":
    translator = RealTimeTranslator()
    translator.continuous_translate()  # ⚠️ Only works on local machine
