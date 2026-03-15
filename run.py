"""
Run script for Sarawak Tourism & Culture Synth
Provides easy commands to run different components.
"""

import sys
import subprocess
import argparse


def run_streamlit():
    """Run the Streamlit frontend."""
    print("🌴 Starting Sarawak Tourism Streamlit App...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app/main.py"])


def run_mcp_server():
    """Run the MCP server."""
    print("🔌 Starting Sarawak Tourism MCP Server...")
    subprocess.run([sys.executable, "tools/mcp_server.py"])


def initialize_knowledge_base():
    """Initialize the knowledge base from PDFs."""
    print("📚 Initializing knowledge base...")
    from tools.rag_pipeline import initialize_pipeline
    pipeline = initialize_pipeline(force_reload=True)
    print("✅ Knowledge base initialized!")


def main():
    parser = argparse.ArgumentParser(
        description="Sarawak Tourism & Culture Synth - Run Script"
    )
    parser.add_argument(
        "command",
        choices=["app", "mcp", "init"],
        help="Command to run: 'app' (Streamlit), 'mcp' (MCP server), 'init' (Initialize KB)"
    )
    
    args = parser.parse_args()
    
    if args.command == "app":
        run_streamlit()
    elif args.command == "mcp":
        run_mcp_server()
    elif args.command == "init":
        initialize_knowledge_base()


if __name__ == "__main__":
    main()
