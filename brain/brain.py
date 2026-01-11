import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama

# --- TASK: THE LIBRARIAN ---
def build_medical_database():
    print("--- 📚 Starting Database Build ---")
    all_chunks = []
    # Using absolute path to be 100% sure we find the folder
    docs_folder = os.path.join(os.getcwd(), "medical_docs")
    
    if not os.path.exists(docs_folder):
        print(f"❌ ERROR: Folder not found at {docs_folder}")
        return

    files = [f for f in os.listdir(docs_folder) if f.endswith(".pdf")]
    print(f"📂 Found {len(files)} PDF files in the folder.")

    for filename in files:
        print(f"📄 Reading: {filename}...")
        try:
            loader = PyPDFLoader(os.path.join(docs_folder, filename))
            data = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
            chunks = text_splitter.split_documents(data)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"⚠️ Failed to read {filename}: {e}")
    
    if not all_chunks:
        print("❌ ERROR: No text could be extracted from your PDFs.")
        return

    print(f"🧠 Converting {len(all_chunks)} text chunks into vectors...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    Chroma.from_documents(all_chunks, embeddings, persist_directory="./hospital_knowledge_base")
    print("--- ✅ SUCCESS: Database is built and saved! ---")

# --- TASK: THE REASONING ENGINE ---
def query_post_discharge_guardian(user_query):
    # Safety Check first
    red_flags = ["chest pain", "bleeding", "breathless", "unconscious"]
    if any(flag in user_query.lower() for flag in red_flags):
        return "⚠️ EMERGENCY: This is a red flag. Contact your surgeon immediately."

    if not os.path.exists("./hospital_knowledge_base"):
        return "❌ ERROR: The AI has no memory. You must run the build function first."

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma(persist_directory="./hospital_knowledge_base", embedding_function=embeddings)
    relevant_docs = db.similarity_search(user_query, k=2)
    
    if not relevant_docs:
        return "🔍 No matching info found in the medical docs."

    context = "\n\n".join([d.page_content for d in relevant_docs])
    llm = Ollama(model="llama3:8b", temperature=0) 
    prompt = f"Answer based ONLY on context: {context}\nQuestion: {user_query}"
    
    return llm.invoke(prompt)

# --- EXECUTION ---
if __name__ == "__main__":
    # STEP 1: Ensure database is built (ONLY uncomment if you have new PDFs)
    build_medical_database() 

    print("\n" + "="*50)
    print("🛡️ YODHA AI: POST-DISCHARGE GUARDIAN ACTIVE")
    print("Type 'exit' or 'quit' to stop the session.")
    print("="*50)

    # This 'while True' loop keeps the program running for follow-up questions
    while True:
        user_input = input("\n👤 Patient Query: ")

        # Exit condition
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Stay safe. Closing Guardian session...")
            break

        if not user_input.strip():
            continue

        print("🧠 Thinking...")
        
        # Call your existing reasoning engine
        response = query_post_discharge_guardian(user_input)
        
        print(f"\n✨ RESPONSE:\n{response}")
        print("-" * 30)