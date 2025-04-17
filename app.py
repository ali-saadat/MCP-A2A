import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
import google.generativeai as genai
from pathlib import Path
import json
import uuid
from adk_agents import setup_showcase_agents, simulate_multi_agent_interaction
from generate_diagrams import create_a2a_architecture_diagram, create_a2a_architecture_overview_diagram

# Set page configuration
st.set_page_config(
    page_title="A2A and MCP Protocol Interactive Showcase",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for persistence
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"
    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
    
if "mcp_enabled" not in st.session_state:
    st.session_state.mcp_enabled = True
    
if "api_key" not in st.session_state:
    st.session_state.api_key = None
    
if "visited_pages" not in st.session_state:
    st.session_state.visited_pages = set()
    
if "completed_sections" not in st.session_state:
    st.session_state.completed_sections = {}

if "agent_registry" not in st.session_state:
    st.session_state.agent_registry = None
    
if "navigate_to" not in st.session_state:
    st.session_state.navigate_to = None
    
# Navigation helper functions
def navigate_to(page):
    st.session_state.navigate_to = page
    st.rerun()

# API Key Management
def check_api_key():
    """Check if API key is available in .env file or session state"""
    # First try to load from .env file
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    
    # If found in .env, save to session state
    if api_key and "api_key" not in st.session_state:
        try:
            st.session_state.api_key = api_key
            # Validate the key and get available models
            is_valid, result = validate_api_key(api_key)
            if is_valid:
                st.session_state.available_models = result
                st.session_state.selected_model = result[0] if result else "gemini-pro"
                return True
            else:
                st.session_state.api_key = None
                return False
        except Exception as e:
            try:
                print(f"Error validating API key from .env: {str(e)}")
            except:
                pass
            st.session_state.api_key = None
            return False
    
    # Return True if key exists in session state
    return "api_key" in st.session_state and st.session_state.api_key is not None

def validate_api_key(api_key):
    """Validate API key by listing available models"""
    try:
        genai.configure(api_key=api_key)
        # List available models instead of making a test call
        models = genai.list_models()
        # Extract just the model name without the full path
        available_models = []
        for model in models:
            # Check if model supports generateContent
            if hasattr(model, 'supported_generation_methods') and 'generateContent' in model.supported_generation_methods:
                # Extract the model name from the full path (e.g., models/gemini-pro)
                model_name = model.name.split('/')[-1] if '/' in model.name else model.name
                available_models.append(model_name)
        
        # If no models support generateContent, use the full names
        if not available_models:
            available_models = [model.name for model in models]
            
        # Log the available models for debugging
        try:
            print(f"Found {len(available_models)} available models: {available_models}")
        except:
            # Ignore print errors
            pass
        
        return True, available_models
    except Exception as e:
        error_msg = str(e)
        try:
            print(f"API key validation error: {error_msg}")
        except:
            # Ignore print errors
            pass
        return False, error_msg

def api_key_input():
    """Display API key input form"""
    st.header("API Key Setup")
    
    st.markdown("""
    To use this application with real functionality, you need to provide a Google API key 
    with access to the Gemini models.
    
    You can obtain a key from the [Google AI Studio](https://makersuite.google.com/).
    """)
    
    api_key = st.text_input(
        "Enter your Google API Key:",
        type="password",
        help="Enter the key as a plain string without quotes or formatting",
        placeholder="AIza..."
    )
    
    save_to_env = st.checkbox("Save to .env file for future use", value=True)
    
    if st.button("Submit API Key"):
        if not api_key:
            st.error("Please enter a valid API key")
            return False
        
        with st.spinner("Validating API key and fetching available models..."):
            # Validate the API key
            is_valid, result = validate_api_key(api_key)
            
            if is_valid:
                # Save to session state
                st.session_state.api_key = api_key
                
                # Save available models
                st.session_state.available_models = result
                
                # Set default model
                if result:
                    st.session_state.selected_model = result[0]
                else:
                    st.session_state.selected_model = "gemini-pro"
                
                # Display available models
                st.success(f"✅ API key validated successfully!")
                st.subheader("Available Models:")
                for model in result:
                    st.info(f"- {model}")
                
                # Save to .env file if requested
                if save_to_env:
                    env_path = Path(".env")
                    if env_path.exists():
                        with open(env_path, "r") as f:
                            lines = f.readlines()
                        
                        # Check if GOOGLE_API_KEY already exists
                        key_exists = False
                        for i, line in enumerate(lines):
                            if line.startswith("GOOGLE_API_KEY="):
                                lines[i] = f"GOOGLE_API_KEY={api_key}\n"
                                key_exists = True
                                break
                        
                        # Add key if it doesn't exist
                        if not key_exists:
                            lines.append(f"GOOGLE_API_KEY={api_key}\n")
                        
                        # Write back to file
                        with open(env_path, "w") as f:
                            f.writelines(lines)
                    else:
                        # Create new .env file
                        with open(env_path, "w") as f:
                            f.write(f"GOOGLE_API_KEY={api_key}\n")
                    
                    st.success("API key saved to .env file")
                
                st.success("API key saved for this session")
                st.info("Please select a model from the sidebar to continue")
                st.rerun()
                
                return True
            else:
                st.error(f"❌ Invalid API key: {result}")
                st.markdown("""
                **Troubleshooting tips:**
                1. Make sure you've copied the entire key without any extra spaces
                2. Verify that your API key has access to Gemini models
                3. Check if you have billing enabled for your Google Cloud project
                4. Try generating a new API key from Google AI Studio
                """)
                return False
    
    return False

# Function to configure Gemini model
def configure_genai():
    """Configure and initialize Gemini model"""
    if not check_api_key():
        return None
    
    api_key = st.session_state.api_key
    
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"Error configuring API: {str(e)}")
        return None
    
    # Check if we have available models in session state
    if "available_models" not in st.session_state or not st.session_state.available_models:
        # Try to get available models
        try:
            is_valid, available_models = validate_api_key(api_key)
            if is_valid:
                st.session_state.available_models = available_models
            else:
                # If we can't get models, use default
                st.session_state.available_models = ["gemini-pro", "gemini-1.5-pro", "gemini-1.0-pro"]
        except Exception as e:
            # If we can't get models, use default
            st.session_state.available_models = ["gemini-pro", "gemini-1.5-pro", "gemini-1.0-pro"]
            st.warning(f"Could not retrieve model list: {str(e)}. Using default models.")
    
    # Use model selection if available, otherwise default to gemini-pro
    if "selected_model" not in st.session_state:
        # Default to gemini-pro as it's most widely available
        st.session_state.selected_model = "gemini-pro"
    
    # Initialize Gemini model
    try:
        # Always use the current selected model from session state
        model_name = st.session_state.selected_model
        st.session_state.current_model = model_name  # Track current model for display
        
        # Log model usage for debugging
        try:
            print(f"Using model: {model_name}")
        except:
            pass
        
        model = genai.GenerativeModel(model_name)
        return model
    except Exception as e:
        st.error(f"Error initializing Gemini model {st.session_state.selected_model}: {e}")
        st.info("Trying fallback to gemini-pro model...")
        try:
            model = genai.GenerativeModel("gemini-pro")
            # Update session state to reflect the fallback
            st.session_state.selected_model = "gemini-pro"
            st.session_state.current_model = "gemini-pro"
            return model
        except Exception as e2:
            st.error(f"Error initializing fallback model: {e2}")
            return None

