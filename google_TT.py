"""
text_to_text_bot.py
Complete TEXT-based communication system
Complements the audio system with pure text interface
"""
from deep_translator import GoogleTranslator
import os
from datetime import datetime
import requests
import json

class TextToTextBot:
    def __init__(self, use_ollama=False):
        """
        Initialize text communication system
        
        Args:
            use_ollama: Enable AI backend
        """
        print("Initializing Text-to-Text Bot...")
        
        # Google Translate
        self.translator_en_to_ml = GoogleTranslator(source='en', target='ml')
        self.translator_ml_to_en = GoogleTranslator(source='ml', target='en')
        
        # Auto-detect translator
        self.auto_translator = GoogleTranslator(source='auto', target='en')
        
        self.use_ollama = use_ollama
        
        # Create folders for logs
        os.makedirs("conversations", exist_ok=True)
        os.makedirs("transcripts", exist_ok=True)
        
        print("✓ Google Translate ready")
        print("✓ System ready!\n")
    
    # ============================================================
    # LANGUAGE DETECTION & TRANSLATION
    # ============================================================
    
    def detect_language(self, text):
        """Detect if text is Malayalam or English"""
        malayalam_chars = 'അആഇഈഉഊഋഎഏഐഒഓഔകഖഗഘങചഛജഝഞടഠഡഢണതഥദധനപഫബഭമയരലവശഷസഹളഴറ'
        
        if any(c in malayalam_chars for c in text):
            return 'ml'
        elif text.isascii():
            return 'en'
        else:
            # Try auto-detect
            try:
                detected = GoogleTranslator(source='auto', target='en').translate(text)
                return 'ml' if detected != text else 'en'
            except:
                return 'en'
    
    def translate_to_malayalam(self, english_text):
        """English → Malayalam"""
        try:
            translated = self.translator_en_to_ml.translate(english_text)
            return translated if translated else english_text
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return english_text
    
    def translate_to_english(self, malayalam_text):
        """Malayalam → English"""
        try:
            translated = self.translator_ml_to_en.translate(malayalam_text)
            return translated if translated else malayalam_text
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return malayalam_text
    
    def auto_translate_to_english(self, text):
        """Auto-detect language and translate to English"""
        try:
            translated = self.auto_translator.translate(text)
            return translated if translated else text
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            return text
    
    # ============================================================
    # AI PROCESSING
    # ============================================================
    
    def query_ollama(self, english_text, context="general"):
        """
        Query AI backend with context
        
        Args:
            english_text: Question in English
            context: Context type ('medical', 'general', 'technical')
        """
        if not self.use_ollama:
            return None
        
        try:
            # Customize prompt based on context
            if context == "medical":
                prompt = f"Medical query: {english_text}\n\nProvide a brief, helpful response:"
            elif context == "technical":
                prompt = f"Technical question: {english_text}\n\nProvide a clear explanation:"
            else:
                prompt = f"Question: {english_text}\n\nProvide a helpful response:"
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama2",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["response"]
            else:
                return None
                
        except Exception as e:
            print(f"⚠️ AI not available: {e}")
            return None
    
    def get_fallback_response(self, english_query, context="general"):
        """Generate fallback response when AI is not available"""
        
        # Simple keyword-based responses
        query_lower = english_query.lower()
        
        if context == "medical":
            if any(word in query_lower for word in ['fever', 'pain', 'sick', 'ill']):
                return "I understand you're not feeling well. Please consult a healthcare provider for proper medical advice."
            elif any(word in query_lower for word in ['medicine', 'drug', 'medication']):
                return "Please consult a doctor or pharmacist about medications. They can provide proper guidance."
            else:
                return "For medical concerns, please consult a qualified healthcare professional."
        
        elif context == "technical":
            return "I'm here to help with technical questions. Could you provide more details about what you need help with?"
        
        else:
            return "I'm here to help! Could you provide more details about your question?"
    
    # ============================================================
    # TEXT PROCESSING PIPELINE
    # ============================================================
    
    def process_text(self, user_input, context="general", respond_in_malayalam=True):
        """
        COMPLETE PIPELINE: Text → Translation → AI → Response
        
        Args:
            user_input: User's text input (any language)
            context: Context type ('medical', 'general', 'technical')
            respond_in_malayalam: Return response in Malayalam
        
        Returns:
            dict: Complete conversation result
        """
        print(f"\n{'🔄'*30}")
        print("PROCESSING TEXT INPUT")
        print(f"{'🔄'*30}\n")
        
        # Step 1: Detect language
        print("Step 1: Detecting language...")
        user_language = self.detect_language(user_input)
        print(f"✓ Detected: {user_language}")
        print(f"👤 User: {user_input}")
        
        # Step 2: Translate to English if needed
        if user_language == 'ml':
            print("\nStep 2: Translating to English...")
            english_query = self.translate_to_english(user_input)
            print(f"🔄 English: {english_query}")
        else:
            english_query = user_input
            print("\nStep 2: Already in English, skipping translation")
        
        # Step 3: Get AI response
        print("\nStep 3: Getting AI response...")
        ai_response = self.query_ollama(english_query, context)
        
        if ai_response is None:
            ai_response = self.get_fallback_response(english_query, context)
            print(f"💭 Fallback: {ai_response}")
        else:
            print(f"🤖 AI: {ai_response}")
        
        # Step 4: Translate response if needed
        if respond_in_malayalam:
            print("\nStep 4: Translating response to Malayalam...")
            malayalam_response = self.translate_to_malayalam(ai_response)
            print(f"✅ Malayalam: {malayalam_response}")
            final_response = malayalam_response
        else:
            print("\nStep 4: Keeping response in English")
            final_response = ai_response
        
        print(f"\n{'✅'*30}")
        print("COMPLETE!")
        print(f"{'✅'*30}\n")
        
        result = {
            'success': True,
            'user_input': user_input,
            'user_language': user_language,
            'english_query': english_query,
            'ai_response_english': ai_response,
            'final_response': final_response,
            'response_language': 'ml' if respond_in_malayalam else 'en',
            'context': context,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    # ============================================================
    # CONVERSATION MANAGEMENT
    # ============================================================
    
    def save_conversation(self, conversation_result, filename=None):
        """
        Save conversation to file
        
        Args:
            conversation_result: Result from process_text()
            filename: Output filename (auto-generated if None)
        
        Returns:
            str: Path to saved file
        """
        try:
            if filename is None:
                timestamp = int(datetime.now().timestamp())
                filename = f"conversations/conversation_{timestamp}.txt"
            
            # Save as text file
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("="*60 + "\n")
                f.write("CONVERSATION LOG\n")
                f.write("="*60 + "\n\n")
                f.write(f"Timestamp: {conversation_result['timestamp']}\n")
                f.write(f"Context: {conversation_result['context']}\n")
                f.write(f"User Language: {conversation_result['user_language']}\n")
                f.write(f"Response Language: {conversation_result['response_language']}\n\n")
                f.write("="*60 + "\n")
                f.write("USER INPUT:\n")
                f.write("="*60 + "\n")
                f.write(f"{conversation_result['user_input']}\n\n")
                
                if conversation_result['user_language'] == 'ml':
                    f.write("ENGLISH TRANSLATION:\n")
                    f.write(f"{conversation_result['english_query']}\n\n")
                
                f.write("="*60 + "\n")
                f.write("BOT RESPONSE:\n")
                f.write("="*60 + "\n")
                f.write(f"{conversation_result['final_response']}\n\n")
                
                if conversation_result['response_language'] == 'ml':
                    f.write("ENGLISH VERSION:\n")
                    f.write(f"{conversation_result['ai_response_english']}\n\n")
                
                f.write("="*60 + "\n")
            
            # Also save as JSON
            json_filename = filename.replace('.txt', '.json')
            with open(json_filename, 'w', encoding='utf-8') as f:
                json.dump(conversation_result, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Conversation saved:")
            print(f"   Text: {filename}")
            print(f"   JSON: {json_filename}\n")
            
            return filename
            
        except Exception as e:
            print(f"❌ Save error: {e}")
            return None
    
    def load_conversation_history(self, filename):
        """Load previous conversation from file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                if filename.endswith('.json'):
                    return json.load(f)
                else:
                    return {'text': f.read()}
        except Exception as e:
            print(f"❌ Load error: {e}")
            return None
    
    # ============================================================
    # INTERACTIVE MODES
    # ============================================================
    
    def interactive_mode(self, context="general"):
        """
        Interactive text chat mode
        
        Args:
            context: Default context ('medical', 'general', 'technical')
        """
        print("\n" + "="*60)
        print("💬 INTERACTIVE TEXT MODE")
        print("="*60)
        print(f"\nContext: {context.upper()}")
        print("\nCommands:")
        print("  - Type your message in English or Malayalam")
        print("  - '/context medical' - Switch to medical context")
        print("  - '/context general' - Switch to general context")
        print("  - '/context technical' - Switch to technical context")
        print("  - '/english' - Toggle English responses")
        print("  - '/malayalam' - Toggle Malayalam responses")
        print("  - '/save' - Save conversation")
        print("  - '/history' - Show conversation history")
        print("  - '/exit' - Quit\n")
        
        respond_in_malayalam = True
        conversation_history = []
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                # Commands
                if user_input.lower() == '/exit':
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.lower().startswith('/context '):
                    new_context = user_input.split()[1].lower()
                    if new_context in ['medical', 'general', 'technical']:
                        context = new_context
                        print(f"✓ Context changed to: {context}\n")
                    else:
                        print("❌ Invalid context. Use: medical, general, or technical\n")
                    continue
                
                if user_input.lower() == '/english':
                    respond_in_malayalam = False
                    print("✓ Responses will be in English\n")
                    continue
                
                if user_input.lower() == '/malayalam':
                    respond_in_malayalam = True
                    print("✓ Responses will be in Malayalam\n")
                    continue
                
                if user_input.lower() == '/save':
                    if conversation_history:
                        timestamp = int(datetime.now().timestamp())
                        filename = f"conversations/session_{timestamp}.json"
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(conversation_history, f, ensure_ascii=False, indent=2)
                        print(f"✓ Conversation saved: {filename}\n")
                    else:
                        print("❌ No conversation to save\n")
                    continue
                
                if user_input.lower() == '/history':
                    if conversation_history:
                        print("\n" + "─"*60)
                        print("CONVERSATION HISTORY")
                        print("─"*60)
                        for i, conv in enumerate(conversation_history, 1):
                            print(f"\n{i}. You: {conv['user_input']}")
                            print(f"   Bot: {conv['final_response']}")
                        print("─"*60 + "\n")
                    else:
                        print("❌ No conversation history\n")
                    continue
                
                # Process message
                result = self.process_text(
                    user_input, 
                    context=context,
                    respond_in_malayalam=respond_in_malayalam
                )
                
                if result['success']:
                    print(f"Bot: {result['final_response']}\n")
                    conversation_history.append(result)
                else:
                    print("❌ Error processing message\n")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")
    
    def batch_process(self, text_list, context="general", respond_in_malayalam=True):
        """
        Process multiple texts in batch
        
        Args:
            text_list: List of text inputs
            context: Context type
            respond_in_malayalam: Return responses in Malayalam
        
        Returns:
            list: List of conversation results
        """
        print(f"\n{'='*60}")
        print(f"📁 BATCH PROCESSING: {len(text_list)} texts")
        print(f"{'='*60}\n")
        
        results = []
        
        for i, text in enumerate(text_list, 1):
            print(f"Processing {i}/{len(text_list)}: {text[:50]}...")
            
            result = self.process_text(
                text,
                context=context,
                respond_in_malayalam=respond_in_malayalam
            )
            
            if result['success']:
                results.append(result)
                print(f"✓ Response: {result['final_response'][:50]}...\n")
        
        print(f"{'='*60}")
        print(f"✅ Batch complete: {len(results)}/{len(text_list)} successful")
        print(f"{'='*60}\n")
        
        return results
    
    def quick_translate(self, text, to_language='ml'):
        """
        Quick translation without AI processing
        
        Args:
            text: Text to translate
            to_language: Target language ('ml' or 'en')
        
        Returns:
            str: Translated text
        """
        try:
            if to_language == 'ml':
                return self.translate_to_malayalam(text)
            else:
                return self.translate_to_english(text)
        except Exception as e:
            print(f"❌ Translation error: {e}")
            return text


# ============================================================
# SIMPLE USAGE FUNCTIONS
# ============================================================

def simple_chat(user_text, respond_in_malayalam=True):
    """
    Simple one-line chat function
    
    Usage:
        response = simple_chat("എനിക്ക് സഹായം വേണം")
        print(response)
    """
    bot = TextToTextBot(use_ollama=True)
    result = bot.process_text(user_text, respond_in_malayalam=respond_in_malayalam)
    return result['final_response'] if result['success'] else None


def simple_translate(text, to_malayalam=True):
    """
    Simple one-line translation
    
    Usage:
        malayalam = simple_translate("Hello, how are you?", to_malayalam=True)
        english = simple_translate("എങ്ങനെയുണ്ട്", to_malayalam=False)
    """
    bot = TextToTextBot()
    return bot.quick_translate(text, 'ml' if to_malayalam else 'en')


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("💬 TEXT-TO-TEXT MALAYALAM COMMUNICATION")
    print("="*60)
    print("\nComplete System:")
    print("  1. Text Input (Malayalam/English)")
    print("  2. Auto Translation")
    print("  3. AI Processing")
    print("  4. Response (Malayalam/English)")
    
    # Check Ollama
    try:
        requests.get("http://localhost:11434/api/version", timeout=2)
        ollama_available = True
        print("  • AI Backend: Available")
    except:
        ollama_available = False
        print("  • AI Backend: Not available (using fallback)")
    
    # Initialize
    bot = TextToTextBot(use_ollama=ollama_available)
    
    print("\n" + "="*60)
    print("CHOOSE MODE")
    print("="*60)
    print("\n1. Interactive Chat (General)")
    print("2. Interactive Chat (Medical)")
    print("3. Interactive Chat (Technical)")
    print("4. Quick Translation")
    print("5. Batch Process Texts")
    print("6. Single Query")
    print("7. Exit")
    
    choice = input("\nChoice (1-7): ").strip()
    
    if choice == '1':
        bot.interactive_mode(context="general")
    
    elif choice == '2':
        bot.interactive_mode(context="medical")
    
    elif choice == '3':
        bot.interactive_mode(context="technical")
    
    elif choice == '4':
        print("\n" + "─"*60)
        print("QUICK TRANSLATION")
        print("─"*60)
        text = input("\nEnter text to translate: ").strip()
        direction = input("To Malayalam (m) or English (e)? ").strip().lower()
        
        if direction == 'm':
            result = bot.quick_translate(text, 'ml')
            print(f"\nMalayalam: {result}")
        else:
            result = bot.quick_translate(text, 'en')
            print(f"\nEnglish: {result}")
    
    elif choice == '5':
        print("\n" + "─"*60)
        print("BATCH PROCESSING")
        print("─"*60)
        print("\nEnter texts (one per line, empty line to finish):")
        
        texts = []
        while True:
            line = input("> ").strip()
            if not line:
                break
            texts.append(line)
        
        if texts:
            context = input("\nContext (medical/general/technical): ").strip().lower()
            if context not in ['medical', 'general', 'technical']:
                context = 'general'
            
            results = bot.batch_process(texts, context=context)
            
            print("\n" + "─"*60)
            print("RESULTS")
            print("─"*60)
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Input: {result['user_input']}")
                print(f"   Output: {result['final_response']}")
    
    elif choice == '6':
        print("\n" + "─"*60)
        print("SINGLE QUERY")
        print("─"*60)
        text = input("\nYour message: ").strip()
        context = input("Context (medical/general/technical): ").strip().lower()
        if context not in ['medical', 'general', 'technical']:
            context = 'general'
        
        respond_ml = input("Response in Malayalam? (y/n): ").strip().lower()
        
        result = bot.process_text(
            text,
            context=context,
            respond_in_malayalam=(respond_ml == 'y')
        )
        
        if result['success']:
            print("\n" + "─"*60)
            print("RESPONSE")
            print("─"*60)
            print(f"You: {result['user_input']}")
            print(f"Bot: {result['final_response']}")
            print("─"*60)
            
            save = input("\nSave conversation? (y/n): ").strip().lower()
            if save == 'y':
                bot.save_conversation(result)
    
    else:
        print("\n👋 Exiting...")
    
    print("\n" + "="*60)
    print("Complete text-to-text communication system")
    print("="*60)
