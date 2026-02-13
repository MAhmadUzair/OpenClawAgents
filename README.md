# OpenClawAgents - Multi-Agent Content Research & Publishing Pipeline

A production-grade multi-agent workflow system with a modern web interface for intelligent content automation.

## 🎯 Project Overview

This project implements an **Intelligent Content Production Pipeline** that coordinates multiple specialized AI agents to:
1. **Research** topics from multiple sources
2. **Analyze** and synthesize research findings
3. **Write** high-quality content based on research
4. **Optimize** content for SEO
5. **Validate** quality before publication

## 🏗️ Architecture

```
OpenClawAgents/
├── backend/          # Python FastAPI backend
│   ├── src/         # Agent implementations
│   ├── main.py      # FastAPI server
│   └── requirements.txt
├── frontend/        # Next.js frontend
│   ├── app/         # Next.js app directory
│   └── package.json
└── README.md
```

## 🚀 Quick Start

### Backend Setup

1. **Navigate to backend**:
```bash
cd backend
```

2. **Create virtual environment**:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

5. **Run backend server**:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend**:
```bash
cd frontend
```

2. **Install dependencies**:
```bash
npm install
```

3. **Configure API URL** (optional):
```bash
# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

4. **Run development server**:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📋 Features

### Backend
- FastAPI REST API
- Multi-agent orchestration
- Task queue with dependencies
- Persistent memory system
- Groq LLM integration

### Frontend
- Modern Next.js 14 interface
- Real-time pipeline status
- Task progress tracking
- Results visualization
- Responsive design

## 🎨 Tech Stack

### Backend
- Python 3.9+
- FastAPI
- Groq API (Llama models)
- Pydantic
- Uvicorn

### Frontend
- Next.js 14
- TypeScript
- Tailwind CSS
- React 18
- Axios
- Lucide Icons

## 📖 Usage

1. Start the backend server
2. Start the frontend development server
3. Navigate to `http://localhost:3000`
4. Enter a topic and run the pipeline
5. Monitor real-time progress and view results

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

## 📄 License

MIT License

---

**Built with ❤️ for intelligent content automation**