# MCP Integration
# Import the improved MCP server and client from mcp_integration.py
from mcp_integration import CompanyDataMCPServer, CompanyDataMCPClient

# Setup MCP client and server
@st.cache_resource
def get_mcp_client():
    """Get MCP client instance"""
    data_path = os.path.join(os.path.dirname(__file__), "data", "company_data.json")
    server = CompanyDataMCPServer(data_path)
    client = CompanyDataMCPClient(server)
    return client

# Setup ADK-inspired agents
@st.cache_resource
def get_agent_registry():
    """Get agent registry with configured agents"""
    if st.session_state.agent_registry is None:
        # Configure Gemini model for agents
        model = configure_genai()
        # Setup showcase agents
        st.session_state.agent_registry = setup_showcase_agents(model)
    
    return st.session_state.agent_registry

# Function to generate response with Gemini
async def generate_response(prompt, use_mcp=False, query=""):
    """Generate response using Gemini model with optional MCP context. Returns debug info for UI."""
    model = configure_genai()
    if model is None:
        st.error("Gemini model not available. Please provide a valid API key.")
        return {
            "answer": "API key required to generate responses. Please provide a valid Google API key.",
            "mcp_context": None,
            "prompt": prompt,
            "raw_response": None
        }
    try:
        mcp_context = None
        used_prompt = prompt
        if use_mcp:
            mcp_client = get_mcp_client()
            mcp_response = await mcp_client.request_company_data(query)
            mcp_context = mcp_client.format_for_llm(mcp_response)
            used_prompt = f"{prompt}\n\nUse the following company information to help answer:\n{mcp_context}"
            response = model.generate_content(used_prompt)
        else:
            response = model.generate_content(prompt)
        # Return debug info
        return {
            "answer": getattr(response, 'text', str(response)),
            "mcp_context": mcp_context,
            "prompt": used_prompt,
            "raw_response": str(response)
        }
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return {
            "answer": f"Error generating response: {e}",
            "mcp_context": mcp_context if 'mcp_context' in locals() else None,
            "prompt": used_prompt if 'used_prompt' in locals() else prompt,
            "raw_response": None
        }

# Track page visit and mark as completed
def track_page_visit(page_key):
    """Track page visit in session state"""
    # Add to visited pages
    if isinstance(st.session_state.visited_pages, list):
        st.session_state.visited_pages = set(st.session_state.visited_pages)
    
    st.session_state.visited_pages.add(page_key)

# Mark section as completed
def mark_section_completed(section_key, subsection_key=None):
    """Mark section as completed in session state"""
    if section_key not in st.session_state.completed_sections:
        st.session_state.completed_sections[section_key] = set()
    
    if subsection_key:
        if isinstance(st.session_state.completed_sections[section_key], list):
            st.session_state.completed_sections[section_key] = set(st.session_state.completed_sections[section_key])
        
        st.session_state.completed_sections[section_key].add(subsection_key)

# Check if section is completed
def is_section_completed(section_key, subsection_key=None):
    """Check if section is completed in session state"""
    if section_key not in st.session_state.completed_sections:
        return False
    
    if subsection_key:
        if isinstance(st.session_state.completed_sections[section_key], list):
            st.session_state.completed_sections[section_key] = set(st.session_state.completed_sections[section_key])
        
        return subsection_key in st.session_state.completed_sections[section_key]
    
    return True

