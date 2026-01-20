# ⚡ AskQL - Quick Start Guide

## 🎯 Get Running in 5 Minutes

### Prerequisites Checklist
- [ ] Python 3.11+ installed
- [ ] Neon PostgreSQL account (free tier works)
- [ ] Google Gemini API key (free tier available)

---

## Step 1️⃣: Setup Environment (2 min)

```powershell
# Navigate to project
cd f:\PAT\AskQL

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Expected Output:**
```
Successfully installed streamlit-1.31.0 sqlalchemy-2.0.27...
```

---

## Step 2️⃣: Configure Credentials (1 min)

Copy `.env.example` to `.env` and edit:

```env
# Your Neon PostgreSQL credentials
NEON_DB_HOST=your-project-name.neon.tech
NEON_DB_NAME=neondb
NEON_DB_USER=your-username
NEON_DB_PASSWORD=your-password

# Your Gemini API Key
GEMINI_API_KEY=AIzaSy...your-key-here
```

**Get Your Keys:**
- **Neon:** https://console.neon.tech → Create Project → Connection Details
- **Gemini:** https://makersuite.google.com/app/apikey → Create API Key

---

## Step 3️⃣: Initialize Database (1 min)

**Option A: Neon Console (Easiest)**
1. Go to https://console.neon.tech
2. Select your project → SQL Editor
3. Copy entire contents of `sql/init_schema.sql`
4. Paste and click "Run"

**Option B: Command Line**
```bash
psql "postgresql://user:pass@host/db" -f sql/init_schema.sql
```

**✅ Success Message:**
```
AskQL Database Setup Complete!
Users created: 3
Sample sales records: 500
```

---

## Step 4️⃣: Run Application (1 min)

```powershell
streamlit run app.py
```

**Expected Output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

Browser should open automatically!

---

## Step 5️⃣: Login & Test

### Login Credentials
```
Username: analyst1
Password: demo123
```

### Try These Questions
1. "Show me total sales by product category"
2. "What were the top 5 customers by revenue?"
3. "How have sales trended over the past 6 months?"

---

## 🎉 You're Done!

You should see:
- ✅ Login page
- ✅ Dataset selector showing "Sales Analytics"
- ✅ Query input box
- ✅ Results with charts and insights

---

## 🆘 Quick Troubleshooting

### Issue: "Cannot connect to database"
```powershell
# Test connection manually
psql -h your-host.neon.tech -U your-user -d your-db
```
**Fix:** Check credentials in `.env`

### Issue: "Module not found"
```powershell
# Verify venv is activated
pip list | findstr streamlit
```
**Fix:** Reinstall: `pip install -r requirements.txt`

### Issue: "Gemini API error"
**Fix:** Verify API key at https://makersuite.google.com/app/apikey

### Issue: "No tables in schema"
**Fix:** Re-run `sql/init_schema.sql` in Neon SQL Editor

---

## 📚 Next Steps

1. **Read PROJECT_OVERVIEW.md** - Understand the architecture
2. **Review SETUP.md** - Production deployment guide
3. **Explore Code** - Start with `app.py`, then modules
4. **Customize** - Add your own datasets and schemas

---

## 🎓 Sample Data Schema

The demo includes:
- **Users:** 3 demo accounts (admin, analyst, viewer)
- **Datasets:** Sales Analytics (sales_data schema)
- **Tables:** products, customers, sales (500 transactions)
- **Time Range:** Last 12 months of data

---

## 🔑 All Demo Credentials

| Username | Password | Role | Access |
|----------|----------|------|--------|
| admin | demo123 | Admin | All datasets |
| analyst1 | demo123 | Analyst | Sales only |
| viewer1 | demo123 | Viewer | Read-only |

---

## 📊 Architecture at a Glance

```
User Question → Gemini AI → SQL → PostgreSQL → Results → Charts + Insights
```

**Key Features:**
- 🔐 Secure multi-tenant auth
- 🧠 Natural language to SQL
- 🛡️ SQL injection prevention
- 📊 Auto-generated charts
- 💡 AI-powered insights
- 📜 Query history
- 🚀 Production-ready

---

## 🚀 Quick Commands Reference

```powershell
# Activate environment
venv\Scripts\activate

# Run app
streamlit run app.py

# Run in background
start /B streamlit run app.py

# Check logs (if errors)
type askql_*.log

# Update dependencies
pip install --upgrade -r requirements.txt

# Test database connection
python -c "from config.database_config import DatabaseConfig; print(DatabaseConfig.test_connection())"
```

---

## 💡 Pro Tips

1. **Use Chrome/Edge** - Best Streamlit experience
2. **Check Logs** - Errors appear in terminal and logs
3. **Try Simple Questions First** - "Show me all products"
4. **View Generated SQL** - Click "View Generated SQL" expander
5. **Session Timeout** - Default 60 minutes, re-login if needed

---

## 📞 Need Help?

1. Check **SETUP.md** for detailed troubleshooting
2. Review **PROJECT_OVERVIEW.md** for architecture
3. Read module docstrings in source code
4. Check Neon status: https://neon.tech/status
5. Check Gemini status: https://status.cloud.google.com

---

**Version:** 1.0.0  
**Updated:** January 2026  
**Time to Deploy:** ~5 minutes  
**Difficulty:** Beginner-friendly 🟢

---

**Happy Querying! 🚀**
