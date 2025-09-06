# SlopScan

> AI-powered code quality analysis tool that detects AI-generated code, and fraud in SoM

SlopScan is a comprehensive analysis platform designed to find fruad and slop on SoM

## Screenshots
![img](https://hc-cdn.hel1.your-objectstorage.com/s/v3/0e70036d42fb5e425835f29f4159fcf1d28ee598_image.png)


## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- GitHub Personal Access Token
- AI API access (HackClub AI)

### Installation

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## Architecture

### Backend Components

- **FastAPI Application**
- **GitHub Service**
- **Hackclub AI API**
- **Tree-sitter Integration**
- **Summer of Making Service API**

### Frontend Components

- **React + TypeScript**
- **HeroUI**:
- **Tailwind CSS**:
- **Vite**:

---

**Made with ❤️ for better code quality and authentic development**