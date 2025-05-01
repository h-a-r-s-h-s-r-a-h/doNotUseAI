import os
from dotenv import load_dotenv
import spacy
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

def test_imports():
    print("Testing imports...")
    try:
        # Test spaCy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy loaded successfully")
        
        # Test Google AI
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("❌ GOOGLE_API_KEY not found in .env file")
        else:
            genai.configure(api_key=api_key)
            print("✅ Google AI configured successfully")
            
        # Test LangChain
        model = ChatGoogleGenerativeAI(model="gemini-pro")
        print("✅ LangChain initialized successfully")
        
        print("\nAll basic imports are working!")
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        return False

if __name__ == "__main__":
    test_imports() 