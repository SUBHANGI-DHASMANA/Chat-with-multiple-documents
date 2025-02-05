# PDF Chat Application

## Project Overview
A Django and Nextjs web application that allows users to upload PDF documents and interact with their content through an AI-powered chat interface.

## Prerequisites
- Python 3.9+
- Node.js 14+
- pip
- npm/yarn

## Backend Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd pdf_chat_project
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create `.env` file in project root:
```
GOOGLE_API_KEY=your_google_generative_ai_api_key
```

### 5. Run Migrations
```bash
python manage.py migrate
```

### 6. Start Django Server
```bash
python manage.py runserver
```

## Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Start React Development Server
```bash
npm run dev
```

## Configuration Notes
- Backend runs on `http://localhost:8000`
- Frontend runs on `http://localhost:3000`
- Ensure CORS settings match your development environment

## Troubleshooting
- Check console for specific error messages
- Verify API key in `.env`
- Confirm all dependencies are installed

## Tech Stack
- Backend: Django, Langchain
- Frontend: Nextjs, tailwindcss, TypeScript
- AI: Google Generative AI
- Vector Storage: FAISS
