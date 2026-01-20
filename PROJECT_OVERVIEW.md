# AskQL - Natural Language Database Query Platform

## Project Summary

AskQL is a web application that lets you query databases using plain English. Built with Streamlit, Google Gemini, and Neon PostgreSQL.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                    Streamlit Web UI                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  Login   │  │ Dataset  │  │  Query   │  │ Results  │  │
│  │  Page    │  │ Selector │  │  Input   │  │  View    │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Auth Module  │  │  LLM Module  │  │Analytics Mod │    │
│  │              │  │              │  │              │    │
│  │ • Login      │  │ • Gemini     │  │ • Charts     │    │
│  │ • Session    │  │ • Prompts    │  │ • Insights   │    │
│  │ • Access     │  │ • SQL Gen    │  │ • Stats      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │Database Mod  │  │ Config Mod   │  │  Utils Mod   │    │
│  │              │  │              │  │              │    │
│  │ • Schema     │  │ • Settings   │  │ • Logging    │    │
│  │ • Executor   │  │ • DB Config  │  │ • Helpers    │    │
│  │ • Validator  │  │ • Constants  │  │ • Format     │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────────────────────────────────────────┐
│                      DATA LAYER                              │
│                                                              │
│  ┌────────────────────┐          ┌────────────────────┐   │
│  │  Neon PostgreSQL   │          │  Google Gemini     │   │
│  │                    │          │                    │   │
│  │ • Users            │          │ • LLM API          │   │
│  │ • Datasets         │          │ • Text → SQL       │   │
│  │ • Access Control   │          │ • Insights         │   │
│  │ • Sales Data       │          │                    │   │
│  │ • Query History    │          │                    │   │
│  └────────────────────┘          └────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
AskQL/
│
├── 📄 app.py                          # Main Streamlit application
├── 📄 requirements.txt                # Python dependencies
├── 📄 README.md                       # Project documentation
├── 📄 SETUP.md                        # Setup & deployment guide
├── 📄 .env.example                    # Environment template
├── 📄 .gitignore                      # Git ignore rules
│
├── 📁 auth/                           # Authentication & Authorization
│   ├── __init__.py
│   ├── user_auth.py                   # User authentication logic
│   └── session_manager.py             # Session state management
│
├── 📁 config/                         # Configuration Management
│   ├── __init__.py
│   ├── settings.py                    # App settings & constants
│   └── database_config.py             # Database connection config
│
├── 📁 database/                       # Database Operations
│   ├── __init__.py
│   ├── connection.py                  # Connection management
│   ├── schema_loader.py               # Schema introspection
│   ├── query_executor.py              # Query execution
│   └── validators.py                  # SQL validation & safety
│
├── 📁 llm/                            # AI/LLM Integration
│   ├── __init__.py
│   ├── gemini_client.py               # Gemini API client
│   └── prompt_templates.py            # Prompt engineering
│
├── 📁 analytics/                      # Analytics & Visualization
│   ├── __init__.py
│   ├── chart_generator.py             # Plotly chart generation
│   └── insight_generator.py           # Statistical insights
│
├── 📁 utils/                          # Utilities
│   ├── __init__.py
│   ├── logger.py                      # Logging configuration
│   └── helpers.py                     # Helper functions
│
└── 📁 sql/                            # Database Scripts
    └── init_schema.sql                # Database initialization
```

## 🎯 Core Features

### 1. **Multi-Tenant Authentication** 🔐
- Secure user login with hashed passwords
- Role-based access control (Admin, Analyst, Viewer)
- Session management with timeout
- Dataset-level authorization

### 2. **Natural Language Processing** 🧠
- Convert plain English to SQL using Gemini AI
- Context-aware query generation
- Schema-aware prompts
- Automatic query refinement on errors

### 3. **Comprehensive Security** 🛡️
- SQL injection prevention
- Query validation (SELECT-only)
- Schema isolation
- Automatic LIMIT enforcement
- Multi-layer security checks

### 4. **Intelligent Visualizations** 📊
- Auto-detect optimal chart types
- Interactive Plotly charts (bar, line, pie, scatter)
- Time-series analysis
- Responsive design

### 5. **AI-Powered Insights** 💡
- Automated result interpretation
- Statistical analysis
- Trend detection
- Business-friendly summaries

### 6. **Production Ready** 🚀
- Connection pooling
- Error handling & retry logic
- Comprehensive logging
- Query history & audit trail
- Scalable architecture

## 🔑 Key Design Decisions

### 1. **Modular Architecture**
- **Why:** Maintainability, testability, scalability
- **Impact:** Easy to extend, modify, and debug
- **Pattern:** Separation of concerns, single responsibility

### 2. **Schema-Aware Prompting**
- **Why:** Improve SQL generation accuracy
- **Impact:** Higher success rate, fewer errors
- **Implementation:** Dynamic schema injection in prompts

### 3. **Multi-Layer SQL Validation**
- **Why:** Security and data integrity
- **Impact:** Prevents destructive operations
- **Layers:** Keyword blocking, pattern matching, schema validation

### 4. **Connection Pooling**
- **Why:** Efficiency for concurrent users
- **Impact:** Better performance, resource management
- **Config:** Configured in DatabaseConfig class

### 5. **Session-Based State Management**
- **Why:** Streamlit's stateless nature
- **Impact:** Persistent user experience
- **Implementation:** SessionManager class

### 6. **Automatic Query Refinement**
- **Why:** Improve user experience on errors
- **Impact:** Higher query success rate
- **Process:** Error → Refinement → Retry

## 🔐 Security Features

| Feature | Implementation | Benefit |
|---------|---------------|---------|
| **SQL Injection Prevention** | Keyword blocking, pattern matching | Prevents malicious queries |
| **Row-Level Security** | User-dataset mapping | Multi-tenant isolation |
| **Read-Only Queries** | SELECT-only enforcement | Data integrity |
| **Schema Isolation** | Schema validation | Prevent cross-dataset access |
| **Session Timeout** | Configurable timeout | Security compliance |
| **Password Hashing** | SHA-256 (upgradeable) | Credential protection |
| **Audit Logging** | Query history table | Compliance & monitoring |

## 📊 Data Flow

```
User Question
     ↓
