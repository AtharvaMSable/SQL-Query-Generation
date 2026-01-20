# AskQL - AI-Powered Analytics Platform

A production-grade natural language query and analytics platform powered by Google Gemini and Neon PostgreSQL.

## 🎯 Overview

AskQL enables non-technical users to query databases using plain English. The system intelligently converts natural language questions into safe SQL, executes them on secure multi-tenant PostgreSQL databases, and presents results with interactive visualizations and AI-generated insights.

## 🏗️ Architecture

```
┌─────────────────┐
│   Streamlit UI  │
└────────┬────────┘
         │
    ┌────┴────┐
    │  Auth   │
    └────┬────┘
         │
┌────────┴────────────┐
│  Natural Language   │
│     Question        │
└────────┬────────────┘
         │
    ┌────┴─────┐
    │  Gemini  │ ──► SQL Generation
    │   LLM    │
    └────┬─────┘
         │
    ┌────┴─────┐
    │   SQL    │ ──► Validation
    │ Validator│
    └────┬─────┘
         │
    ┌────┴─────┐
    │   Neon   │ ──► Query Execution
    │PostgreSQL│
    └────┬─────┘
         │
    ┌────┴─────┐
    │Analytics │ ──► Charts + Insights
    │  Engine  │
    └──────────┘
```

## 📁 Project Structure

```
AskQL/
├── app.py                      # Streamlit entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # This file
│
├── auth/                      # Authentication & Authorization
│   ├── __init__.py
│   ├── session_manager.py    # Session state handling
│   └── user_auth.py          # Login & user management
│
├── config/                    # Configuration Management
│   ├── __init__.py
│   ├── settings.py           # App settings & constants
│   └── database_config.py    # Neon DB connection config
│
├── database/                  # Database Layer
│   ├── __init__.py
│   ├── connection.py         # SQLAlchemy engine & connection
│   ├── schema_loader.py      # Dynamic schema introspection
│   ├── query_executor.py     # Safe query execution
│   └── validators.py         # SQL safety validation
│
├── llm/                       # AI/LLM Integration
│   ├── __init__.py
│   ├── gemini_client.py      # Gemini API client
│   └── prompt_templates.py   # Prompt engineering
│
├── analytics/                 # Analytics & Visualization
│   ├── __init__.py
│   ├── chart_generator.py    # Plotly chart creation
│   └── insight_generator.py  # AI-powered insights
│
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── logger.py             # Logging configuration
│   └── helpers.py            # Helper functions
│
└── sql/                       # Database Setup Scripts
    └── init_schema.sql       # Sample schema & data
```

## 🚀 Setup Instructions

### 1. Clone & Navigate
```bash
cd f:\PAT\AskQL
```

### 2. Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
copy .env.example .env
# Edit .env with your Neon DB credentials and Gemini API key
```

### 5. Initialize Database
```bash
# Run the SQL schema initialization script on your Neon database
# Use Neon SQL Editor or psql:
psql -h your-neon-host.neon.tech -U your_username -d your_database -f sql/init_schema.sql
```

### 6. Run Application
```bash
streamlit run app.py
```

## 🔐 Security Features

- **Multi-tenant isolation**: Row-level security via user-dataset mapping
- **SQL injection prevention**: Strict SQL validation & sanitization
- **Read-only queries**: Only SELECT statements allowed
- **Row limiting**: Automatic LIMIT enforcement
- **Session management**: Secure session state with timeout
- **Schema isolation**: Users only see authorized datasets

## 🎨 Key Features

### 1. Natural Language Processing
- Convert business questions to SQL using Gemini
- Context-aware prompt engineering
- Schema-aware query generation

### 2. Smart Visualizations
- Auto-detect chart types (line, bar, pie, scatter)
- Interactive Plotly charts
- Time-series analysis

### 3. AI Insights
- Automated result interpretation
- Trend detection
- Business-friendly summaries

### 4. User Experience
- Intuitive Streamlit interface
- Session-based query history
- Collapsible SQL preview
- Dataset switcher

## 📊 Usage Example

**User Question:** "What were our top 5 products by revenue last quarter?"

**System Actions:**
1. Validates user has access to sales dataset
2. Loads product & sales schema
3. Generates SQL:
   ```sql
   SELECT product_name, SUM(revenue) as total_revenue
   FROM sales
   WHERE order_date >= '2025-10-01' AND order_date < '2026-01-01'
   GROUP BY product_name
   ORDER BY total_revenue DESC
   LIMIT 5
   ```
4. Executes query safely
5. Displays bar chart
6. Generates insight: "Widget Pro led Q4 sales with $1.2M revenue, up 23% from Q3"

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | Streamlit |
| Backend | Python 3.11+ |
| Database | Neon PostgreSQL |
| ORM | SQLAlchemy |
| AI Model | Google Gemini |
| Visualization | Plotly |
| Data Processing | Pandas |

## 📈 Scalability Considerations

- Connection pooling for concurrent users
- Query result caching
- Async query execution for large datasets
- Rate limiting on LLM API calls
- Horizontal scaling with Streamlit Cloud/K8s

## 🧪 Testing

```bash
# Run tests (to be implemented)
pytest tests/

# Linting
flake8 .

# Type checking
mypy .
```

## 📝 License

Proprietary - All Rights Reserved

## 👥 Contributors

Built by Senior AI Platform Engineers

---

**Version:** 1.0.0  
**Last Updated:** January 2026
