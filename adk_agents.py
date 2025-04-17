import os
import json
import uuid
import asyncio
from typing import Dict, List, Any, Optional

# ADK-inspired agent implementation
class BaseAgent:
    """Base class for all agents in the system, inspired by Google ADK BaseAgent"""
    
    def __init__(self, name: str, description: str = None):
        """Initialize the base agent with name and description"""
        self.name = name
        self.description = description or f"{name} Agent"
        self.agent_id = str(uuid.uuid4())
        self.tools = []
        self.state = {}
    
    def add_tool(self, tool):
        """Add a tool to the agent's capabilities"""
        self.tools.append(tool)
    
    async def process(self, input_data: Dict) -> Dict:
        """Process input data and return a response"""
        raise NotImplementedError("Subclasses must implement this method")
    
    def get_agent_card(self) -> Dict:
        """Generate agent card with capabilities"""
        return {
            "name": self.name,
            "description": self.description,
            "id": self.agent_id,
            "capabilities": [tool.name for tool in self.tools],
            "endpoint": f"/agents/{self.name.lower().replace(' ', '_')}",
            "authentication": {
                "type": "none"
            }
        }

class Tool:
    """Tool class for agent capabilities, inspired by Google ADK Tool"""
    
    def __init__(self, name: str, description: str, func):
        """Initialize tool with name, description and function"""
        self.name = name
        self.description = description
        self.func = func
    
    async def execute(self, **kwargs) -> Dict:
        """Execute the tool function with provided arguments"""
        try:
            result = await self.func(**kwargs) if asyncio.iscoroutinefunction(self.func) else self.func(**kwargs)
            return {
                "status": "success",
                "result": result
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

class LlmAgent(BaseAgent):
    """LLM-powered agent, inspired by Google ADK LlmAgent"""
    
    def __init__(self, name: str, description: str, model, instruction: str):
        """Initialize LLM agent with model and instruction"""
        super().__init__(name, description)
        self.model = model
        self.instruction = instruction
        self.history = []
    
    async def process(self, input_data: Dict) -> Dict:
        """Process input using LLM reasoning"""
        # Add input to history
        self.history.append({"role": "user", "content": input_data.get("query", "")})
        
        # Check if we need to use tools
        tool_results = {}
        for tool in self.tools:
            if tool.name in input_data.get("requested_tools", []):
                tool_result = await tool.execute(**input_data.get("tool_args", {}))
                tool_results[tool.name] = tool_result
        
        # Generate response using model
        if self.model:
            # In a real implementation, this would use the model API
            # For demo purposes, we'll simulate a response
            response = f"LLM Agent {self.name} processed: {input_data.get('query', '')}"
            if tool_results:
                response += f"\nUsed tools: {list(tool_results.keys())}"
        else:
            response = f"Agent {self.name} received input but no model is configured."
        
        # Add response to history
        self.history.append({"role": "assistant", "content": response})
        
        return {
            "response": response,
            "tool_results": tool_results,
            "agent": self.get_agent_card()
        }

class WorkflowAgent(BaseAgent):
    """Workflow agent for orchestrating other agents, inspired by Google ADK SequentialAgent"""
    
    def __init__(self, name: str, description: str, agents: List[BaseAgent]):
        """Initialize workflow agent with a list of agents to orchestrate"""
        super().__init__(name, description)
        self.agents = agents
    
    async def process(self, input_data: Dict) -> Dict:
        """Process input by sequentially delegating to each agent"""
        results = []
        current_input = input_data
        
        for agent in self.agents:
            agent_result = await agent.process(current_input)
            results.append({
                "agent": agent.name,
                "result": agent_result
            })
            
            # Update input for next agent with previous result
            current_input = {
                "query": input_data.get("query", ""),
                "previous_result": agent_result
            }
        
        return {
            "workflow_results": results,
            "final_result": results[-1]["result"] if results else None,
            "agent": self.get_agent_card()
        }

class AgentRegistry:
    """Registry for managing and discovering agents"""
    
    def __init__(self):
        """Initialize empty agent registry"""
        self.agents = {}
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent in the registry"""
        self.agents[agent.name] = agent
        return agent.get_agent_card()
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    def get_agent_by_capability(self, capability: str) -> Optional[BaseAgent]:
        """Find an agent with the specified capability"""
        for agent in self.agents.values():
            agent_card = agent.get_agent_card()
            if capability in agent_card["capabilities"]:
                return agent
        return None
    
    def list_agents(self) -> List[Dict]:
        """List all registered agents"""
        return [agent.get_agent_card() for agent in self.agents.values()]

# Example tool functions
async def search_company_data(query: str) -> Dict:
    """Search company data for relevant information"""
    # In a real implementation, this would search a database
    # For demo purposes, we'll return mock data
    return {
        "query": query,
        "results": [
            {"title": "Company Profile", "content": "TechCorp was founded in 2010..."},
            {"title": "Products", "content": "TechCorp offers TechAssist, DataInsight..."}
        ]
    }

async def analyze_data(data: Dict) -> Dict:
    """Analyze data and return insights"""
    # In a real implementation, this would perform real analysis
    # For demo purposes, we'll return mock insights
    return {
        "insights": [
            "Data shows increasing trend in user engagement",
            "Product A has highest customer satisfaction"
        ],
        "confidence": 0.85
    }

# Create and configure agents for the showcase
def setup_showcase_agents(model=None):
    """Set up agents for the A2A showcase"""
    # Create registry
    registry = AgentRegistry()
    
    # Create tools
    search_tool = Tool(
        name="search_company_data",
        description="Search company data for relevant information",
        func=search_company_data
    )
    
    analyze_tool = Tool(
        name="analyze_data",
        description="Analyze data and return insights",
        func=analyze_data
    )
    
    # Create assistant agent
    assistant = LlmAgent(
        name="Assistant",
        description="Primary assistant that can answer questions and delegate tasks",
        model=model,
        instruction="You are a helpful assistant that can answer questions and delegate specialized tasks."
    )
    assistant.add_tool(search_tool)
    
    # Create research agent
    researcher = LlmAgent(
        name="Researcher",
        description="Specialized agent for research tasks",
        model=model,
        instruction="You are a research specialist that can find and summarize information."
    )
    researcher.add_tool(search_tool)
    
    # Create analyst agent
    analyst = LlmAgent(
        name="Analyst",
        description="Specialized agent for data analysis",
        model=model,
        instruction="You are a data analyst that can analyze and interpret data."
    )
    analyst.add_tool(analyze_tool)
    
    # Create workflow agent
    research_workflow = WorkflowAgent(
        name="ResearchWorkflow",
        description="Workflow that coordinates research and analysis",
        agents=[researcher, analyst]
    )
    
    # Register all agents
    registry.register_agent(assistant)
    registry.register_agent(researcher)
    registry.register_agent(analyst)
    registry.register_agent(research_workflow)
    
    return registry

# Example usage in the Streamlit app
async def process_a2a_query(registry: AgentRegistry, query: str, agent_name: str = None, capability: str = None) -> Dict:
    """Process a query using the A2A system"""
    # Find appropriate agent
    agent = None
    if agent_name:
        agent = registry.get_agent(agent_name)
    elif capability:
        agent = registry.get_agent_by_capability(capability)
    else:
        # Default to assistant
        agent = registry.get_agent("Assistant")
    
    if not agent:
        return {
            "status": "error",
            "error": "No suitable agent found"
        }
    
    # Process query
    result = await agent.process({"query": query})
    
    return {
        "status": "success",
        "agent": agent.name,
        "result": result
    }

# Simulate a multi-agent interaction
async def simulate_multi_agent_interaction(registry: AgentRegistry, query: str) -> Dict:
    """Simulate a multi-agent interaction for demonstration purposes"""
    # Start with assistant
    assistant = registry.get_agent("Assistant")
    
    # First step: Assistant processes query
    step1 = await assistant.process({"query": query})
    
    # Determine if delegation is needed (simplified logic for demo)
    needs_research = "research" in query.lower() or "information" in query.lower()
    needs_analysis = "analyze" in query.lower() or "data" in query.lower()
    
    steps = [
        {
            "agent": "Assistant",
            "action": "Received query",
            "result": step1["response"]
        }
    ]
    
    # Second step: Delegate if needed
    if needs_research:
        researcher = registry.get_agent("Researcher")
        step2 = await researcher.process({"query": f"Research about: {query}"})
        steps.append({
            "agent": "Researcher",
            "action": "Delegated research task",
            "result": step2["response"]
        })
        
        # If analysis is also needed, continue the workflow
        if needs_analysis:
            analyst = registry.get_agent("Analyst")
            step3 = await analyst.process({
                "query": f"Analyze the research results",
                "previous_result": step2
            })
            steps.append({
                "agent": "Analyst",
                "action": "Delegated analysis task",
                "result": step3["response"]
            })
            
            # Final step: Assistant summarizes
            final = await assistant.process({
                "query": query,
                "research_result": step2,
                "analysis_result": step3
            })
            steps.append({
                "agent": "Assistant",
                "action": "Summarized results",
                "result": final["response"]
            })
        else:
            # Final step: Assistant summarizes research only
            final = await assistant.process({
                "query": query,
                "research_result": step2
            })
            steps.append({
                "agent": "Assistant",
                "action": "Summarized research",
                "result": final["response"]
            })
    elif needs_analysis:
        analyst = registry.get_agent("Analyst")
        step2 = await analyst.process({"query": f"Analyze data for: {query}"})
        steps.append({
            "agent": "Analyst",
            "action": "Delegated analysis task",
            "result": step2["response"]
        })
        
        # Final step: Assistant summarizes
        final = await assistant.process({
            "query": query,
            "analysis_result": step2
        })
        steps.append({
            "agent": "Assistant",
            "action": "Summarized analysis",
            "result": final["response"]
        })
    else:
        # No delegation needed
        steps.append({
            "agent": "Assistant",
            "action": "Completed task directly",
            "result": "No delegation was needed for this query."
        })
    
    return {
        "status": "success",
        "steps": steps,
        "final_response": steps[-1]["result"]
    }