Login & Authentication
     ↓
Dataset Selection
     ↓
Schema Loading → [LLM Context]
     ↓
Gemini AI → Generate SQL
     ↓
SQL Validation → [Security Checks]
     ↓
Query Execution → [Neon PostgreSQL]
     ↓
Results → DataFrame
     ↓
┌────────────────┐
│ Visualizations │
│    Insights    │
│   Statistics   │
└────────────────┘
     ↓
Display to User
     ↓
Log to History
```

## 🚀 Performance Optimizations

### Database Level
- **Indexes:** On foreign keys, date columns, frequently queried fields
- **Connection Pool:** Reuses connections, prevents overhead
- **Query LIMIT:** Automatic enforcement prevents large result sets
- **Approximate Counts:** Uses pg_class for fast row estimates

### Application Level
- **Lazy Loading:** Schemas loaded on demand
- **Result Caching:** Streamlit session state caching
- **Batch Operations:** Efficient data processing with Pandas
- **Async Ready:** Architecture supports async operations

### LLM Level
- **Low Temperature:** Deterministic SQL generation (0.1)
- **Retry Logic:** Exponential backoff for transient failures
- **Token Limits:** Configured max tokens prevents runaway costs
- **Prompt Optimization:** Minimal context, maximum clarity

## 🧪 Testing Strategy

### Unit Tests (To Implement)
```python
# tests/test_validators.py
def test_sql_validator_blocks_delete():
    assert not SQLValidator.validate_query("DELETE FROM users")[0]

def test_sql_validator_allows_select():
    assert SQLValidator.validate_query("SELECT * FROM users")[0]
```

### Integration Tests
```python
# tests/test_query_flow.py
def test_end_to_end_query():
    # Test: Question → SQL → Execution → Results
    pass
```

### Load Tests
```python
# tests/test_performance.py
def test_concurrent_queries():
    # Simulate 50 concurrent users
    pass
```

## 📈 Scalability Considerations

### Horizontal Scaling
- Stateless application design
- Deploy multiple Streamlit instances
- Load balancer distribution
- Shared database backend (Neon)

### Vertical Scaling
- Adjust connection pool sizes
- Increase LLM rate limits
- Database resource allocation
- Cache layer (Redis)

### Cost Optimization
- Query result caching
- LLM response caching
- Efficient schema loading
- Connection pooling

## 🔄 Future Enhancements

### Phase 2 Features
- [ ] Custom dashboard builder
- [ ] Scheduled reports
- [ ] Email notifications
- [ ] Export to Excel/PowerBI
- [ ] Real-time collaboration

### Phase 3 Features
- [ ] Advanced analytics (ML models)
- [ ] Natural language reports
- [ ] Voice input support
- [ ] Mobile app
- [ ] Multi-language support

## 📊 Monitoring & Observability

### Metrics to Track
- Query success rate
- Average response time
- LLM API usage/cost
- Database query performance
- User session duration
- Error rates by type

### Logging Levels
- **DEBUG:** Detailed execution flow
- **INFO:** Key operations (login, query execution)
- **WARNING:** Recoverable errors
- **ERROR:** Failures requiring attention

### Health Checks
- Database connectivity
- LLM API availability
- Application startup
- Session management

## 🎓 Learning Points

This project demonstrates:

1. **Full-Stack AI Integration**
   - LLM integration in production
   - Prompt engineering best practices
   - Error handling for AI systems

2. **Enterprise Security**
   - Multi-tenant architecture
   - SQL injection prevention
   - Role-based access control

3. **Modern Python Patterns**
   - Type hints and validation
   - Modular design
   - Configuration management
   - Logging and monitoring

4. **Database Design**
   - Multi-tenant schema
   - Access control tables
   - Audit logging
   - Performance optimization

5. **UX/UI Design**
   - Streamlit best practices
   - Progressive disclosure
   - Error messaging
   - Loading states

## 📝 Code Quality

### Standards Followed
- PEP 8 style guide
- Type hints throughout
- Comprehensive docstrings
- DRY principle
- SOLID principles
- Defensive programming

### Documentation
- Inline comments for complex logic
- Module-level documentation
- Function docstrings with types
- README with examples
- Setup guide

## 🎯 Interview-Ready Aspects

### Technical Depth
✅ Production-grade architecture  
✅ Security best practices  
✅ Error handling & logging  
✅ Performance optimization  
✅ Scalability considerations  

### Business Value
✅ Solves real-world problem  
✅ Cost-effective (serverless)  
✅ User-friendly interface  
✅ Enterprise features  
✅ Extensible design  

### Code Quality
✅ Clean, readable code  
✅ Well-documented  
✅ Modular structure  
✅ Industry standards  
✅ Best practices  

## 📞 Support & Maintenance

### Getting Help
- Review SETUP.md for deployment
- Check logs for errors
- Test database connectivity
- Verify API keys

### Regular Maintenance
- Update dependencies monthly
- Review query logs weekly
- Backup database daily (Neon auto)
- Monitor LLM costs

---

**Developed by:** Atharva  
**Tech Stack:** Python, Streamlit, PostgreSQL, Google Gemini, Plotly  
**Version:** 1.0.0  
**License:** Proprietary  
**Date:** January 2026
