# AskQL - Natural Language Database Query Tool

Query PostgreSQL databases using plain English, powered by Google Gemini AI.

## What It Does

Type questions in normal language and get SQL queries automatically generated, validated, and executed with visual results.

## Quick Start

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**
   ```bash
   # Create .env file with your credentials
   NEON_DB_URL=postgresql://user:pass@host/db?sslmode=require
   GEMINI_API_KEY=your_api_key
   ```

3. **Setup database**
   ```bash
   # Run sql/init_schema.sql in Neon SQL Editor
   ```

4. **Run app**
   ```bash
   streamlit run app.py
   ```

5. **Login**
   - Username: analyst1
   - Password: demo123

## Features

- User authentication
- Natural language to SQL conversion
- Query validation (prevents harmful queries)
- Interactive charts (Plotly)
- AI-generated insights
- Query history

## Project Structure

```
AskQL/
├── app.py              # Main app
├── auth/               # Login & sessions
├── config/             # Settings
├── database/           # DB operations
├── llm/                # Gemini integration
├── analytics/          # Charts & insights
└── utils/              # Helpers
```

## Tech Stack

- Frontend: Streamlit
- Database: Neon PostgreSQL
- AI: Google Gemini
- Charts: Plotly
- ORM: SQLAlchemy

## Security

- SQL injection prevention
- SELECT-only queries
- Row-level access control
- Session timeouts
- Query validation

## Example

**Question:** "Show top 5 products by revenue"

**Generated SQL:**
```sql
SELECT product_name, SUM(revenue) as total
FROM sales_data.sales s
JOIN sales_data.products p ON s.product_id = p.product_id
GROUP BY product_name
ORDER BY total DESC
LIMIT 5
```

**Result:** Bar chart + AI insight

## Author

Developed by Atharva

