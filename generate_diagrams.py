"""
Professional Architecture Diagram Generator

Key Improvements:
1. Academic accuracy with proper protocol layer representation
2. Professional visualization using Matplotlib
3. Enhanced UX with visual hierarchy and icons
4. Dark/light mode support
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import matplotlib.patheffects as path_effects
import numpy as np
import io
from typing import Dict, Tuple, List

# Academic style configuration
STYLE_CONFIG = {
    "colors": {
        "title": "#2E3440",
        "agent_registry": "#5E81AC",
        "assistant_agent": "#88C0D0",
        "research_agent": "#81A1C1",
        "analysis_agent": "#8FBCBB",
        "tool": "#D08770",
        "connection": "#4C566A",
        "annotation": "#3B4252",
        "shadow": "#2E3440",
        "background": "#ECEFF4",
        "text": "#2E3440"
    },
    "dark_colors": {
        "title": "#ECEFF4",
        "agent_registry": "#5E81AC",
        "assistant_agent": "#88C0D0",
        "research_agent": "#81A1C1",
        "analysis_agent": "#8FBCBB",
        "tool": "#D08770",
        "connection": "#D8DEE9",
        "annotation": "#E5E9F0",
        "shadow": "#000000",
        "background": "#2E3440",
        "text": "#E5E9F0"
    },
    "fonts": {
        "title": {"family": "DejaVu Sans", "size": 16, "weight": "bold"},
        "component": {"family": "DejaVu Sans", "size": 10, "weight": "normal"},
        "annotation": {"family": "DejaVu Sans", "size": 8, "weight": "light"}
    },
    "icons": {
        "agent_registry": "",
        "assistant_agent": "",
        "research_agent": "",
        "analysis_agent": "",
        "tool": ""
    },
    "academic_references": [
        "Based on: Wooldridge, M. (2009). An Introduction to MultiAgent Systems.",
        "Protocol design inspired by FIPA standards (Foundation for Intelligent Physical Agents)"
    ]
}

# Global dark mode setting
DARK_MODE = False

def set_dark_mode(enabled: bool):
    """Enable/disable dark mode for diagrams"""
    global DARK_MODE
    DARK_MODE = enabled

def create_a2a_architecture_diagram():
    """
    Create a professional A2A architecture diagram with:
    - Proper academic representation
    - Visual hierarchy
    - Annotation layers
    """
    # Create figure with professional proportions
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Set style based on dark mode
    style = STYLE_CONFIG["dark_colors"] if DARK_MODE else STYLE_CONFIG["colors"]
    bg_color = style["background"]
    
    # Configure figure aesthetics
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.axis('off')
    
    # Add academic title with reference
    title = ax.text(0.5, 0.95, "Agent-to-Agent Protocol Architecture",
                   ha='center', va='center',
                   fontdict=STYLE_CONFIG["fonts"]["title"],
                   color=style["title"])
    
    # Add reference footnote
    ref_text = "\n".join(STYLE_CONFIG["academic_references"])
    ax.text(0.02, 0.02, ref_text,
            fontdict=STYLE_CONFIG["fonts"]["annotation"],
            color=style["annotation"],
            alpha=0.7)
    
    # Define component positions (normalized coordinates)
    components = {
        "agent_registry": {"pos": (0.5, 0.75), "size": (0.2, 0.1), "type": "agent_registry"},
        "assistant_agent": {"pos": (0.3, 0.55), "size": (0.15, 0.08), "type": "assistant_agent"},
        "research_agent": {"pos": (0.5, 0.55), "size": (0.15, 0.08), "type": "research_agent"},
        "analysis_agent": {"pos": (0.7, 0.55), "size": (0.15, 0.08), "type": "analysis_agent"},
        "tool1": {"pos": (0.2, 0.35), "size": (0.1, 0.06), "type": "tool"},
        "tool2": {"pos": (0.4, 0.35), "size": (0.1, 0.06), "type": "tool"},
        "tool3": {"pos": (0.6, 0.35), "size": (0.1, 0.06), "type": "tool"},
        "tool4": {"pos": (0.8, 0.35), "size": (0.1, 0.06), "type": "tool"}
    }
    
    # Add all components
    component_data = {}
    for name, config in components.items():
        component_data[name] = add_component(
            ax, config["pos"], config["size"],
            f"{STYLE_CONFIG['icons'][config['type']]} {name.replace('_', ' ').title()}",
            config["type"]
        )
    
    # Add professional connections with arrowheads
    connections = [
        ("agent_registry", "assistant_agent", "registers"),
        ("agent_registry", "research_agent", "discovers"),
        ("agent_registry", "analysis_agent", "discovers"),
        ("assistant_agent", "research_agent", "delegates"),
        ("research_agent", "analysis_agent", "shares data"),
        ("assistant_agent", "tool1", "uses"),
        ("assistant_agent", "tool2", "uses"),
        ("analysis_agent", "tool3", "uses"),
        ("analysis_agent", "tool4", "uses")
    ]
    
    for src, dst, label in connections:
        add_connection(
            ax,
            component_data[src]["bottom"],
            component_data[dst]["top"],
            label,
            style["connection"]
        )
    
    # Add protocol layer annotations
    add_protocol_layers(ax, style)
    
    # Save to buffer and return
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor=bg_color)
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()

def add_component(ax, pos, size, text, component_type):
    """
    Add a professional diagram component with:
    - Rounded corners
    - Subtle shadow
    - Icon + text
    - Consistent styling
    """
    style = STYLE_CONFIG["dark_colors"] if DARK_MODE else STYLE_CONFIG["colors"]
    x, y = pos
    width, height = size
    
    # Create rounded rectangle with professional styling
    rect = patches.FancyBboxPatch(
        (x-width/2, y-height/2), width, height,
        boxstyle=patches.BoxStyle("Round", pad=0.02, rounding_size=0.1),
        edgecolor=style[component_type],
        facecolor=style[component_type] + "40",  # Add transparency
        linewidth=1.5,
        alpha=0.9
    )
    
    # Add subtle shadow for depth
    if DARK_MODE:
        shadow = patches.FancyBboxPatch(
            (x-width/2+0.01, y-height/2-0.01), width, height,
            boxstyle=patches.BoxStyle("Round", pad=0.02, rounding_size=0.1),
            facecolor=style["shadow"],
            alpha=0.2,
            zorder=-1
        )
        ax.add_patch(shadow)
    
    ax.add_patch(rect)
    
    # Add text with icon
    ax.text(
        x, y, text,
        ha='center', va='center',
        color=style["text"],
        fontsize=STYLE_CONFIG["fonts"]["component"]["size"],
        fontweight=STYLE_CONFIG["fonts"]["component"]["weight"],
        path_effects=[path_effects.withStroke(linewidth=2, foreground=style["background"])]
    )
    
    # Return connection points
    return {
        "top": (x, y + height/2),
        "bottom": (x, y - height/2),
        "left": (x - width/2, y),
        "right": (x + width/2, y),
        "center": (x, y)
    }

def add_connection(ax, start, end, label=None, color="#4C566A"):
    """Add professional connection arrow with optional label"""
    style = STYLE_CONFIG["dark_colors"] if DARK_MODE else STYLE_CONFIG["colors"]
    
    # Draw simple arrow
    ax.annotate(
        "",
        xy=end,
        xytext=start,
        arrowprops=dict(
            arrowstyle="->",
            color=color,
            linewidth=1.5,
            shrinkA=5,
            shrinkB=5
        )
    )
    
    # Add label if provided
    if label:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        ax.text(
            mid_x, mid_y + 0.02, label,
            ha='center', va='center',
            fontsize=STYLE_CONFIG["fonts"]["annotation"]["size"],
            color=color,
            bbox=dict(
                facecolor=style["background"],
                edgecolor='none',
                pad=1,
                alpha=0.7
            )
        )

def add_protocol_layers(ax, style):
    """Add academic protocol layer annotations"""
    layers = [
        (0.85, "Application Layer\n(Agent Interactions)"),
        (0.7, "Protocol Layer\n(FIPA ACL, Ontologies)"),
        (0.55, "Transport Layer\n(HTTP, WebSockets)")
    ]
    
    for y, text in layers:
        ax.text(
            0.05, y, text,
            ha='left', va='center',
            fontsize=STYLE_CONFIG["fonts"]["annotation"]["size"],
            color=style["annotation"],
            bbox=dict(
                facecolor=style["background"],
                edgecolor=style["annotation"],
                pad=4,
                alpha=0.3
            )
        )

def create_mcp_architecture_diagram():
    """Create an improved MCP architecture diagram using matplotlib
    
    This diagram shows the flow of information in the Model Context Protocol,
    illustrating how LLMs can access external data through MCP servers.
    """
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Define component positions and sizes
    component_height = 0.12
    component_width = 0.2
    
    # Add components
    llm = add_component(
        ax, 
        pos=(0.2, 0.7), 
        size=(component_width, component_height),
        text="Large Language Model (LLM)",
        component_type="assistant_agent"
    )
    
    mcp_server = add_component(
        ax, 
        pos=(0.5, 0.7), 
        size=(component_width, component_height),
        text="MCP Server",
        component_type="agent_registry"
    )
    
    data_sources = add_component(
        ax, 
        pos=(0.5, 0.5), 
        size=(component_width, component_height),
        text="Data Sources",
        component_type="tool"
    )
    
    # Draw arrows connecting the components with clear labels
    # LLM to MCP Server
    add_connection(
        ax, 
        llm["right"], 
        mcp_server["left"],
        label="Request Context",
        color="#4C566A"
    )
    
    # MCP Server to LLM
    add_connection(
        ax, 
        mcp_server["left"], 
        llm["right"],
        label="Return Context",
        color="#4C566A"
    )
    
    # MCP Server to Data Sources
    add_connection(
        ax, 
        mcp_server["bottom"], 
        data_sources["top"],
        label="Query Data",
        color="#4C566A"
    )
    
    # Data Sources to MCP Server
    add_connection(
        ax, 
        data_sources["top"], 
        mcp_server["bottom"],
        label="Return Results",
        color="#4C566A"
    )
    
    # Add MCP flow steps
    mcp_steps = [
        "LLM recognizes need for external information",
        "LLM sends structured request to MCP Server",
        "MCP Server queries appropriate data sources",
        "Data sources return relevant information",
        "MCP Server formats and returns context to LLM",
        "LLM incorporates context into its response"
    ]
    
    # Add legend
    legend_components = [
        ("assistant_agent", "Large Language Model"),
        ("agent_registry", "MCP Server"),
        ("tool", "Data Sources")
    ]
    
    # Add note about MCP's purpose
    ax.text(
        0.5, 0.2, 
        "The Model Context Protocol (MCP) enables LLMs to access up-to-date information\n"
        "beyond their training data by providing a standardized way to request\n"
        "and receive external context from various data sources.",
        ha='center', va='center',
        color="#2E3440",
        fontsize=10,
        fontweight="normal",
        bbox=dict(facecolor='white', alpha=0.7, edgecolor="#4C566A", pad=10, boxstyle='round,pad=0.5')
    )
    
    # Save the image to a bytes buffer
    buf = io.BytesIO()
    fig.tight_layout()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()

def create_integration_diagram():
    """Create A2A and MCP integration diagram (improved)"""
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 9))
    
    # Define component positions and sizes
    component_height = 0.11
    component_width = 0.18
    
    # Add components
    registry = add_component(
        ax, 
        pos=(0.4, 0.8), 
        size=(0.2, 0.1),
        text="Agent Registry",
        component_type="agent_registry"
    )
    
    assistant = add_component(
        ax, 
        pos=(0.15, 0.65), 
        size=(component_width, component_height),
        text="Assistant Agent",
        component_type="assistant_agent"
    )
    
    research = add_component(
        ax, 
        pos=(0.41, 0.65), 
        size=(component_width, component_height),
        text="Research Agent",
        component_type="research_agent"
    )
    
    analysis = add_component(
        ax, 
        pos=(0.67, 0.65), 
        size=(component_width, component_height),
        text="Analysis Agent",
        component_type="analysis_agent"
    )
    
    mcp_server = add_component(
        ax, 
        pos=(0.41, 0.45), 
        size=(component_width, component_height),
        text="MCP Server",
        component_type="agent_registry"
    )
    
    data_sources = add_component(
        ax, 
        pos=(0.41, 0.25), 
        size=(component_width, component_height),
        text="Data Sources",
        component_type="tool"
    )
    
    # Draw arrows connecting components
    # Registry discovery connections
    add_connection(ax, registry["bottom"], assistant["top"], label="Discover", color="#4C566A")
    add_connection(ax, registry["bottom"], research["top"], label="Discover", color="#4C566A")
    add_connection(ax, registry["bottom"], analysis["top"], label="Discover", color="#4C566A")
    
    # Agent to agent collaboration
    add_connection(ax, assistant["right"], research["left"], label="Task Delegation", color="#4C566A")
    add_connection(ax, research["right"], analysis["left"], label="Results Sharing", color="#4C566A")
    add_connection(ax, analysis["bottom_left"], assistant["bottom_right"], label="Response", color="#4C566A")
    
    # Agents to MCP Server
    add_connection(ax, assistant["bottom"], mcp_server["left"], label="Query Context", color="#4C566A")
    add_connection(ax, research["bottom"], mcp_server["top"], label="Query Context", color="#4C566A")
    add_connection(ax, analysis["bottom"], mcp_server["right"], label="Query Context", color="#4C566A")
    
    # MCP Server to Data Sources
    add_connection(ax, mcp_server["bottom"], data_sources["top"], label="Access Data", color="#4C566A")
    add_connection(ax, data_sources["top"], mcp_server["bottom"], label="Return Results", color="#4C566A")
    
    # Add A2A flow steps
    a2a_steps = [
        "Agents register capabilities with Agent Registry",
        "Agents discover other agents through the Registry",
        "Agents delegate tasks based on other agents' capabilities", 
        "Agents collaborate to solve complex problems",
        "Agents access external data through MCP when needed",
        "Results are combined to provide comprehensive solutions"
    ]
    
    # Add legend
    legend_components = [
        ("agent_registry", "Agent Registry"),
        ("assistant_agent", "Assistant Agent"),
        ("research_agent", "Research Agent"),
        ("analysis_agent", "Analysis Agent"),
        ("tool", "Data Sources")
    ]
    
    # Add note about A2A's purpose
    ax.text(
        0.8, 0.4, 
        "Agent-to-Agent (A2A) Protocol enables\n"
        "multiple specialized AI agents to\n"
        "collaborate effectively, sharing tasks\n"
        "and information to solve complex problems.",
        ha='center', va='center',
        color="#2E3440",
        fontsize=10,
        fontweight="normal",
        bbox=dict(facecolor='white', alpha=0.7, edgecolor="#4C566A", pad=10, boxstyle='round,pad=0.5')
    )
    
    # Save the image to a bytes buffer
    buf = io.BytesIO()
    fig.tight_layout()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf.getvalue()

def create_integration_diagram():
    """Create an integrated A2A and MCP architecture diagram using matplotlib
    
    This diagram illustrates how A2A and MCP protocols work together to provide a
    comprehensive system where multiple agents can collaborate and access external data.
    """
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Define component positions and sizes
    component_height = 0.11
    component_width = 0.18
    
    # Add components
    registry = add_component(
        ax, 
        pos=(0.5, 0.85), 
        size=(0.25, 0.1),
        text="Agent Registry",
        component_type="agent_registry"
    )
    
    # Add the agents in a circular layout around the MCP server
    assistant = add_component(
        ax, 
        pos=(0.2, 0.7), 
        size=(component_width, component_height),
        text="Assistant Agent",
        component_type="assistant_agent"
    )
    
    research = add_component(
        ax, 
        pos=(0.5, 0.6), 
        size=(component_width, component_height),
        text="Research Agent",
        component_type="research_agent"
    )
    
    analysis = add_component(
        ax, 
        pos=(0.8, 0.7), 
        size=(component_width, component_height),
        text="Analysis Agent",
        component_type="analysis_agent"
    )
    
    # MCP components in the center and bottom
    mcp_server = add_component(
        ax, 
        pos=(0.5, 0.4), 
        size=(component_width, component_height),
        text="MCP Server",
        component_type="agent_registry"
    )
    
    data_sources = add_component(
        ax, 
        pos=(0.5, 0.2), 
        size=(component_width, component_height),
        text="Data Sources",
        component_type="tool"
    )
    
    # Draw agent-to-agent connections
    add_connection(ax, registry["bottom"], assistant["top"], 
                   label="1. Register & Discover", color="#4C566A")
    add_connection(ax, registry["bottom"], research["top"], 
                   label="1. Register & Discover", color="#4C566A")
    add_connection(ax, registry["bottom"], analysis["top"], 
                   label="1. Register & Discover", color="#4C566A")
    
    # Draw task delegation arrows
    add_connection(ax, assistant["right"], research["left"], 
                   label="2. Delegate Research Task", color="#4C566A")
    add_connection(ax, research["right"], analysis["left"], 
                   label="3. Delegate Analysis Task", color="#4C566A")
    add_connection(ax, analysis["left"], research["right"], 
                   label="6. Return Analysis Results", color="#4C566A")
    add_connection(ax, research["left"], assistant["right"], 
                   label="7. Return Research Results", color="#4C566A")
    
    # Draw agent to MCP connections
    add_connection(ax, research["bottom"], mcp_server["top"], 
                   label="4. Query Context", color="#4C566A")
    add_connection(ax, mcp_server["top"], research["bottom"], 
                   label="5. Return Context", color="#4C566A")
    
    # Draw MCP to data source connections
    add_connection(ax, mcp_server["bottom"], data_sources["top"], 
                   label="4a. Query Data", color="#4C566A")
    add_connection(ax, data_sources["top"], mcp_server["bottom"], 
                   label="4b. Return Data", color="#4C566A")
    
    # Add explanatory text boxes
    a2a_explain = "A2A Protocol:\nEnables agents to discover each other,\ndelegate tasks based on capabilities,\nand collaborate effectively."
    ax.text(
        0.2, 0.5, a2a_explain,
        ha='center', va='center',
        color="#2E3440",
        fontsize=10,
        fontweight="normal",
        bbox=dict(facecolor="#ECEFF4", 
                 edgecolor="#4C566A", 
                 pad=10, boxstyle='round,pad=0.5', alpha=0.9)
    )
    
    mcp_explain = "MCP Protocol:\nEnables agents to access up-to-date\nexternal data sources beyond their\ntraining data, improving responses."
    ax.text(
        0.8, 0.5, mcp_explain,
        ha='center', va='center',
        color="#2E3440",
        fontsize=10,
        fontweight="normal",
        bbox=dict(facecolor="#ECEFF4", 
                 edgecolor="#4C566A", 
                 pad=10, boxstyle='round,pad=0.5', alpha=0.9)
    )
    
    # Add legend
    legend_components = [
        ("agent_registry", "Agent Registry"),
        ("assistant_agent", "Assistant Agent"),
        ("research_agent", "Research Agent"),
        ("analysis_agent", "Analysis Agent"),
        ("tool", "Data Sources")
    ]
    
    # Save the image to a bytes buffer
    buf = io.BytesIO()
    fig.tight_layout()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)

def create_a2a_architecture_overview_diagram():
    """Create a high-level A2A Architecture Overview diagram."""
    fig, ax = plt.subplots(figsize=(10, 6))
    style = STYLE_CONFIG["dark_colors"] if DARK_MODE else STYLE_CONFIG["colors"]
    bg_color = style["background"]
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    ax.axis('off')

    # Title
    ax.text(0.5, 0.93, "A2A Architecture Overview", ha='center', va='center', fontsize=16, color=style["title"], fontweight='bold')

    # Main components (boxes)
    boxes = [
        (0.18, 0.7, 0.22, 0.15, "Agent Cards"),
        (0.5, 0.7, 0.22, 0.15, "Discovery Mechanism"),
        (0.82, 0.7, 0.22, 0.15, "Task Management"),
        (0.5, 0.35, 0.45, 0.18, "A2A Protocol Engine")
    ]
    for x, y, w, h, label in boxes:
        rect = patches.FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=0.02", edgecolor=style["tool"], facecolor=style["tool"]+"30", linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=14, color=style["text"], fontweight='bold')

    # Arrows (Discovery <-> Protocol Engine, Agent Cards <-> Protocol Engine, Task Management <-> Protocol Engine)
    arrow_style = dict(arrowstyle="->", color=style["connection"], linewidth=2)
    ax.annotate("", xy=(0.5, 0.61), xytext=(0.18, 0.61), arrowprops=arrow_style)
    ax.annotate("", xy=(0.5, 0.61), xytext=(0.82, 0.61), arrowprops=arrow_style)
    ax.annotate("", xy=(0.32, 0.61), xytext=(0.5, 0.45), arrowprops=arrow_style)
    ax.annotate("", xy=(0.68, 0.61), xytext=(0.5, 0.45), arrowprops=arrow_style)
    ax.annotate("", xy=(0.5, 0.61), xytext=(0.5, 0.45), arrowprops=arrow_style)

    # Academic reference
    ax.text(0.02, 0.03, "A2A: Agent-to-Agent Protocol for Multi-Agent Collaboration", fontsize=8, color=style["annotation"], ha='left', va='bottom', alpha=0.7)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight', facecolor=bg_color)
    buf.seek(0)
    plt.close(fig)
    return buf.getvalue()

def generate_and_save_diagrams():
    """Generate and save all diagrams to the images directory"""
    try:
        print("[INFO] Starting diagram generation process")
        output_dir = os.path.join(os.path.dirname(__file__), "images")
        os.makedirs(output_dir, exist_ok=True)
        # Generate and save each diagram
        print("[INFO] Generating A2A architecture diagram...")
        a2a_buf = create_a2a_architecture_diagram()
        with open(os.path.join(output_dir, "a2a_architecture.png"), "wb") as f:
            f.write(a2a_buf)
        print("[INFO] Generating MCP architecture diagram...")
        mcp_buf = create_mcp_architecture_diagram()
        with open(os.path.join(output_dir, "mcp_architecture.png"), "wb") as f:
            f.write(mcp_buf)
        print("[INFO] Generating integration diagram...")
        int_buf = create_integration_diagram()
        with open(os.path.join(output_dir, "integration_architecture.png"), "wb") as f:
            f.write(int_buf)
        print("[INFO] Generating A2A architecture overview diagram...")
        a2a_overview_buf = create_a2a_architecture_overview_diagram()
        with open(os.path.join(output_dir, "a2a_architecture_overview.png"), "wb") as f:
            f.write(a2a_overview_buf)
        print("[SUCCESS] All diagrams generated successfully")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to generate/save diagrams: {str(e)}")
        return False

if __name__ == "__main__":
    generate_and_save_diagrams()

