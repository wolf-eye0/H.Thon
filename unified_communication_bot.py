"""
unified_communication_bot.py
Complete unified system integrating all three communication modes
Imports from: google_TT.py (text) and googlev_audio.py (audio)
"""
import os
import sys
from datetime import datetime

# Import from your existing files
try:
    from google_TT import TextToTextBot, simple_chat, simple_translate
    TEXT_BOT_AVAILABLE = True
    print("✓ Text-to-Text system loaded (google_TT.py)")
except ImportError as e:
    TEXT_BOT_AVAILABLE = False
    print(f"⚠️ Text system not available: {e}")

try:
    from googlev_audio import BidirectionalMalayalamBot, simple_transcribe, simple_audio_to_audio
    AUDIO_BOT_AVAILABLE = True
    print("✓ Audio system loaded (googlev_audio.py)")
except ImportError as e:
    AUDIO_BOT_AVAILABLE = False
    print(f"⚠️ Audio system not available: {e}")


class UnifiedCommunicationBot:
    """
    Unified bot combining ALL communication modes:
    - Text → Text (google_TT.py)
    - Audio → Text (googlev_audio.py)
    - Text → Audio (googlev_audio.py)
    - Audio → Audio (googlev_audio.py)
    """
    
    def __init__(self, use_ollama=False):
        """Initialize unified system"""
        print("\n" + "="*60)
        print("🚀 UNIFIED COMMUNICATION SYSTEM")
        print("="*60)
        print("\nInitializing all subsystems...")
        
        self.use_ollama = use_ollama
        
        # Initialize text bot
        if TEXT_BOT_AVAILABLE:
            self.text_bot = TextToTextBot(use_ollama=use_ollama)
            print("✓ Text-to-Text engine ready")
        else:
            self.text_bot = None
            print("❌ Text-to-Text engine unavailable")
        
        # Initialize audio bot
        if AUDIO_BOT_AVAILABLE:
            self.audio_bot = BidirectionalMalayalamBot(use_ollama=use_ollama)
            print("✓ Audio engine ready")
        else:
            self.audio_bot = None
            print("❌ Audio engine unavailable")
        
        print("\n" + "="*60)
        print("SYSTEM CAPABILITIES")
        print("="*60)
        print(f"Text Input:  {'✓' if TEXT_BOT_AVAILABLE else '❌'}")
        print(f"Text Output: {'✓' if TEXT_BOT_AVAILABLE else '❌'}")
        print(f"Audio Input: {'✓' if AUDIO_BOT_AVAILABLE else '❌'}")
        print(f"Audio Output: {'✓' if AUDIO_BOT_AVAILABLE else '❌'}")
        print(f"AI Backend:  {'✓' if use_ollama else '❌'}")
        print("="*60 + "\n")
    
    # ============================================================
    # UNIVERSAL COMMUNICATION METHOD
    # ============================================================
    
    def communicate(self, 
                   input_data, 
                   input_type='text',
                   output_type='text',
                   context='general',
                   save_conversation=False):
        """
        Universal communication method
        
        Args:
            input_data: Text string or audio file path
            input_type: 'text' or 'audio'
            output_type: 'text' or 'audio' or 'both'
            context: 'general', 'medical', 'technical'
            save_conversation: Save to file
        
        Returns:
            dict: {
                'success': bool,
                'input_type': str,
                'output_type': str,
                'user_input': str (text),
                'text_response': str,
                'audio_response': str (path if audio),
                'conversation_log': dict
            }
        """
        result = {
            'success': False,
            'input_type': input_type,
            'output_type': output_type,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # STEP 1: Convert input to text
            print(f"\n{'🔄'*30}")
            print(f"UNIFIED COMMUNICATION: {input_type.upper()} → {output_type.upper()}")
            print(f"{'🔄'*30}\n")
            
            if input_type == 'audio':
                if not AUDIO_BOT_AVAILABLE:
                    result['error'] = 'Audio input not available'
                    return result
                
                print("Step 1: Transcribing audio input...")
                transcription = self.audio_bot.transcribe_audio(input_data)
                
                if not transcription:
                    result['error'] = 'Audio transcription failed'
                    return result
                
                text_input = transcription['text']
                result['audio_input'] = input_data
                print(f"✓ Transcribed: {text_input}")
            
            else:  # text input
                text_input = input_data
                print(f"Step 1: Text input received: {text_input}")
            
            result['user_input'] = text_input
            
            # STEP 2: Process with text bot
            print("\nStep 2: Processing with AI...")
            
            if TEXT_BOT_AVAILABLE:
                text_result = self.text_bot.process_text(
                    text_input,
                    context=context,
                    respond_in_malayalam=True
                )
                
                if not text_result['success']:
                    result['error'] = 'Text processing failed'
                    return result
                
                response_text = text_result['final_response']
                result['text_response'] = response_text
                result['conversation_details'] = text_result
                print(f"✓ Response: {response_text}")
            
            else:
                result['error'] = 'Text processing not available'
                return result
            
            # STEP 3: Generate audio if needed
            if output_type in ['audio', 'both']:
                if not AUDIO_BOT_AVAILABLE:
                    result['warning'] = 'Audio output not available, returning text only'
                else:
                    print("\nStep 3: Generating audio response...")
                    audio_file = self.audio_bot.generate_audio(response_text)
                    
                    if audio_file:
                        result['audio_response'] = audio_file
                        print(f"✓ Audio saved: {audio_file}")
                    else:
                        result['warning'] = 'Audio generation failed'
            
            # STEP 4: Save if requested
            if save_conversation and TEXT_BOT_AVAILABLE:
                print("\nStep 4: Saving conversation...")
                saved_file = self.text_bot.save_conversation(text_result)
                result['saved_file'] = saved_file
            
            result['success'] = True
            
            print(f"\n{'✅'*30}")
            print("COMMUNICATION COMPLETE!")
            print(f"{'✅'*30}\n")
            
            return result
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            result['error'] = str(e)
            return result
    
    # ============================================================
    # CONVENIENCE METHODS
    # ============================================================
    
    def text_to_text(self, text, context='general'):
        """Text input → Text output"""
        return self.communicate(text, 'text', 'text', context)
    
    def text_to_audio(self, text, context='general'):
        """Text input → Audio output"""
        return self.communicate(text, 'text', 'audio', context)
    
    def audio_to_text(self, audio_file):
        """Audio input → Text output"""
        return self.communicate(audio_file, 'audio', 'text')
    
    def audio_to_audio(self, audio_file, context='general'):
        """Audio input → Audio output (full pipeline)"""
        return self.communicate(audio_file, 'audio', 'audio', context)
    
    # ============================================================
    # INTERACTIVE MODES
    # ============================================================
    
    def interactive_chat(self):
        """
        Interactive chat with dynamic input/output modes
        """
        print("\n" + "="*60)
        print("💬 UNIFIED INTERACTIVE CHAT")
        print("="*60)
        print("\nCommands:")
        print("  - Type your message for text input")
        print("  - 'audio: path/to/file.mp3' for audio input")
        print("  - '/mode text' - Text output (default)")
        print("  - '/mode audio' - Audio output")
        print("  - '/mode both' - Text + Audio output")
        print("  - '/context medical' - Medical context")
        print("  - '/context general' - General context")
        print("  - '/context technical' - Technical context")
        print("  - '/save' - Toggle auto-save")
        print("  - '/exit' - Quit")
        print("="*60 + "\n")
        
        output_mode = 'text'
        context = 'general'
        auto_save = False
        conversation_count = 0
        
        while True:
            try:
                # Show current settings
                status = f"[{context}|{output_mode}]"
                user_input = input(f"{status} You: ").strip()
                
                if not user_input:
                    continue
                
                # Commands
                if user_input.lower() == '/exit':
                    print(f"\n👋 Goodbye! Total conversations: {conversation_count}")
                    break
                
                if user_input.lower().startswith('/mode '):
                    new_mode = user_input.split()[1].lower()
                    if new_mode in ['text', 'audio', 'both']:
                        output_mode = new_mode
                        print(f"✓ Output mode: {output_mode}\n")
                    else:
                        print("❌ Invalid mode. Use: text, audio, or both\n")
                    continue
                
                if user_input.lower().startswith('/context '):
                    new_context = user_input.split()[1].lower()
                    if new_context in ['medical', 'general', 'technical']:
                        context = new_context
                        print(f"✓ Context: {context}\n")
                    else:
                        print("❌ Invalid context\n")
                    continue
                
                if user_input.lower() == '/save':
                    auto_save = not auto_save
                    print(f"✓ Auto-save: {'ON' if auto_save else 'OFF'}\n")
                    continue
                
                # Detect input type
                if user_input.lower().startswith('audio:'):
                    input_type = 'audio'
                    input_data = user_input[6:].strip()
                    
                    if not os.path.exists(input_data):
                        print(f"❌ File not found: {input_data}\n")
                        continue
                else:
                    input_type = 'text'
                    input_data = user_input
                
                # Process
                result = self.communicate(
                    input_data,
                    input_type=input_type,
                    output_type=output_mode,
                    context=context,
                    save_conversation=auto_save
                )
                
                if result['success']:
                    conversation_count += 1
                    
                    # Display response
                    print(f"\n{'─'*60}")
                    print(f"Bot: {result['text_response']}")
                    
                    if result.get('audio_response'):
                        print(f"🔊 Audio: {result['audio_response']}")
                    
                    if result.get('saved_file'):
                        print(f"💾 Saved: {result['saved_file']}")
                    
                    print('─'*60 + "\n")
                else:
                    print(f"\n❌ Error: {result.get('error', 'Unknown error')}\n")
                
            except KeyboardInterrupt:
                print(f"\n\n👋 Goodbye! Total conversations: {conversation_count}")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
    
    def quick_test(self):
        """Quick test of all modes"""
        print("\n" + "="*60)
        print("🧪 QUICK TEST - ALL MODES")
        print("="*60)
        
        tests = [
            {
                'name': 'Text → Text',
                'input': 'എനിക്ക് പനിയുണ്ട്',
                'input_type': 'text',
                'output_type': 'text'
            },
            {
                'name': 'Text → Audio',
                'input': 'Hello, how are you?',
                'input_type': 'text',
                'output_type': 'audio'
            }
        ]
        
        for i, test in enumerate(tests, 1):
            print(f"\n{i}. Testing {test['name']}...")
            print("─"*60)
            
            result = self.communicate(
                test['input'],
                input_type=test['input_type'],
                output_type=test['output_type'],
                context='general'
            )
            
            if result['success']:
                print(f"✅ {test['name']} - SUCCESS")
                print(f"   Input: {result['user_input']}")
                print(f"   Output: {result['text_response']}")
                if result.get('audio_response'):
                    print(f"   Audio: {result['audio_response']}")
            else:
                print(f"❌ {test['name']} - FAILED")
                print(f"   Error: {result.get('error')}")
        
        print("\n" + "="*60)
        print("TEST COMPLETE")
        print("="*60)


# ============================================================
# SIMPLE WRAPPER FUNCTIONS
# ============================================================

def quick_chat(message, output_audio=False):
    """
    Ultra-simple one-line chat
    
    Usage:
        response = quick_chat("എനിക്ക് സഹായം വേണം")
        response = quick_chat("Hello", output_audio=True)
    """
    bot = UnifiedCommunicationBot(use_ollama=True)
    result = bot.communicate(
        message,
        input_type='text',
        output_type='audio' if output_audio else 'text'
    )
    
    if result['success']:
        if output_audio:
            return {
                'text': result['text_response'],
                'audio': result.get('audio_response')
            }
        else:
            return result['text_response']
    return None


def quick_transcribe(audio_file):
    """
    Ultra-simple audio transcription
    
    Usage:
        text = quick_transcribe("audio.mp3")
    """
    if AUDIO_BOT_AVAILABLE:
        return simple_transcribe(audio_file)
    return None


def quick_translate_text(text, to_malayalam=True):
    """
    Ultra-simple translation
    
    Usage:
        ml = quick_translate_text("Hello", to_malayalam=True)
        en = quick_translate_text("നമസ്കാരം", to_malayalam=False)
    """
    if TEXT_BOT_AVAILABLE:
        return simple_translate(text, to_malayalam)
    return None


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 UNIFIED COMMUNICATION SYSTEM")
    print("="*60)
    print("\nIntegrated Systems:")
    print(f"  • Text-to-Text (google_TT.py): {'✓' if TEXT_BOT_AVAILABLE else '❌'}")
    print(f"  • Audio System (googlev_audio.py): {'✓' if AUDIO_BOT_AVAILABLE else '❌'}")
    
    if not TEXT_BOT_AVAILABLE and not AUDIO_BOT_AVAILABLE:
        print("\n❌ ERROR: No subsystems available!")
        print("\nRequired files:")
        print("  - google_TT.py (text-to-text)")
        print("  - googlev_audio.py (audio system)")
        sys.exit(1)
    
    # Check AI backend
    try:
        import requests
        requests.get("http://localhost:11434/api/version", timeout=2)
        ollama_available = True
        print("  • AI Backend (Ollama): ✓")
    except:
        ollama_available = False
        print("  • AI Backend (Ollama): ❌ (using fallback)")
    
    # Initialize unified bot
    print("\n" + "="*60)
    bot = UnifiedCommunicationBot(use_ollama=ollama_available)
    
    print("\n" + "="*60)
    print("CHOOSE MODE")
    print("="*60)
    print("\n1. Interactive Chat (All modes)")
    print("2. Quick Test (Test all features)")
    print("3. Text → Text")
    print("4. Text → Audio")
    print("5. Audio → Text")
    print("6. Audio → Audio")
    print("7. Exit")
    
    choice = input("\nChoice (1-7): ").strip()
    
    if choice == '1':
        bot.interactive_chat()
    
    elif choice == '2':
        bot.quick_test()
    
    elif choice == '3':
        if TEXT_BOT_AVAILABLE:
            text = input("\nYour message: ").strip()
            result = bot.text_to_text(text)
            if result['success']:
                print(f"\nBot: {result['text_response']}")
        else:
            print("❌ Text system not available")
    
    elif choice == '4':
        if TEXT_BOT_AVAILABLE and AUDIO_BOT_AVAILABLE:
            text = input("\nYour message: ").strip()
            result = bot.text_to_audio(text)
            if result['success']:
                print(f"\nBot: {result['text_response']}")
                print(f"🔊 Audio: {result['audio_response']}")
        else:
            print("❌ Required systems not available")
    
    elif choice == '5':
        if AUDIO_BOT_AVAILABLE:
            audio_file = input("\nAudio file path: ").strip()
            result = bot.audio_to_text(audio_file)
            if result['success']:
                print(f"\nTranscribed: {result['user_input']}")
                print(f"Bot: {result['text_response']}")
        else:
            print("❌ Audio system not available")
    
    elif choice == '6':
        if AUDIO_BOT_AVAILABLE:
            audio_file = input("\nAudio file path: ").strip()
            result = bot.audio_to_audio(audio_file)
            if result['success']:
                print(f"\nTranscribed: {result['user_input']}")
                print(f"Bot: {result['text_response']}")
                print(f"🔊 Audio: {result['audio_response']}")
        else:
            print("❌ Audio system not available")
    
    else:
        print("\n👋 Exiting...")
    
    print("\n" + "="*60)
    print("Unified Communication System - Complete")
    print("="*60)