# Main navigation
def main_navigation():
    """Display main navigation sidebar"""
    st.sidebar.title("Navigation")
    
    # Main sections
    pages = {
        "home": "🏠 Home",
        "education": "📚 Educational Foundation",
        "mcp_showcase": "🔄 MCP Showcase",
        "a2a_showcase": "🤝 A2A Showcase",
        "integration": "🔗 Integration Example",
        "glossary": "📖 Terminology Glossary"
    }
    
    # Show progress indicators
    st.sidebar.markdown("### Your Progress")
    progress_items = []
    for page_key, page_name in pages.items():
        if page_key in st.session_state.visited_pages:
            progress_items.append(f"✅ {page_name}")
        else:
            progress_items.append(f"⬜ {page_name}")
    
    st.sidebar.markdown("\n".join(progress_items))
    st.sidebar.markdown("---")
    
    # Navigation selection
    selection = st.sidebar.radio("Go to", list(pages.values()))
    
    # Map selection back to page key
    for page_key, page_name in pages.items():
        if selection == page_name:
            st.session_state.current_page = page_key
            break
    
    # Display current page breadcrumb
    st.markdown(f"### {selection}")
    st.markdown("---")
    
    # Session management
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Session Management")
    
    # Display session ID
    st.sidebar.markdown(f"Session ID: `{st.session_state.session_id[:8]}...`")
    
    # Option to reset session
    if st.sidebar.button("Reset Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # API key management
    st.sidebar.markdown("---")
    st.sidebar.markdown("### API Key Management")
    
    if check_api_key():
        st.sidebar.success("API Key: ✓ Configured")
        
        # Show API key input in sidebar for easy changing
        new_api_key = st.sidebar.text_input(
            "Change API Key:",
            type="password",
            key="sidebar_api_key",
            help="Enter a new API key to change the current one"
        )
        
        if st.sidebar.button("Update API Key"):
            if new_api_key:
                with st.sidebar.spinner("Validating new API key..."):
                    # Validate the new API key
                    is_valid, result = validate_api_key(new_api_key)
                    
                    if is_valid:
                        # Save to session state
                        st.session_state.api_key = new_api_key
                        
                        # Save available models
                        st.session_state.available_models = result
                        
                        # Set default model
                        if result:
                            st.session_state.selected_model = result[0]
                        else:
                            st.session_state.selected_model = "gemini-pro"
                        
                        st.sidebar.success("✅ API key updated successfully!")
                        st.sidebar.info(f"Found {len(result)} available models")
                        st.rerun()
                    else:
                        st.sidebar.error(f"❌ Invalid API key: {result}")
        
        # Show selected model if available
        if "selected_model" in st.session_state:
            st.sidebar.info(f"Using model: {st.session_state.selected_model}")
            
            # Add model selection if we have available models
            if "available_models" in st.session_state and st.session_state.available_models:
                model_options = st.session_state.available_models
                selected_model = st.sidebar.selectbox(
                    "Select Gemini Model:",
                    options=model_options,
                    index=model_options.index(st.session_state.selected_model) if st.session_state.selected_model in model_options else 0,
                    key="sidebar_model_selector"
                )
                
                if selected_model != st.session_state.selected_model:
                    st.session_state.selected_model = selected_model
                    st.sidebar.success(f"Model changed to {selected_model}")
                    st.rerun()
    else:
        st.sidebar.warning("API Key: ✗ Not Configured")
        
        # Add quick API key input in sidebar
        quick_api_key = st.sidebar.text_input(
            "Enter API Key:",
            type="password",
            key="sidebar_quick_api_key",
            help="Enter your Google API key to enable model functionality"
        )
        
        if st.sidebar.button("Set API Key"):
            if quick_api_key:
                with st.spinner("Validating API key..."):
                    # Validate the API key
                    is_valid, result = validate_api_key(quick_api_key)
                    
                    if is_valid:
                        # Save to session state
                        st.session_state.api_key = quick_api_key
                        
                        # Save available models
                        st.session_state.available_models = result
                        
                        # Set default model
                        if result:
                            st.session_state.selected_model = result[0]
                        else:
                            st.session_state.selected_model = "gemini-pro"
                        
                        st.sidebar.success("✅ API key set successfully!")
                        st.sidebar.info(f"Found {len(result)} available models")
                        st.rerun()
                    else:
                        st.sidebar.error(f"❌ Invalid API key: {result}")

# Home page
def home_page():
    """Display home page"""
    st.title("A2A and MCP Protocol Interactive Showcase")
    
    # Track page visit
    track_page_visit("home")
    
    st.markdown("""
    Welcome to the interactive showcase for Agent-to-Agent (A2A) and Model Context Protocol (MCP).
    This application provides educational content and interactive demonstrations to help you understand
    these protocols and how they can be used together to create powerful AI agent systems.
    
    ### What you'll learn:
    
    - What A2A and MCP protocols are and their purpose in AI agent systems
    - How each protocol is structured and how they work
    - When to use each protocol and their key benefits
    - How these protocols can work together in integrated systems
    
    ### Getting Started:
    
    Use the navigation menu on the left to explore different sections of the application.
    We recommend starting with the Educational Foundation to understand the basics before
    moving on to the interactive showcases.
    """)
    
    # Quick navigation cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("### 📚 Educational Foundation")
        st.markdown("Learn the basics of A2A and MCP protocols")
    
    with col2:
        st.info("### 🔄 MCP Showcase")
        st.markdown("See MCP in action with interactive demonstrations")
    
    with col3:
        st.info("### 🤝 A2A Showcase")
        st.markdown("See A2A in action with agent communication")

# Educational Foundation page
def education_page():
    """Display educational foundation page"""
    st.title("Educational Foundation")
    
    # Track page visit
    track_page_visit("education")
    
    tab1, tab2, tab3 = st.tabs(["Protocol Overview", "Architecture Diagrams", "Protocol Comparison"])
    
    with tab1:
        st.header("Protocol Overview")
        
        st.subheader("Model Context Protocol (MCP)")
        st.markdown("""
        The Model Context Protocol (MCP) is a standardized way for Large Language Models (LLMs) to request and receive 
        external context from various data sources. Developed by Anthropic, MCP enables LLMs to:
        
        - Recognize when they need additional information
        - Request specific data from external sources
        - Incorporate that data into their reasoning process
        - Provide more accurate and informed responses
        
        MCP addresses the limitation of LLMs being restricted to their training data by creating a standardized 
        interface for accessing external, up-to-date information.
        """)
        
        st.subheader("Agent-to-Agent Protocol (A2A)")
        st.markdown("""
        The Agent-to-Agent (A2A) protocol, developed by Google, enables different AI agents to discover and 
        communicate with each other to accomplish tasks. A2A allows agents to:
        
        - Discover other agents and their capabilities
        - Delegate specialized tasks to appropriate agents
        - Track task status across multiple agents
        - Share context and results between agents
        
        A2A addresses the limitation of single agents trying to handle all tasks by enabling specialization 
        and collaboration between multiple purpose-built agents.
        """)
        
        # Mark subsection as completed
        mark_section_completed("education", "overview")
        if st.button("Mark Overview as Completed"):
            st.success("Protocol Overview section marked as completed!")
            st.rerun()
    
    with tab2:
        st.header("Interactive Protocol Architecture Diagrams")
        
        st.subheader("MCP Architecture")
        try:
            st.image("images/mcp_architecture.png", caption="MCP Architecture Overview")
        except Exception as e:
            st.error(f"Error loading image: {e}")
            st.image("https://miro.medium.com/v2/resize:fit:1400/format:webp/1*8wNWI9XYGQmGZlvwKrYhvQ.png", 
                     caption="MCP Architecture Overview (Fallback)")
        
        st.markdown("""
        The MCP architecture consists of three main components:
        
        1. **MCP Host**: The LLM that recognizes when it needs external information and makes requests
        2. **MCP Client**: The interface that receives requests from the LLM and forwards them to appropriate servers
        3. **MCP Server**: The system that provides access to external data sources and returns formatted information
        
        This architecture allows for a clean separation between the LLM's reasoning capabilities and the 
        external knowledge it can access.
        """)
        
        st.subheader("A2A Architecture")
        try:
            diagram_bytes = create_a2a_architecture_diagram()
            st.image(diagram_bytes, caption="Agent-to-Agent (A2A) Architecture", use_column_width=True)
        except Exception as e:
            st.error(f"Error generating or displaying diagram: {e}")
            st.image("https://storage.googleapis.com/gweb-cloudblog-publish/images/1_Agent_to_Agent_API_overview.max-2000x2000.jpg", 
                     caption="A2A Architecture (Fallback)")
        
        st.markdown("""
        The A2A architecture enables agent communication through:
        
        1. **Agent Cards**: Descriptions of agent capabilities and endpoints
        2. **Discovery Mechanism**: How agents find other agents with needed capabilities
        3. **Task Management**: How tasks are created, delegated, and tracked
        4. **Message Exchange**: Standardized format for communication between agents
        
        This architecture allows agents to collaborate effectively while maintaining clear boundaries and responsibilities.
        """)
        
        # Mark subsection as completed
        mark_section_completed("education", "architecture")
        if st.button("Mark Architecture as Completed"):
            st.success("Architecture Diagrams section marked as completed!")
            st.rerun()
    
    with tab3:
        st.header("Side-by-Side Protocol Comparison")
        
        comparison_data = {
            "Primary Purpose": ["Access external data and context", "Enable agent-to-agent communication"],
            "Main Components": ["Host, Client, Server", "Agent Cards, Task Management, Message Exchange"],
            "Problem Solved": ["Limited knowledge in LLM training data", "Limited capabilities of single agents"],
            "Data Flow": ["LLM ↔ External Data Sources", "Agent ↔ Agent"],
            "Use Case Example": ["Retrieving up-to-date company information", "Delegating specialized tasks to expert agents"]
        }
        
        # Create two columns for comparison
        col1, col2 = st.columns(2)
        
        # Headers
        col1.markdown("### MCP")
        col2.markdown("### A2A")
        
        # Content rows
        for category, values in comparison_data.items():
            col1.markdown(f"**{category}:**")
            col1.markdown(values[0])
            col1.markdown("---")
            
            col2.markdown(f"**{category}:**")
            col2.markdown(values[1])
            col2.markdown("---")
        
        # Mark subsection as completed
        mark_section_completed("education", "comparison")
        if st.button("Mark Comparison as Completed"):
            st.success("Protocol Comparison section marked as completed!")
            st.rerun()
    
    # Check if all subsections are completed
    if (is_section_completed("education", "overview") and 
        is_section_completed("education", "architecture") and 
        is_section_completed("education", "comparison")):
        st.success("🎉 Congratulations! You've completed the Educational Foundation module.")

# MCP Showcase page
def mcp_showcase_page():
    """Display MCP showcase page"""
    st.title("MCP Showcase")
    
    # Track page visit
    track_page_visit("mcp_showcase")
    
    st.markdown("""
    This section demonstrates how the Model Context Protocol (MCP) works in practice.
    You'll see how an LLM can access external company data to provide more accurate responses.
    """)
    
    # Check if API key is configured
    if not check_api_key():
        st.warning("This showcase requires a Google API key to demonstrate real functionality.")
        api_key_input()
        return
    
    tab1, tab2, tab3 = st.tabs(["MCP Architecture", "Interactive Demo", "Response Comparison"])
    
    with tab1:
        st.header("MCP Architecture Visualization")
        
        try:
            st.image("images/mcp_architecture.png", caption="MCP Architecture Flow")
        except Exception as e:
            st.warning(f"Could not load MCP architecture diagram: {e}")
            st.markdown("![MCP Architecture Flow](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*8wNWI9XYGQmGZlvwKrYhvQ.png)")
        
        st.markdown("""
        The MCP flow works as follows:
        
        1. The LLM (Host) recognizes it needs external information to answer a query
        2. The LLM generates a structured request for information
        3. The MCP Client receives this request and routes it to the appropriate MCP Server
        4. The MCP Server retrieves the requested information from its data sources
        5. The information is formatted and returned to the LLM
        6. The LLM incorporates this information into its response
        
        This process happens seamlessly, allowing the LLM to access up-to-date information beyond its training data.
        """)
        
        # Mark subsection as completed
        mark_section_completed("mcp_showcase", "architecture")
        if st.button("Mark Architecture as Completed"):
            st.success("MCP Architecture section marked as completed!")
            st.rerun()
    
    with tab2:
        st.header("Interactive MCP Demonstration")
        
        st.markdown("""
        This demonstration shows how MCP can be used to retrieve company information.
        Enter a question about TechCorp (our fictional company) to see how the LLM uses MCP to access company data.
        """)
        
        # Sample company data that would be accessed via MCP
        with st.expander("Available Company Data (via MCP)", expanded=False):
            st.info("""
            **Company Profile**: TechCorp is a software company founded in 2010, specializing in AI solutions for enterprise clients.
            
            **Products**: TechAssist (AI customer service), DataInsight (analytics platform), CloudSecure (security solution)
            
            **Employee Count**: 500 employees across 5 global offices
            
            **Recent News**: TechCorp announced a new partnership with GlobalTech in March 2025
            
            **Leadership**: CEO Dr. Sarah Chen, CTO Michael Rodriguez, and other executives
            """)
        
        # MCP toggle
        st.session_state.mcp_enabled = st.toggle("Enable MCP Context", value=True)
        
        # User query input
        user_query = st.text_input("Ask a question about TechCorp:", "When was TechCorp founded?")
        
        if st.button("Submit Query"):
            # Prepare prompt
            prompt = f"Answer the following question about TechCorp: {user_query}"
            if st.session_state.mcp_enabled:
                st.markdown("### MCP Flow Visualization")
                with st.status("Processing query through MCP...", expanded=True) as status:
                    st.write("1. LLM recognizes need for company information")
                    st.write("2. MCP Client sends request for company data")
                    st.write("3. MCP Server retrieves relevant information")
                    st.write("4. Context is formatted and returned to LLM")
                    st.write("5. LLM generates response with retrieved context")
                    status.update(label="MCP flow complete!", state="complete")
            with st.spinner("Generating response..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                debug_result = loop.run_until_complete(
                    generate_response(prompt, use_mcp=st.session_state.mcp_enabled, query=user_query)
                )
                loop.close()
                # Display all debug info
                st.markdown(f"### Response {'with' if st.session_state.mcp_enabled else 'without'} MCP Context")
                st.success(debug_result['answer'])
                with st.expander("Show MCP Context", expanded=False):
                    st.code(debug_result['mcp_context'] or "No MCP context used.", language="markdown")
                with st.expander("Show Prompt Sent to LLM", expanded=False):
                    st.code(debug_result['prompt'], language="markdown")
                with st.expander("Show Raw LLM Response Object", expanded=False):
                    st.code(debug_result['raw_response'], language="text")
                # Add to chat history for later comparison
                st.session_state.chat_history.append({
                    "query": user_query,
                    "response": debug_result['answer'],
                    "mcp_context": debug_result['mcp_context'],
                    "prompt": debug_result['prompt'],
                    "raw_response": debug_result['raw_response'],
                    "mcp_enabled": st.session_state.mcp_enabled
                })
                mark_section_completed("mcp_showcase", "demo")
    
    with tab3:
        st.header("MCP Response Comparison")
        
        st.markdown("""
        This comparison shows the difference between LLM responses with and without MCP context.
        """)
        
        # Display user's own comparison history
        if len(st.session_state.chat_history) > 0:
            st.subheader("Your Query History")
            
            for i, item in enumerate(st.session_state.chat_history):
                st.markdown(f"**Query {i+1}:** {item['query']}")
                st.markdown(f"**Response ({'with' if item['mcp_enabled'] else 'without'} MCP):**")
                st.markdown(item['response'])
                st.markdown("---")
        else:
            st.info("Try the Interactive Demo to generate your own comparisons!")
            
            # Sample queries and responses
            comparisons = [
                {
                    "query": "What products does TechCorp offer?",
                    "without_mcp": "I don't have specific information about TechCorp's products in my training data. I would need to access current information to provide an accurate answer.",
                    "with_mcp": "TechCorp offers three main products: TechAssist (an AI customer service solution), DataInsight (an analytics platform), and CloudSecure (a security solution). TechAssist is currently on version 4.2 and was first released in 2015. DataInsight is on version 3.0 and was launched in 2018. CloudSecure is the newest product, released in 2020 and currently on version 2.5."
                },
                {
                    "query": "How many employees work at TechCorp?",
                    "without_mcp": "I don't have specific information about TechCorp's employee count in my training data. This information may have changed since my last update.",
                    "with_mcp": "According to the latest company information, TechCorp has 500 employees across 5 global offices. The workforce includes 200 engineers, 100 sales and marketing professionals, 75 customer support specialists, 50 product managers, 25 HR and administrative staff, and 50 executives and managers. The company has employees from 35 different countries."
                }
            ]
            
            # Display sample comparisons
            st.subheader("Sample Comparisons")
            for i, comp in enumerate(comparisons):
                st.markdown(f"**Query:** {comp['query']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Without MCP:**")
                    st.info(comp["without_mcp"])
                
                with col2:
                    st.markdown("**With MCP:**")
                    st.success(comp["with_mcp"])
                
                st.markdown("---")
        
        # Mark subsection as completed
        mark_section_completed("mcp_showcase", "comparison")
        if st.button("Mark Comparison as Completed"):
            st.success("MCP Response Comparison section marked as completed!")
            st.rerun()
    
    # Check if all subsections are completed
    if (is_section_completed("mcp_showcase", "architecture") and 
        is_section_completed("mcp_showcase", "demo") and 
        is_section_completed("mcp_showcase", "comparison")):
        st.success("🎉 Congratulations! You've completed the MCP Showcase module.")

# A2A Showcase page using ADK-inspired implementation
def a2a_showcase_page():
    """Display A2A showcase page with ADK-inspired implementation"""
    st.title("A2A Showcase")
    
    # Track page visit
    track_page_visit("a2a_showcase")
    
    st.markdown("""
    This section demonstrates how the Agent-to-Agent (A2A) protocol works in practice using 
    concepts inspired by Google's Agent Development Kit (ADK).
    
    You'll see how different agents can discover each other, collaborate on tasks, and 
    delegate specialized work to create more powerful AI systems.
    """)
    
    # Check if API key is configured
    if not check_api_key():
        st.warning("This showcase requires a Google API key to demonstrate real functionality.")
        api_key_input()
        return
    
    # Get agent registry
    agent_registry = get_agent_registry()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["A2A Architecture", "A2A Overview", "Integration Architecture", "Agent Cards", "Multi-Agent Demo"])
    
    with tab1:
        st.header("A2A Architecture")
        
        st.markdown("""
        The Agent-to-Agent (A2A) protocol provides a standardized way for AI agents to discover, communicate, and delegate tasks to each other.
        Key components of the A2A architecture include:
        
        1. **Agent Registry**: Central system where agents register their capabilities and discover other agents
        
        2. **Specialized Agents**: Different types of agents with unique capabilities:
           - Assistant Agents: Handle user interactions and coordinate other agents
           - Research Agents: Retrieve and analyze information from various sources
           - Analysis Agents: Process and synthesize complex data
        
        3. **Task Delegation**: Mechanism for agents to assign specialized work to other agents
        
        4. **Communication Protocol**: Standardized format for agent-to-agent messaging
        
        This architecture enables powerful multi-agent systems where specialized agents collaborate 
        to solve complex problems beyond the capabilities of any single agent.
        """)
        
        # Display architecture diagram
        try:
            diagram_bytes = create_a2a_architecture_diagram()
            st.image(diagram_bytes, caption="Agent-to-Agent (A2A) Architecture", use_column_width=True)
        except Exception as e:
            st.error(f"Error generating or displaying diagram: {e}")
            st.image("https://storage.googleapis.com/gweb-cloudblog-publish/images/1_Agent_to_Agent_API_overview.max-2000x2000.jpg", 
                     caption="A2A Architecture (Fallback)")
        
        # Mark subsection as completed
        mark_section_completed("a2a_showcase", "architecture")
        if st.button("Mark Architecture as Completed"):
            st.success("A2A Architecture section marked as completed!")
            st.rerun()
    
    with tab2:
        st.header("A2A Architecture Overview")
        try:
            overview_bytes = create_a2a_architecture_overview_diagram()
            st.image(overview_bytes, caption="A2A Architecture Overview", use_column_width=True)
        except Exception as e:
            st.error(f"Error generating or displaying overview diagram: {e}")
        
    with tab3:
        st.header("Integration Architecture")
        
        st.markdown("""
        This diagram illustrates how Agent-to-Agent (A2A) and Model Context Protocol (MCP) technologies 
        can be integrated to create powerful, context-aware multi-agent systems.
        
        In this integrated architecture:
        
        1. **A2A Protocol** enables agents to discover each other through the Agent Registry and 
           collaborate based on their specialized capabilities
        
        2. **MCP Protocol** allows agents to access up-to-date external information beyond their 
           training data
        
        3. **Seamless Integration** occurs when agents use both protocols together - collaborating with 
           other agents while leveraging external data sources through MCP
        
        This combined approach creates a comprehensive system that can handle complex tasks requiring 
        both collaboration between specialized agents and access to the most current information.
        """)
        
        # Display integration architecture diagram
        try:
            st.image("images/integration_architecture.png", caption="A2A + MCP Integration Architecture", use_column_width=True)
        except Exception as e:
            st.error(f"Error loading image: {e}")
            st.warning("Integration architecture diagram could not be loaded. Please run the generate_diagrams.py script to generate this diagram.")
        
        # Mark subsection as completed
        mark_section_completed("a2a_showcase", "integration")
        if st.button("Mark Integration Architecture as Completed"):
            st.success("Integration Architecture section marked as completed!")
            st.rerun()
    
    with tab4:
        st.header("Agent Cards")
        st.markdown("""
        Agent Cards are a key component of the A2A protocol and ADK. They describe an agent's capabilities,
        endpoints, and authentication requirements, allowing other agents to discover and interact with them.
        """)
        # Display agent cards
        agent_cards = agent_registry.list_agents()
        for card in agent_cards:
            with st.expander(f"{card['name']} Agent Card", expanded=True):
                st.json(card)
        st.markdown("""
        Agent Cards include:
        - **Name**: The agent's identifier
        - **Description**: What the agent does
        - **Capabilities**: What tasks the agent can perform
        - **Endpoint**: How to reach the agent
        - **Authentication**: Security requirements for interaction
        When an agent needs to delegate a task, it first checks the capabilities of other agents
        through their Agent Cards to find the most appropriate one for the task.
        """)
        # Mark subsection as completed
        mark_section_completed("a2a_showcase", "agent_cards")
        if st.button("Mark Agent Cards as Completed"):
            st.success("Agent Cards section marked as completed!")
            st.rerun()

    with tab5:
        st.header("Multi-Agent Demonstration")
        st.markdown("""
        This demonstration shows how multiple agents can collaborate to solve a task using the A2A protocol.
        Enter a query to see how the Assistant Agent delegates to specialized agents based on the task requirements.
        """)
        # User query input
        user_query = st.text_input("Enter your query:", "Research information about AI trends and analyze the data")
        if st.button("Submit Query"):
            st.markdown("### Multi-Agent Interaction Flow")
            # Use asyncio to run the async function
            with st.spinner("Processing with multiple agents..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                # Simulate multi-agent interaction
                result = loop.run_until_complete(
                    simulate_multi_agent_interaction(agent_registry, user_query)
                )
                loop.close()
            # Display interaction steps
            if result["status"] == "success":
                with st.status("Multi-agent processing complete", expanded=True) as status:
                    for i, step in enumerate(result["steps"]):
                        st.write(f"Step {i+1}: {step['agent']} - {step['action']}")
                
                # Display detailed steps
                st.subheader("Detailed Agent Interactions")
                for i, step in enumerate(result["steps"]):
                    with st.expander(f"Step {i+1}: {step['agent']} {step['action']}", expanded=i==0):
                        st.markdown(f"**Agent:** {step['agent']}")
                        st.markdown(f"**Action:** {step['action']}")
                        st.markdown(f"**Result:** {step['result']}")
                
                # Display final response
                with st.container(border=True):
                    st.subheader("Final Response")
                    st.markdown(result["final_response"])
            else:
                st.error(f"Error: {result.get('error', 'Unknown error occurred')}")
            
            # Mark subsection as completed
            mark_section_completed("a2a_showcase", "multi_agent_demo")
            if not is_section_completed("a2a_showcase", "multi_agent_demo"):
                if st.button("Mark Multi-Agent Demo as Completed"):
                    mark_section_completed("a2a_showcase", "multi_agent_demo")
                    st.success("Multi-Agent Demonstration section marked as completed!")
                    st.rerun()
    
    # Check if all subsections are completed
    if (is_section_completed("a2a_showcase", "architecture") and 
        is_section_completed("a2a_showcase", "agent_cards") and 
        is_section_completed("a2a_showcase", "multi_agent_demo")):
        st.success("🎉 Congratulations! You've completed the A2A Showcase module.")

# Integration Example page
def integration_example_page():
    """Display integration example page"""
    st.title("🤝 A2A + MCP Integration Example")

    # Track page visit
    track_page_visit("integration")

    # Static Introduction and Scenario
    st.markdown("""
    This page demonstrates how A2A and MCP protocols can work together in a practical scenario.
    We'll simulate a user asking a question that requires both external company data (via MCP)
    and potentially some reasoning or specific task handling (conceptually via A2A, simplified here).
    """)

    st.subheader("Combined Protocol Scenario: Answering a Customer Query")
    st.markdown("""
    **Goal:** Answer a user's question about 'TechCorp' products using the most up-to-date information.
    
    **Flow:**
    1.  **User Query:** User asks a question (e.g., "What products does TechCorp offer?").
    2.  **(MCP):** The system (acting as an MCP Client) requests relevant data from the Company Data MCP Server.
    3.  **(MCP):** The MCP Server provides structured data about TechCorp products.
    4.  **(A2A/LLM):** The system (acting as an Assistant Agent or directly using an LLM) formulates a final answer using the user's query and the context received via MCP.
    5.  **Final Response:** The user receives a comprehensive, formatted answer.
    """)

    # Initialize MCP client
    if 'mcp_client' not in st.session_state:
        st.session_state.mcp_client = get_mcp_client()
    mcp_client = st.session_state.mcp_client

    # Check if API key is needed and not configured
    if not check_api_key() and st.session_state.current_page not in ["home", "education", "glossary"]:
        api_key_input()
        return
    
    # --- Configuration and Query Form --- (Always Visible)
    st.markdown("--- ") # Separator
    st.subheader("Configure Your Run")
    with st.form(key="integration_form", clear_on_submit=False):
        st.markdown("Select the technical details you want to see in the results:")
        col_opts1, col_opts2, col_opts3 = st.columns(3)
        with col_opts1:
            # Use session state for default value to persist across reruns before submission
            show_mcp_form = st.checkbox("Show MCP Context", value=st.session_state.get('show_mcp', False), help="See the company data retrieved from the MCP server.")
        with col_opts2:
            show_prompt_form = st.checkbox("Show Prompt Sent to LLM", value=st.session_state.get('show_prompt', False), help="See the final prompt sent to the language model.")
        with col_opts3:
            show_raw_form = st.checkbox("Show Raw LLM Response", value=st.session_state.get('show_raw', False), help="See the raw LLM response object for debugging.")

        # Use session state for default value
        user_query_form = st.text_input("Ask a question about TechCorp:", st.session_state.get('integration_query', "What products does TechCorp offer and when were they released?"))
        run_clicked = st.form_submit_button("Run Integrated Scenario")

    # --- Processing and Results --- (Only shown AFTER form submission)
    if run_clicked:
        # Save form selections to session state *after* submission
        st.session_state.show_mcp = show_mcp_form
        st.session_state.show_prompt = show_prompt_form
        st.session_state.show_raw = show_raw_form
        st.session_state.integration_query = user_query_form

        st.markdown("--- ") # Separator
        st.subheader("Processing and Results")

        with st.spinner("Running integrated scenario..."): # Use spinner for better UX
            # Run the integration logic
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            mcp_context = "Error fetching MCP data."
            prompt = "Error formulating prompt."
            final_response_obj = None
            main_answer = "Error processing request."
            extra_info = {}

            try:
                # 1. Get MCP Context
                with st.status("Fetching company data via MCP...", expanded=False) as mcp_status:
                    st.write("Sending request...")
                    mcp_response = loop.run_until_complete(mcp_client.request_company_data(user_query_form))
                    mcp_context = mcp_client.format_for_llm(mcp_response)
                    st.write("Data received.")
                    mcp_status.update(label="MCP Data Fetched!", state="complete")

                # 2. Simulate A2A/Generate Final Response (incorporating MCP context)
                with st.status("Generating final response...", expanded=False) as gen_status:
                    st.write("Formulating prompt...")
                    # Simplified: Directly use MCP context in the final prompt
                    prompt = f"You are an AI assistant helping with company information. Using ONLY the following context about TechCorp, answer the user's question. Format your answer using markdown (bold, italics, lists, etc.) for professional presentation.\n\nCONTEXT:\n{mcp_context}\n\nQUESTION:\n{user_query_form}\n\nANSWER:"
                    st.write("Sending prompt to LLM...")
                    final_response_obj = loop.run_until_complete(generate_response(prompt, use_mcp=False, query=user_query_form))
                    st.write("Response received.")
                    gen_status.update(label="Response Generated!", state="complete")

                # Extract results after successful execution
                if isinstance(final_response_obj, dict):
                    main_answer = final_response_obj.get('answer', "Could not extract answer.")
                    extra_info = {
                        'MCP Context': mcp_context,
                        'Prompt': final_response_obj.get('prompt', prompt), # Use the constructed prompt
                        'Raw Response': final_response_obj.get('raw_response', '')
                    }
                else:
                    # Handle case where generate_response didn't return a dict
                    main_answer = f"Error or unexpected response format: {str(final_response_obj)}"
                    extra_info = {
                        'MCP Context': mcp_context,
                        'Prompt': prompt,
                        'Raw Response': str(final_response_obj)
                    }

            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
                # Populate extra_info even on error for debugging if possible
                extra_info = {
                        'MCP Context': mcp_context if mcp_context != "Error fetching MCP data." else "Not available due to error.",
                        'Prompt': prompt if prompt != "Error formulating prompt." else "Not available due to error.",
                        'Raw Response': str(final_response_obj) if final_response_obj else "Not available due to error."
                    }
            finally:
                loop.close()

        # --- Display Results --- (Still inside 'if run_clicked')
        # Display Final Answer (Always show)
        with st.container(border=True):
            st.markdown("#### ✅ Final Response")
            if "Error" in main_answer:
                st.error(main_answer)
            else:
                st.markdown(main_answer) # Use st.markdown to render formatting

        # Display Optional Details based on checkboxes (use session state)
        if st.session_state.show_mcp or st.session_state.show_prompt or st.session_state.show_raw:
            st.markdown("#### Technical Details")
            if st.session_state.show_mcp and extra_info.get('MCP Context'):
                with st.expander("MCP Context Used"):
                    st.code(extra_info['MCP Context'], language="markdown")
            if st.session_state.show_prompt and extra_info.get('Prompt'):
                with st.expander("Prompt Sent to LLM"):
                    st.code(extra_info['Prompt'], language="markdown")
            if st.session_state.show_raw and extra_info.get('Raw Response'):
                with st.expander("Raw LLM Response (debug)"):
                    st.code(str(extra_info['Raw Response']), language="text")

        # Optional: Show flow visualization if needed (e.g., in an expander)
        with st.expander("Integration Flow Steps Executed", expanded=False):
            st.info("This represents the logical flow followed during processing.")
            st.write("1. User Query Received")
            st.write("2. MCP Data Requested & Received")
            st.write("3. Final Prompt Formulated (using MCP data)")
            st.write("4. LLM Invoked")
            st.write("5. Final Response Parsed & Displayed")

        # Mark section as completed
        mark_section_completed("integration")
        if st.button("Mark Integration as Completed"):
            st.success("Integration Example section marked as completed!")
            st.rerun()

# Glossary page
def glossary_page():
    """Display terminology glossary page"""
    st.title("Terminology Glossary")
    
    # Track page visit
    track_page_visit("glossary")
    
    st.markdown("""
    This glossary provides definitions for key terminology related to A2A and MCP protocols.
    """)
    
    # Sample glossary terms
    glossary_terms = {
        "Agent": "An autonomous software entity that can perceive its environment, make decisions, and take actions to achieve goals.",
        "Agent Card": "In A2A, a structured description of an agent's capabilities, endpoints, and authentication requirements.",
        "Agent Development Kit (ADK)": "Google's framework for developing and deploying AI agents with a focus on multi-agent systems.",
        "BaseAgent": "In ADK, the fundamental blueprint for all agents that serves as the foundation for more specialized agent types.",
        "Context": "Additional information provided to an LLM to help it generate more accurate and relevant responses.",
        "Context Window": "The maximum amount of text (tokens) an LLM can process in a single interaction.",
        "Host": "In MCP, the LLM that recognizes when it needs external information and makes requests.",
        "Large Language Model (LLM)": "A type of AI model trained on vast amounts of text data that can generate human-like text and perform various language tasks.",
        "LlmAgent": "In ADK, an agent that utilizes Large Language Models as its core engine to understand natural language, reason, and make decisions.",
        "MCP Client": "In MCP, the interface that receives requests from the LLM and forwards them to appropriate servers.",
        "MCP Server": "In MCP, the system that provides access to external data sources and returns formatted information.",
        "Model Context Protocol (MCP)": "A standardized way for LLMs to request and receive external context from various data sources.",
        "Multi-Agent System": "A system composed of multiple interacting agents that collaborate to solve problems beyond the capabilities of any single agent.",
        "Task Delegation": "In A2A, the process of one agent assigning a task to another agent with specialized capabilities.",
        "Task State": "In A2A, the current status of a task (e.g., pending, in-progress, completed, failed).",
        "Tool": "In ADK, a function that agents can use to perform specific tasks or access external resources.",
        "WorkflowAgent": "In ADK, an agent that controls the execution flow of other agents in predefined, deterministic patterns."
    }
    
    # Display glossary terms in alphabetical order
    for term, definition in sorted(glossary_terms.items()):
        with st.expander(term):
            st.markdown(definition)
    
    # Mark glossary as completed
    mark_section_completed("glossary")
    if st.button("Mark Glossary as Completed"):
        st.success("Terminology Glossary marked as completed!")
        st.rerun()

# Main app logic
def main():
    """Main application entry point"""
    # Check for navigation request
    if st.session_state.navigate_to is not None:
        st.session_state.current_page = st.session_state.navigate_to
        st.session_state.navigate_to = None
    
    # Display navigation
    main_navigation()
    
    # Display current page based on session state
    if st.session_state.current_page == "home":
        home_page()
    elif st.session_state.current_page == "education":
        education_page()
    elif st.session_state.current_page == "mcp_showcase":
        mcp_showcase_page()
    elif st.session_state.current_page == "a2a_showcase":
        a2a_showcase_page()
    elif st.session_state.current_page == "integration":
        integration_example_page()
    elif st.session_state.current_page == "glossary":
        glossary_page()

if __name__ == "__main__":
    main()
