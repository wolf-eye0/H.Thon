"""
bidirectional_malayalam_bot.py - FIXED VERSION
Complete communication system with proper error handling
"""
import whisper
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
from datetime import datetime
import requests
import json

class BidirectionalMalayalamBot:
    def __init__(self, use_ollama=False):
        """
        Initialize complete communication system
        
        Args:
            use_ollama: Enable AI backend
        """
        print("Loading models...")
        
        # Whisper for speech-to-text
        print("Loading Whisper (speech recognition)...")
        self.whisper_model = whisper.load_model("base")
        
        # Google Translate for translation
        self.translator_en_to_ml = GoogleTranslator(source='en', target='ml')
        self.translator_ml_to_en = GoogleTranslator(source='ml', target='en')
        
        self.use_ollama = use_ollama
        
        # Create folders
        os.makedirs("transcripts", exist_ok=True)
        os.makedirs("audio_input", exist_ok=True)
        os.makedirs("audio_output", exist_ok=True)
        
        print("✓ Whisper loaded (speech → text)")
        print("✓ Google Translate ready")
        print("✓ Google TTS ready")
        print("✓ System ready!\n")
    
    # ============================================================
    # PART 1: AUDIO INPUT → TEXT (Transcription)
    # ============================================================
    
    def transcribe_audio(self, audio_file_path, language='ml'):
        """
        Convert audio to text using Whisper
        
        Args:
            audio_file_path: Path to audio file (.mp3, .wav, .ogg, .m4a)
            language: 'ml' (Malayalam) or 'en' (English) or None (auto-detect)
        
        Returns:
            dict: {text, language, confidence}
        """
        try:
            print(f"\n{'='*60}")
            print(f"🎤 Transcribing: {audio_file_path}")
            
            # Check if file exists
            if not os.path.exists(audio_file_path):
                print(f"❌ File not found: {audio_file_path}")
                return None
            
            # Transcribe with Whisper
            if language:
                result = self.whisper_model.transcribe(
                    audio_file_path,
                    language=language,
                    fp16=False
                )
            else:
                # Auto-detect language
                result = self.whisper_model.transcribe(
                    audio_file_path,
                    fp16=False
                )
            
            text = result["text"].strip()
            detected_language = result.get("language", language)
            
            print(f"✅ Transcribed ({detected_language}): {text}")
            print(f"{'='*60}\n")
            
            return {
                'text': text,
                'language': detected_language,
                'audio_file': audio_file_path,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Transcription error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def save_transcript(self, transcription_result, filename=None):
        """
        Save transcript as text file
        
        Args:
            transcription_result: Result from transcribe_audio()
            filename: Output filename (auto-generated if None)
        
        Returns:
            str: Path to saved transcript file
        """
        try:
            if filename is None:
                timestamp = int(datetime.now().timestamp())
                filename = f"transcripts/transcript_{timestamp}.txt"
            
            # Save as text file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("AUDIO TRANSCRIPT\n")
                f.write("="*60 + "\n\n")
                f.write(f"Timestamp: {transcription_result['timestamp']}\n")
                f.write(f"Audio File: {transcription_result['audio_file']}\n")
                f.write(f"Language: {transcription_result['language']}\n\n")
                f.write("="*60 + "\n")
                f.write("TRANSCRIPTION:\n")
                f.write("="*60 + "\n\n")
                f.write(transcription_result['text'])
                f.write("\n\n" + "="*60 + "\n")
            
            # Also save as JSON
            json_filename = filename.replace('.txt', '.json')
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(transcription_result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Transcript saved:")
            print(f"   Text: {filename}")
            print(f"   JSON: {json_filename}\n")
            
            return filename
            
        except Exception as e:
            print(f"❌ Save error: {e}")
            return None
    
    def batch_transcribe(self, audio_files):
        """
        Transcribe multiple audio files
        
        Args:
            audio_files: List of audio file paths
        
        Returns:
            list: List of transcription results
        """
        print(f"\n{'='*60}")
        print(f"📁 BATCH TRANSCRIPTION: {len(audio_files)} files")
        print(f"{'='*60}\n")
        
        results = []
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f"Processing {i}/{len(audio_files)}: {audio_file}")
            
            result = self.transcribe_audio(audio_file)
            
            if result:
                transcript_file = self.save_transcript(result)
                results.append({
                    'audio': audio_file,
                    'transcript': transcript_file,
                    'text': result['text']
                })
        
        print(f"\n{'='*60}")
        print(f"✅ Batch complete: {len(results)}/{len(audio_files)} successful")
        print(f"{'='*60}\n")
        
        return results
    
    # ============================================================
    # PART 2: TEXT PROCESSING (Translation)
    # ============================================================
    
    def detect_language(self, text):
        """Detect if text is Malayalam or English"""
        malayalam_chars = 'അആഇഈഉഊഋഎഏഐഒഓഔകഖഗഘങചഛജഝഞടഠഡഢണതഥദധനപഫബഭമയരലവശഷസഹളഴറ'
        return 'ml' if any(c in malayalam_chars for c in text) else 'en'
    
    def translate_to_malayalam(self, english_text):
        """English → Malayalam"""
        try:
            return self.translator_en_to_ml.translate(english_text)
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return english_text
    
    def translate_to_english(self, malayalam_text):
        """Malayalam → English"""
        try:
            return self.translator_ml_to_en.translate(malayalam_text)
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return malayalam_text
    
    def query_ollama(self, english_text):
        """Query AI backend"""
        if not self.use_ollama:
            return None
        
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2",
                    "prompt": f"Medical query: {english_text}\nBrief helpful response:",
                    "stream": False
                },
                timeout=30
            )
            return response.json()["response"]
        except Exception as e:
            print(f"⚠️ AI not available: {e}")
            return None
    
    # ============================================================
    # PART 3: TEXT → AUDIO OUTPUT (Synthesis)
    # ============================================================
    
    def generate_audio(self, text, filename=None, language='ml'):
        """
        Convert text to audio using Google TTS
        
        Args:
            text: Text to convert
            filename: Output filename
            language: 'ml' or 'en'
        """
        try:
            if filename is None:
                timestamp = int(datetime.now().timestamp())
                filename = f"audio_output/response_{timestamp}.mp3"
            
            tts = gTTS(text=text, lang=language, slow=False)
            tts.save(filename)
            
            return filename
            
        except Exception as e:
            print(f"❌ Audio generation error: {e}")
            return None
    
    # ============================================================
    # PART 4: COMPLETE COMMUNICATION PIPELINE
    # ============================================================
    
    def process_audio_input(self, audio_file_path, save_transcript_file=True):
        """
        COMPLETE PIPELINE: Audio → Text → AI → Malayalam Audio
        
        Args:
            audio_file_path: User's audio input
            save_transcript_file: Save transcript to file
        
        Returns:
            dict: Complete conversation result
        """
        print(f"\n{'🔄'*30}")
        print("PROCESSING AUDIO INPUT")
        print(f"{'🔄'*30}\n")
        
        # Step 1: Transcribe audio to text
        print("Step 1: Transcribing audio...")
        transcription = self.transcribe_audio(audio_file_path)
        
        if not transcription:
            print("❌ Transcription failed!")
            return {
                'error': 'Transcription failed',
                'user_audio': audio_file_path,
                'user_text': None,
                'success': False
            }
        
        # Save transcript
        if save_transcript_file:
            self.save_transcript(transcription)
        
        user_text = transcription['text']
        user_language = self.detect_language(user_text)
        
        print(f"👤 User said ({user_language}): {user_text}")
        
        # Step 2: Translate to English if needed
        if user_language == 'ml':
            print("\nStep 2: Translating to English...")
            english_query = self.translate_to_english(user_text)
            print(f"🔄 English: {english_query}")
        else:
            english_query = user_text
        
        # Step 3: Get AI response
        print("\nStep 3: Getting AI response...")
        ai_response = self.query_ollama(english_query)
        
        if ai_response is None:
            ai_response = f"I understand your concern. Please consult a healthcare provider."
            print(f"💭 Fallback response: {ai_response}")
        else:
            print(f"🤖 AI: {ai_response}")
        
        # Step 4: Translate to Malayalam
        print("\nStep 4: Translating to Malayalam...")
        malayalam_response = self.translate_to_malayalam(ai_response)
        print(f"✅ Malayalam: {malayalam_response}")
        
        # Step 5: Generate audio response
        print("\nStep 5: Generating audio response...")
        audio_output = self.generate_audio(malayalam_response)
        print(f"🔊 Audio: {audio_output}")
        
        print(f"\n{'✅'*30}")
        print("COMPLETE!")
        print(f"{'✅'*30}\n")
        
        return {
            'success': True,
            'user_audio': audio_file_path,
            'user_text': user_text,
            'user_language': user_language,
            'english_query': english_query,
            'ai_response': ai_response,
            'malayalam_response': malayalam_response,
            'response_audio': audio_output,
            'transcript_saved': save_transcript_file
        }
    
    def interactive_audio_mode(self):
        """
        Interactive mode: Upload audio files and get responses
        """
        print("\n" + "="*60)
        print("🎤 INTERACTIVE AUDIO MODE")
        print("="*60)
        print("\nCommands:")
        print("  - Enter audio file path to transcribe")
        print("  - 'test' - Run test with sample audio")
        print("  - 'batch' - Batch transcribe multiple files")
        print("  - 'exit' - Quit\n")
        
        while True:
            try:
                user_input = input("Audio file path (or command): ").strip()
                
                if user_input.lower() == 'exit':
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower() == 'test':
                    self.run_test()
                    continue
                
                if user_input.lower() == 'batch':
                    print("\nEnter audio files (comma-separated):")
                    files = input("> ").strip().split(',')
                    files = [f.strip() for f in files]
                    self.batch_transcribe(files)
                    continue
                
                if not user_input:
                    continue
                
                # Check if file exists
                if not os.path.exists(user_input):
                    print(f"❌ File not found: {user_input}\n")
                    continue
                
                # Process audio
                result = self.process_audio_input(user_input)
                
                if result.get('success'):
                    print("\n" + "─"*60)
                    print("CONVERSATION SUMMARY")
                    print("─"*60)
                    print(f"User said: {result['user_text']}")
                    print(f"Bot replied: {result['malayalam_response']}")
                    print(f"Audio response: {result['response_audio']}")
                    print("─"*60 + "\n")
                else:
                    print("\n❌ Processing failed\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
                import traceback
                traceback.print_exc()
    
    def run_test(self):
        """
        Generate test audio and process it - FIXED VERSION
        """
        print("\n" + "="*60)
        print("🧪 RUNNING TEST")
        print("="*60)
        
        # Generate test audio file
        print("\nGenerating test audio...")
        test_text_ml = "എനിക്ക് പനിയുണ്ട്, തലവേദനയുണ്ട്"
        test_audio = "audio_input/test_input.mp3"
        
        try:
            tts = gTTS(text=test_text_ml, lang='ml')
            tts.save(test_audio)
            print(f"✓ Test audio created: {test_audio}")
        except Exception as e:
            print(f"❌ Failed to create test audio: {e}")
            return
        
        # Process it
        print("\nProcessing test audio through full pipeline...")
        result = self.process_audio_input(test_audio)
        
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)
        
        # Check if processing was successful
        if result.get('success'):
            print(f"\n✅ SUCCESS!")
            print(f"Input audio: {test_audio}")
            print(f"Transcribed: {result['user_text']}")
            print(f"AI response: {result['ai_response']}")
            print(f"Malayalam: {result['malayalam_response']}")
            print(f"Output audio: {result['response_audio']}")
            print("\n✅ Full communication cycle working!")
        else:
            print(f"\n❌ FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            if result.get('user_text') is None:
                print("\nTroubleshooting:")
                print("1. Check if audio file was created properly")
                print("2. Try with a different audio file")
                print("3. Check Whisper model is loaded")
        
        print("="*60)


# ============================================================
# SIMPLE USAGE FUNCTIONS
# ============================================================

def simple_transcribe(audio_file):
    """
    Simple one-line transcription
    
    Usage:
        text = simple_transcribe("audio.mp3")
    """
    bot = BidirectionalMalayalamBot()
    result = bot.transcribe_audio(audio_file)
    if result:
        bot.save_transcript(result)
        return result['text']
    return None


def simple_audio_to_audio(input_audio_file):
    """
    Simple: Audio in → Audio out
    
    Usage:
        output_audio = simple_audio_to_audio("user_question.mp3")
    """
    bot = BidirectionalMalayalamBot(use_ollama=True)
    result = bot.process_audio_input(input_audio_file)
    if result.get('success'):
        return result['response_audio']
    return None


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔄 BIDIRECTIONAL MALAYALAM COMMUNICATION")
    print("="*60)
    print("\nComplete System:")
    print("  1. Audio → Text (Whisper)")
    print("  2. Text → AI Processing")
    print("  3. AI → Malayalam Audio (Google TTS)")
    
    # Check Ollama
    try:
        requests.get("http://localhost:11434/api/version", timeout=2)
        ollama_available = True
        print("  • AI Backend: Available")
    except:
        ollama_available = False
        print("  • AI Backend: Not available (using fallback)")
    
    # Initialize
    bot = BidirectionalMalayalamBot(use_ollama=ollama_available)
    
    print("\n" + "="*60)
    print("CHOOSE MODE")
    print("="*60)
    print("\n1. Test Complete Pipeline (audio → audio)")
    print("2. Interactive Audio Mode")
    print("3. Transcribe Single Audio File")
    print("4. Batch Transcribe Multiple Files")
    print("5. Exit")
    
    choice = input("\nChoice (1-5): ").strip()
    
    if choice == '1':
        # Full pipeline test
        bot.run_test()
        
    elif choice == '2':
        # Interactive
        bot.interactive_audio_mode()
        
    elif choice == '3':
        # Single transcription
        audio_file = input("\nEnter audio file path: ").strip()
        if os.path.exists(audio_file):
            result = bot.transcribe_audio(audio_file)
            if result:
                bot.save_transcript(result)
                print(f"\n✅ Transcribed: {result['text']}")
            else:
                print("\n❌ Transcription failed")
        else:
            print(f"❌ File not found: {audio_file}")
    
    elif choice == '4':
        # Batch transcription
        print("\nEnter audio files (comma-separated):")
        files_input = input("> ").strip()
        audio_files = [f.strip() for f in files_input.split(',')]
        bot.batch_transcribe(audio_files)
    
    else:
        print("\n👋 Exiting...")
    
    print("\n" + "="*60)
    print("Complete bidirectional communication system")
    print("="*60)
