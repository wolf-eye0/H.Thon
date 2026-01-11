import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama

# --- 1. GLOBAL INITIALIZATION (Loads ONCE at start) ---
print("🔋 Powering up Yodha AI Engines...")

# Load these once globally so the functions can see them
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
llm = Ollama(model="llama3:8b", temperature=0)

# Connect to the database globally
db_path = "./hospital_knowledge_base"
if os.path.exists(db_path):
    db = Chroma(persist_directory=db_path, embedding_function=embeddings)
else:
    db = None
    print("⚠️ Warning: Database folder not found.")

# --- 2. REASONING ENGINE ---
def query_post_discharge_guardian(user_query, history):
    # 1. SAFETY GATE (Highest Priority) [cite: 616, 626]
    red_flags = ["chest pain", "bleeding", "breathless", "heartbeat", "fluttering"]
    if any(flag in user_query.lower() for flag in red_flags):
        return "⚠️ EMERGENCY: This sounds critical. Please contact your doctor immediately."

    # 2. INCREASE RETRIEVAL (k=5)
    # This ensures Arthur's specific chunks aren't pushed out by general guide text.
    relevant_docs = db.similarity_search(user_query, k=5)
    
    # Separating context to help the LLM see the difference between "Rules" and "Facts"
    patient_facts = ""
    general_rules = ""
    
    for doc in relevant_docs:
        source = doc.metadata.get('source', '')
        if "Portfolio" in source or "person" in source:
            patient_facts += f"\n{doc.page_content}"
        else:
            general_rules += f"\n{doc.page_content}"

    # 3. THE "STRICT IDENTITY" PROMPT 
    # We explicitly tell the AI to trust 'Patient Facts' over 'General Rules'
    prompt = f"""
    SYSTEM PERSONA: You are a Medical Guardian for Arthur Pendelton.
    STRICT RULE: Only use the 'Patient Facts' for specific dates, medications, and history.
    If 'Patient Facts' contradicts 'General Rules', Arthur's facts are the TRUTH.

    [CONVERSATION HISTORY]
    {history[-1500:]}

    [PATIENT FACTS (ARTHUR'S PORTFOLIO)]
    {patient_facts}

    [GENERAL RECOVERY RULES]
    {general_rules}

    USER QUESTION: {user_query}
    ASSISTANT RESPONSE (Be direct and fact-based):"""
    
    return llm.invoke(prompt)

# --- 3. EXECUTION LOOP ---
if __name__ == "__main__":
    chat_history = ""
    print("\n🛡️ GUARDIAN ACTIVE (Arthur Pendelton Mode)")
    
    while True:
        user_input = input("\n👤 Patient: ")
        if user_input.lower() in ["exit", "quit"]: break

        print("🧠 Thinking...")
        response = query_post_discharge_guardian(user_input, chat_history)
        chat_history += f"Patient: {user_input}\nAssistant: {response}\n"
        print(f"\n✨ RESPONSE:\n{response}")