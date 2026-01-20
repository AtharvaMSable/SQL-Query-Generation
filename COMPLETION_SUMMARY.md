# AskQL - Project Summary

## What it does
Query PostgreSQL databases using plain English. The app converts your questions to SQL, runs them safely, and shows results with charts.

## Tech Stack
- **Frontend:** Streamlit
- **Database:** Neon PostgreSQL
- **AI:** Google Gemini
- **Charts:** Plotly

## Main Features
- User authentication
- Natural language to SQL conversion
- Query validation (prevents harmful queries)
- Interactive data visualizations
- AI-generated insights
- Query history

## Project Structure
```
AskQL/
├── app.py              # Main application
├── auth/               # User login
├── config/             # Settings
├── database/           # DB operations
├── llm/                # Gemini integration
├── analytics/          # Charts & insights
└── utils/              # Helpers
```

## Quick Start
1. Install: `pip install -r requirements.txt`
2. Configure `.env` with credentials
3. Run database setup in Neon
4. Start: `streamlit run app.py`
5. Login: analyst1 / demo123

## Developed by
Atharva
