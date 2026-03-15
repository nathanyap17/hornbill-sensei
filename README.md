# 🌴 Sarawak Tourism & Culture Synth

An AI-powered tourism assistant for Sarawak, Malaysia, built with a **3-agent swarm architecture** using Gemini 2.5 Flash, RAG (Retrieval-Augmented Generation), and Streamlit.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Query (Streamlit UI)                     │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              🔍 Trip Planner Agent (Gemini 2.5 Flash)            │
│         Analyzes query → Extracts key topic/location            │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│               📚 Sarawak Info Agent (RAG Pipeline)               │
│     Searches ChromaDB → Retrieves relevant document chunks      │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              🎯 Tour Guide Agent (Gemini 2.5 Flash)              │
│      Synthesizes context → Friendly tour guide response         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Response to User                              │
└─────────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
q10-hackathon/
├── agents/
│   ├── __init__.py
│   └── tourism_swarm.py      # 3-agent swarm implementation
├── tools/
│   ├── __init__.py
│   ├── rag_pipeline.py       # RAG pipeline with ChromaDB
│   └── mcp_server.py         # MCP server (FastMCP)
├── app/
│   ├── __init__.py
│   └── main.py               # Streamlit frontend
├── data/                      # Place your PDF documents here
├── .chroma/                   # ChromaDB vector store (auto-generated)
├── requirements.txt
├── .env.example
└── README.md
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- Google Gemini API key (Get one at [Google AI Studio](https://aistudio.google.com/))
- (Optional) Ollama for local Gemma models

### 2. Installation

```bash
# Clone the repository
cd q10-hackathon

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy the example environment file
copy .env.example .env  # Windows
# cp .env.example .env  # macOS/Linux

# Edit .env and add your API keys
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Add Documents

Place your Sarawak tourism PDF documents in the `data/` folder:

- Official visitor guides (Bako National Park, Mulu Caves, etc.)
- Tourism brochures
- Cultural information documents
- Event guides (Rainforest World Music Festival, etc.)

### 5. Run the Application

```bash
# Start the Streamlit app
streamlit run app/main.py
```

The app will open in your browser at `http://localhost:8501`

## 🤖 Agent Details

### Trip Planner Agent
- **Model**: Gemini 2.5 Flash
- **Role**: Router/Analyzer
- **Function**: Extracts key topics and locations from user queries
- **Output**: Clean search query for the Info Agent

### Sarawak Info Agent
- **Technology**: RAG Pipeline with ChromaDB
- **Role**: Researcher
- **Function**: Performs semantic search on vector database
- **Output**: Relevant document chunks with source metadata

### Tour Guide Agent
- **Model**: Gemini 2.5 Flash
- **Role**: Synthesizer
- **Function**: Transforms raw information into friendly, helpful responses
- **Output**: Natural language answer as a local tour guide

## 🔧 MCP Server

The project includes an MCP (Model Context Protocol) server for integration with other AI tools:

```bash
# Run the MCP server
python tools/mcp_server.py
```

Available MCP tools:
- `search_sarawak_documents` - Search the knowledge base
- `get_sarawak_context` - Get formatted context for LLMs
- `list_available_documents` - List loaded PDF documents
- `reload_knowledge_base` - Refresh the vector store

## 📊 Knowledge Base Management

### Adding New Documents

1. Place PDF files in the `data/` folder
2. The system will automatically detect and index them on next query
3. Or use the MCP tool `reload_knowledge_base` to force refresh

### Vector Store

- Stored in `.chroma/` directory
- Uses `all-MiniLM-L6-v2` embeddings (fast, efficient)
- Automatically persists between sessions

## 🎨 UI Features

- **Beautiful gradient design** with Sarawak green theme
- **Real-time agent logs** showing the thinking process
- **Example questions** for quick exploration
- **Source citations** for transparency
- **Responsive layout** for all screen sizes

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Google Gemini 2.5 Flash |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Vector DB | ChromaDB |
| Document Processing | LangChain + PyPDF |
| Frontend | Streamlit |
| MCP Server | FastMCP |

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `DATA_DIR` | Path to PDF documents | No (default: `data`) |
| `CHROMA_DIR` | Path to ChromaDB storage | No (default: `.chroma`) |

## 🤝 Contributing

This project was built for the Q10 Hackathon. Feel free to fork and extend!

## 📄 License

MIT License - Built with ❤️ for Sarawak Tourism

## 🙏 Acknowledgments

- Sarawak Tourism Board for inspiration
- Google for Gemini API
- LangChain community for RAG tools
- Streamlit for the amazing UI framework
