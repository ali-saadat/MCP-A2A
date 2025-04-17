# A2A and MCP Protocol Interactive Showcase

This Streamlit application provides an educational and interactive showcase for Agent-to-Agent (A2A) and Model Context Protocol (MCP) technologies. It demonstrates how these protocols work and how they can be integrated to create powerful AI agent systems.

![image](https://github.com/user-attachments/assets/a1886391-aca7-4832-9bb0-d1ed3ac30e9c)


## Features

- **Educational Foundation**: Learn about A2A and MCP protocols, their architecture, and use cases
- **MCP Showcase**: See how LLMs can access external company data using the Model Context Protocol
- **A2A Showcase**: Experience agent-to-agent communication with an implementation inspired by Google's Agent Development Kit (ADK)
- **Integration Example**: Discover how A2A and MCP can work together in integrated systems
- **Terminology Glossary**: Reference comprehensive definitions of key terms

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone this repository:
   ```
   git clone <repository-url>
   cd streamlit_app
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Set up your API key:
   - Option 1: Create a `.env` file in the project root with:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```
   - Option 2: The application will prompt you to enter your API key when you run it

## Usage

1. Run the Streamlit application:
   ```
   streamlit run app.py
   ```

2. Open your browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

3. Use the navigation menu to explore different sections of the application

## Application Structure

- `app.py`: Main Streamlit application
- `adk_agents.py`: ADK-inspired agent implementation for A2A showcase
- `mcp_integration.py`: MCP client and server implementation
- `persistence.py`: Session state management
- `data/company_data.json`: Sample company data for MCP demonstration
- `data/user_sessions/`: Directory for storing user session data

## API Key Requirements

This application requires a Google API key with access to the Gemini Pro 2.5 model. You can obtain a key from the [Google AI Studio](https://makersuite.google.com/).

## Features in Detail

### Educational Foundation

- Protocol overviews with detailed explanations
- Interactive architecture diagrams
- Side-by-side protocol comparison

### MCP Showcase

- Demonstrates how LLMs can access external company data
- Shows the difference between responses with and without MCP context
- Visualizes the MCP flow

### A2A Showcase

- Implements an ADK-inspired agent architecture
- Displays agent cards with capabilities
- Demonstrates multi-agent collaboration
- Shows how agents can delegate tasks based on specialization

### Integration Example

- Combines A2A and MCP in a unified workflow
- Demonstrates how protocols complement each other

## ADK Implementation

The A2A showcase is inspired by Google's Agent Development Kit (ADK) and implements:

- BaseAgent: Foundation for all agent types
- LlmAgent: Agents powered by large language models
- WorkflowAgent: Agents that orchestrate other agents
- Tool: Functions that agents can use
- AgentRegistry: System for discovering and managing agents

## Customization

You can customize the application by:

1. Modifying the company data in `data/company_data.json`
2. Adding new agent types in `adk_agents.py`
3. Creating additional tools for agents to use
4. Extending the educational content

## Troubleshooting

- **API Key Issues**: Ensure your API key is correctly set in the `.env` file or entered in the application
- **Connection Errors**: Check your internet connection as the application requires access to the Gemini API
- **Display Problems**: If the UI appears broken, try refreshing the page or restarting the application

## Credits

This application was developed as a demonstration of A2A and MCP protocols, with implementation patterns inspired by Google's Agent Development Kit (ADK).

## License

[MIT License](LICENSE)
