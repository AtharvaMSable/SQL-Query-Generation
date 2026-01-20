# AskQL Platform - Setup & Deployment Guide

## 📋 Prerequisites

- Python 3.11 or higher
- PostgreSQL (Neon recommended)
- Google Gemini API key
- Git (for version control)

## 🚀 Quick Start (5 Minutes)

### Step 1: Environment Setup

```bash
# Navigate to project directory
cd f:\PAT\AskQL

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

```bash
# Copy example environment file
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Edit .env with your credentials
notepad .env  # Windows
# nano .env  # Linux
```

**Required Variables:**
```env
# Neon PostgreSQL
NEON_DB_HOST=your-project.neon.tech
NEON_DB_NAME=your_database
NEON_DB_USER=your_username
NEON_DB_PASSWORD=your_password
NEON_DB_PORT=5432

# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# App Configuration
APP_ENV=production
LOG_LEVEL=INFO
SESSION_TIMEOUT_MINUTES=60
MAX_QUERY_ROWS=10000
```

### Step 3: Initialize Database

**Option A: Using Neon SQL Editor**
1. Log in to Neon Console
2. Open SQL Editor
3. Copy and paste contents of `sql/init_schema.sql`
4. Execute

**Option B: Using psql**
```bash
psql -h your-project.neon.tech -U your_username -d your_database -f sql/init_schema.sql
```

### Step 4: Run Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 🔐 Demo Login Credentials

After database initialization, use these credentials:

| Username | Password | Role | Access |
|----------|----------|------|--------|
| admin | demo123 | Admin | All datasets |
| analyst1 | demo123 | Analyst | Sales Analytics |
| viewer1 | demo123 | Viewer | Sales Analytics |

## 📊 Sample Queries to Try

Once logged in, try these natural language questions:

1. **Sales Overview**
   - "What were the total sales last month?"
   - "Show me the top 5 products by revenue"
   - "Which region had the highest sales?"

2. **Trend Analysis**
   - "How have sales trended over the past 6 months?"
   - "What is the average order value by month?"
   - "Show revenue by product category"

3. **Customer Insights**
   - "Which customers spent the most?"
   - "What is the distribution of sales by customer segment?"
   - "How many unique customers purchased last quarter?"

4. **Product Analysis**
   - "What are the top selling products?"
   - "Which products have the highest profit margin?"
   - "Show sales by product category"

## 🔧 Troubleshooting

### Connection Issues

**Problem:** Cannot connect to database
```
❌ Failed to connect to database
```

**Solution:**
1. Verify Neon credentials in `.env`
2. Check if IP is whitelisted in Neon (if IP restrictions enabled)
3. Test connection:
   ```bash
   psql -h your-project.neon.tech -U your_username -d your_database
   ```

### Gemini API Issues

**Problem:** SQL generation fails
```
❌ Failed to generate SQL
```

**Solution:**
1. Verify `GEMINI_API_KEY` in `.env`
2. Check API key is active at: https://makersuite.google.com/app/apikey
3. Ensure you have API quota remaining

### Empty Schema

**Problem:** No tables found in schema
```
❌ No tables found in schema: sales_data
```

**Solution:**
1. Verify `sql/init_schema.sql` was executed successfully
2. Check schema exists:
   ```sql
   SELECT schema_name FROM information_schema.schemata 
   WHERE schema_name = 'sales_data';
   ```
3. Re-run initialization script

### Module Import Errors

**Problem:** Module not found
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
1. Ensure virtual environment is activated
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🌐 Deployment Options

### Option 1: Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in Streamlit Cloud dashboard:
   ```toml
   [secrets]
   NEON_DB_HOST = "your-host"
   NEON_DB_NAME = "your-db"
   NEON_DB_USER = "your-user"
   NEON_DB_PASSWORD = "your-password"
   GEMINI_API_KEY = "your-key"
   ```
5. Deploy!

### Option 2: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t askql .
docker run -p 8501:8501 --env-file .env askql
```

### Option 3: Traditional Server

```bash
# Install screen or tmux for background execution
apt-get install screen  # Ubuntu/Debian

# Start in screen session
screen -S askql
streamlit run app.py --server.port=8501

# Detach with Ctrl+A, D
# Reattach with: screen -r askql
```

## 📈 Production Considerations

### Security Hardening

1. **Change Default Passwords**
   ```sql
   UPDATE users SET password_hash = 'new_hash' WHERE username = 'admin';
   ```

2. **Use Strong Password Hashing**
   - Replace SHA-256 with bcrypt or argon2
   - Update `auth/user_auth.py` accordingly

3. **Enable HTTPS**
   - Use reverse proxy (nginx, traefik)
   - Obtain SSL certificate (Let's Encrypt)

4. **IP Whitelisting**
   - Configure in Neon Console
   - Limit database access

5. **API Rate Limiting**
   - Implement rate limiting for Gemini API
   - Add request throttling in production

### Performance Optimization

1. **Database Indexes**
   - Already included in `init_schema.sql`
   - Add custom indexes based on query patterns

2. **Connection Pooling**
   - Configured in `config/database_config.py`
   - Adjust `pool_size` and `max_overflow` for load

3. **Query Caching**
   - Enable Streamlit caching for schema metadata
   - Cache LLM responses for identical questions

4. **Monitoring**
   - Enable application logging
   - Set up alerts for errors
   - Monitor Neon metrics

## 🔄 Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

2. **Database Backups**
   - Neon provides automatic backups
   - Export critical data periodically
   ```bash
   pg_dump -h host -U user -d database > backup.sql
   ```

3. **Monitor Logs**
   ```bash
   tail -f askql_*.log
   ```

4. **Clean Query History**
   ```sql
   DELETE FROM query_history WHERE created_at < NOW() - INTERVAL '90 days';
   ```

## 📞 Support

- **Documentation:** See README.md
- **Issues:** Create GitHub issue
- **Email:** support@askql.com (configure as needed)

## 📄 License

Proprietary - All Rights Reserved

---

**Version:** 1.0.0  
**Last Updated:** January 2026  
**Built with:** Streamlit, PostgreSQL, Google Gemini
