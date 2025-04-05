import streamlit as st
import os
from dotenv import load_dotenv
from components.chat_interface import ChatInterface
from services.bot_service import BotService
from utils.config import setup_page_config
import io

# Load environment variables
load_dotenv()

def main():
    # Setup page configuration
    setup_page_config()
    
    # Initialize session state if not exists
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "uploaded_doc" not in st.session_state:
        st.session_state.uploaded_doc = None
    
    if "bot_service" not in st.session_state:
        st.session_state.bot_service = BotService()

    # Display header
    st.title("Mark Musk - CreditChek API Assistant")
    
    # Add sidebar for document upload
    with st.sidebar:
        st.header("Documentation Upload")
        st.write("Upload CreditChek documentation to improve responses.")
        
        uploaded_file = st.file_uploader("Upload documentation (PDF/TXT)", type=["pdf", "txt"])
        
        if uploaded_file is not None and (st.session_state.uploaded_doc != uploaded_file.name):
            st.session_state.uploaded_doc = uploaded_file.name
            
            # Process the uploaded file
            file_content = uploaded_file.read()
            file_type = uploaded_file.type
            
            with st.spinner("Processing documentation..."):
                # Update the bot service with the new documentation
                st.session_state.bot_service.process_uploaded_document(file_content, file_type, uploaded_file.name)
                st.success(f"Documentation processed: {uploaded_file.name}")
    
    st.markdown("""
    Welcome to Mark Musk, your AI assistant for CreditChek API integration! 
    Ask me anything about:
    - API endpoints and their usage
    - Sample code in Python, NodeJS, PHP Laravel, or GoLang
    - Best practices for integration
    - Error handling and troubleshooting
    """)

    # Initialize chat interface
    chat_interface = ChatInterface()
    
    # Display chat messages
    chat_interface.display_chat_history()
    
    # Get user input
    if prompt := st.chat_input("Ask me about CreditChek API..."):
        chat_interface.handle_user_input(prompt)

if __name__ == "__main__":
    main() 