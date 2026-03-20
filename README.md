# Skill-Bridge Career Navigator

> An AI-powered career planning platform that helps learners assess their skills, discover aligned job roles, and generate personalized learning roadmaps. Built as a full-stack prototype demonstrating practical AI integration, responsible data handling, and scalable architecture.

**Case Challenge Submission** | Name: Rythm Chawla | Scenario: Skill-Bridge Career Navigator | [Demo Video](https://youtu.be/8WNyeHnfhzA)

---

## 📋 Problem Understanding

### The Problem
Career transitions are chaotic. Learners struggle with:
- **Information overload**: Too many roles, unclear fit
- **Skill awareness gaps**: Don't know what they're missing
- **Overwhelm in planning**: No clear, prioritized learning path
- **Slow feedback loops**: Generic career advice isn't personalized

### Our Solution
We built a **single, clear user journey** that helps learners go from resume upload to personalized learning roadmap in minutes. The app answers three critical questions:
1. *What roles am I closest to?*
2. *What skills do I have vs. need?*
3. *What should I learn next, and in what order?*

**User Value**: Learners get instant clarity + actionable next steps instead of generic advice.

---

## ⚙️ Technical Approach

### Architecture Philosophy
We deliberately split **deterministic logic** (explainable, verifiable) from **AI-assisted logic** (flexible, human-like):

| **Logic Type** | **What It Does** | **Why This Split?** |
|---|---|---|
| **Rule-Based** (Deterministic) | Skill matching, role ranking, gap computation | Stable, auditable, no hallucination risk |
| **AI-Assisted** (LLM-Powered) | Resume structuring, feedback generation, roadmap creation | Flexibility where natural language matters |

### Core Features Implemented

✅ **User Authentication & Persistence**
- Email/password auth with hashed storage (`passlib`)
- SQLite profile persistence

✅ **Resume Parsing Pipeline**
- Extract PDF text → LLM-structured extraction → Editable profile sections
- User-correctable data (prevents cascading errors)

✅ **Skill-Gap Analysis Engine**
- Deterministic skill matching: user skills vs. role requirements
- Proficiency scoring based on presence/match quality
- Top 3 role recommendations from synthetic dataset

✅ **AI-Powered Personalization**
- **LLM Used**: Groq's `llama-3.3-70b-versatile` (fast, open inference)
- **Prompts**: Resume structuring, narrative feedback, learning roadmaps
- **Fallback**: Deterministic templates if LLM unavailable

✅ **Robust Error Handling**
- API failure resilience with retry logic
- Graceful LLM timeouts
- User-friendly error messages

### Tech Stack

```
Frontend:
  - React 18 + Vite (fast dev, optimized prod builds)
  - Axios (HTTP client with interceptors)
  - CSS modules (component scoping)

Backend:
  - FastAPI (modern, type-safe, async-ready)
  - SQLAlchemy ORM (queryable, migration-ready)
  - Pydantic (schema validation)
  - Groq API (LLM inference)

Data:
  - SQLite (lightweight, file-based)
  - Pandas (CSV processing)

Testing:
  - pytest + pytest-asyncio
```

---

## 🎨 Creativity & Design Decisions

### 1. **Hybrid AI Architecture**
Instead of going "all-in on LLM," we keep scoring deterministic and AI opportunistic. This means:
- ✅ Results are explainable (user can see *why* they matched a role)
- ✅ No hallucination risk in critical path
- ✅ Cost-effective (fewer LLM calls)

### 2. **Section-by-Section Profile Editing**
Rather than one giant resume form, users edit their profile in focused, manageable sections (Skills, Experience, Projects, etc.). This:
- Reduces cognitive load
- Feels less overwhelming
- Mirrors how users think about their career

### 3. **User-Correctable Extraction**
Resume parsing isn't perfect. Instead of hiding errors, we show structured data and let users correct it. This ensures downstream analysis is accurate.

### 4. **Synthetic Dataset with Realistic Roles**
We provide 50+ realistic job postings in CSV format so reviewers can test matching without legal/privacy concerns.

---

## 🚀 How to Run the Prototype

### Prerequisites
- Python 3.9+
- Node.js 16+
- [Groq API Key](https://console.groq.com/keys) (free tier available)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
# or
.\venv\Scripts\Activate.ps1   # Windows PowerShell

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
GROQ_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./profile.db
EOF

# Initialize database
python -c "from models import Base, engine; Base.metadata.create_all(engine)"

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
# Opens at http://localhost:5173
```

### Test the Prototype

1. **Sign up** with any email (uses SQLite locally)
2. **Upload a resume** (sample PDF provided or use your own)
3. **Review extracted profile** and edit sections
4. **View top 3 matching roles** from the synthetic dataset
5. **Run skill-gap analysis** on a target role
6. **See personalized roadmap** generated by Groq LLM

**Sample test credentials:**
```
Email: test@example.com
Password: testpass123
```

### API Endpoints (Backend)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/auth/signup` | Register user |
| POST | `/api/auth/login` | Authenticate |
| POST | `/api/profiles/upload-resume` | Upload & parse resume |
| GET | `/api/profiles/{user_id}` | Get profile |
| PUT | `/api/profiles/{user_id}` | Update profile |
| POST | `/api/analysis/match-roles` | Get top matching roles |
| POST | `/api/analysis/gap-analysis` | Analyze skill gaps for a role |

FastAPI interactive docs: `http://localhost:8000/docs`

---

## 📊 Dataset & Responsible Data Practices

**Dataset Location**: `backend/all_job_post.csv`

### Data Characteristics
- **50 synthetic job postings** with roles like Data Engineer, Product Manager, ML Engineer, etc.
- **Fields**: job_title, company, required_skills, proficiency_level, location, salary_range
- **Real-world-like** but fully synthetic (no real personal data)
- **Open for reviewers** to test matching without privacy concerns

### Responsible AI Decisions

| Decision | Why It Matters |
|----------|---|
| **Synthetic data only** | No PII, no privacy violations |
| **User-correctable extraction** | Prevents error amplification |
| **Deterministic core logic** | Explainable recommendations = trust |
| **LLM fallback** | Service remains usable if API fails |
| **Clear model source** | Users know *how* personalization works |
| **No profile tracking** | Profiles scoped to session |

---

## 📁 Repository Structure

```
.
├── README.md                    # This file
├── DESIGN.md                    # Detailed design rationale
├── .gitignore                   # Standard Python/Node ignores
│
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── models.py                # SQLAlchemy ORM models
│   ├── schemas.py               # Pydantic request/response schemas
│   ├── requirements.txt          # Python dependencies
│   ├── all_job_post.csv         # Synthetic job dataset
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── profiles.py          # Profile CRUD endpoints
│   │   ├── analysis.py          # Skill-gap analysis endpoints
│   │   └── jobs.py              # Job dataset endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Auth business logic
│   │   ├── database_service.py  # DB query helper
│   │   ├── skill_analysis.py    # Skill matching + gap analysis
│   │   └── retry_handler.py     # API resilience
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── resume_parser.py     # PDF extraction + LLM structuring
│   │   ├── pdf_parser.py        # PDF text extraction
│   │   ├── job_loader.py        # CSV dataset loading
│   │   └── rate_limiter.py      # API throttling
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py          # Pytest fixtures
│       ├── test_api.py          # Integration tests
│       └── test_skill_analysis.py # Unit tests for matching logic
│
└── frontend/
    ├── package.json             # Node dependencies
    ├── vite.config.js           # Vite bundler config
    ├── index.html               # Entry point
    └── src/
        ├── main.jsx             # React app root
        ├── App.jsx              # Main component
        ├── api/
        │   ├── client.js        # Axios instance + interceptors
        │   └── constants.js     # API URLs
        └── components/          # Reusable UI components
            ├── AuthPage.jsx
            ├── ResumePage.jsx
            ├── ProfilePage.jsx
            ├── ResultsPage.jsx
            ├── SkillGapVisualization.jsx
            └── ...
```

---

## 🔍 Technical Rigor Highlights

### Error Handling & Resilience
- **API Timeout Handling**: LLM calls wrapped with retry logic
- **Fallback Templates**: If Groq is down, we serve pre-written feedback
- **Input Validation**: All endpoints use Pydantic for strict type checking
- **CORS & Security**: FastAPI CORS middleware configured

### Testing
```bash
# Run tests
cd backend
pytest -v tests/

# Unit test for skill matching logic
pytest tests/test_skill_analysis.py -v

# Integration tests for API endpoints
pytest tests/test_api.py -v
```

### Performance Considerations
- **Frontend**: Vite bundler optimizes chunk splitting, tree-shaking
- **Backend**: Async SQLAlchemy queries + connection pooling
- **API Calls**: Batch role matching to reduce LLM calls

---

## 🎯 Future Enhancements

### Phase 2: Enhanced Analytics
- User engagement tracking (most-searched roles, popular skills)
- Cohort analysis (what skills matter across roles?)
- Learning outcome tracking (did users follow recommendations?)

### Phase 3: Advanced Personalization
- Fine-tuned LLM on company-specific job data
- Multi-role comparison ("path from A → B → C")
- Integration with real job boards (Indeed, LinkedIn)

### Phase 4: Scalability & Production
- PostgreSQL for multi-tenant support
- Redis caching for role/skill lookups
- Background job queues (Celery) for resume processing
- Docker containerization

### Phase 5: Responsible AI Governance
- Bias audits on role matching algorithms
- A/B testing of recommendation strategies
- User consent & data deletion workflows
- Explainability dashboard (show *why* a role matched)

---

## 🎬 Demo Video

(https://youtu.be/8WNyeHnfhzA)

---

## ✅ Evaluation Mapping

| Pillar | Coverage |
|--------|----------|
| **Problem Understanding** | Clear problem framing + user journey(s) defined in section 1 |
| **Technical Rigor** | Type-safe stack (Pydantic, FastAPI), tested, error-resilient |
| **Creativity** | Hybrid AI design, section-based UX, deterministic + AI balance |
| **Prototype Quality** | Full-stack working, realistic synthetic data, demo-ready |
| **Responsible AI** | Synthetic data, user correction loop, explainable logic, LLM fallback |

---

## 📝 Notes for Reviewers

1. **No API Keys Required for Demo**: SQLite + synthetic data mean you can run locally without Groq key (though LLM features will timeout gracefully)
2. **Synthetic Dataset Included**: `backend/all_job_post.csv` has realistic but fictional roles
3. **Code Comments**: Inline code explains design decisions at key junctures
4. **Design Rationale**: See `DESIGN.md` for deeper architecture decisions

---

## 🔗 Additional Resources

- **Backend Docs**: FastAPI auto-docs at `http://localhost:8000/docs`
- **Design Deep Dive**: See `DESIGN.md`
- **Deployment Ready**: See comments in `backend/main.py` for production checklist

---

