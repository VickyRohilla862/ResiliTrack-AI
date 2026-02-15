# ResiliTrack AI

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Node](https://img.shields.io/badge/node-16%2B-success)
![Flask](https://img.shields.io/badge/flask-2.3-lightgrey)
![React](https://img.shields.io/badge/react-18-61dafb)
![Vite](https://img.shields.io/badge/vite-5-646cff)

ResiliTrack AI is a full-stack web app that analyzes pandemic resilience for 10 countries using Google Gemini. It combines a React/Vite frontend with a Flask API, delivering an AI-driven analysis summary plus country rankings and aspect-level heatmaps.

## What It Does

- Accepts a pandemic scenario headline from users.
- Uses Gemini to interpret the scenario and score 7 resilience aspects per country.
- Computes overall resilience scores and ranks countries.
- Visualizes results through a bar chart and heatmap.
- Supports email or Google login with per-user API key storage.

## Key Features

- AI-assisted scenario analysis with Gemini.
- 7 resilience aspects: Defence, Economy, Healthcare, Infrastructure, Social Safety, Technology, Governance.
- 10 tracked countries out of the box.
- Interactive charts and heatmaps.
- Theme, font, and layout customization.
- Email and Google OAuth login with per-user Gemini API keys.

## Architecture

- Frontend: React 18 + Vite single-page app.
- Backend: Flask API with analysis, chat, and auth routes.
- AI layer: Gemini API client for scenario interpretation.
- Data layer: cached World Bank indicators for baseline scoring.
- Auth storage: SQLite database under backend/data/auth.db.

## Data Flow

1. User submits a scenario in the chatbot.
2. Frontend calls POST /api/analyze.
3. Backend builds baseline scores from cached indicators.
4. Gemini interprets the scenario and impacts aspects.
5. Backend applies impacts, computes totals, and returns results.
6. Frontend renders the analysis, bar chart, and heatmap.

## Tech Stack

Frontend:
- React 18
- Vite
- Chart.js + react-chartjs-2
- Axios

Backend:
- Flask 2.3
- Python 3.8+
- google-generativeai
- Flask-CORS
- python-dotenv
- SQLite (auth storage)

## Project Structure

```
RESILITRACK AI/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── routes/
│   └── utils/
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
├── setup.bat
├── setup.sh
├── start.bat
├── start.sh
└── README.md
```

## Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- A Gemini API key from Google AI Studio


### Windows Quick Start

1. Run setup.bat once.
3. Run start.bat.
4. Open http://localhost:5000.

### Manual Setup (All Platforms)

Backend:

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Frontend (new terminal):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5000

## Run In Single-URL Mode (Production Style)

Build the frontend and let Flask serve it:

```bash
cd frontend
npm install
npm run build
cd ../backend
python app.py
```

Open http://localhost:5000.

## API Endpoints

Analysis:
- POST /api/analyze
- GET /api/results
- GET /api/countries
- GET /api/aspects

Chat:
- GET /api/chat-history
- POST /api/chat-history
- DELETE /api/chat-history

Auth:
- GET /api/auth/me
- POST /api/auth/register
- POST /api/auth/login
- POST /api/auth/google
- POST /api/auth/api-key
- POST /api/auth/logout
- DELETE /api/auth/account

## Configuration Notes

- If Google OAuth is not configured, email login still works.
- Gemini API failures fall back to safe demo data for UI testing.
- Cached World Bank data lives in backend/data.
