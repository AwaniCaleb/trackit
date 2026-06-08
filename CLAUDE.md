# CLAUDE.md — Trackit Project Context

This file is read automatically by Claude Code at session start.
Read it fully before taking any action.

---

## What This Project Is

**Trackit** — a Wireless Emergency Telemedicine System (WETS).
A web application for emergency patient registration, record management,
real-time ECG monitoring, and ML-assisted cardiac condition classification.

Built by Caleb (final year CS, RSU Port Harcourt, Nigeria).
High-stakes academic project — potential C.A. grade, exam credit, and
a contract opportunity. Quality and correctness matter.

---

## Repository Structure

```
/
├── CLAUDE.md                  ← you are here
├── frontend/                  ← COMPLETE. Do not modify without instruction.
│   ├── index.html
│   ├── login.html
│   ├── new-patient.html
│   ├── find-patient.html
│   ├── patient-connection.html
│   ├── css/styles.css
│   └── js/
│       ├── data.js            ← 15 dummy patients (DEFAULT_PATIENTS global)
│       ├── index.js
│       ├── login.js
│       ├── new-patient.js
│       ├── find-patient.js
│       └── patient-connection.js
├── backend/                   ← EXISTS but state unknown. Audit before touching.
├── model/
│   └── theirs/                ← Model from another group. Audit before using.
└── PROJECT_DESCRIPTION.md     ← Full requirements document
```

---

## Architecture (confirmed with lecturer)

```
Frontend (Vercel — static HTML/JS/CSS)
    ↕ HTTPS + JWT Bearer token
Java Spring Boot REST API (backend/)
    ↕ Internal HTTP
Python FastAPI ML Service (wraps model/theirs/)
    ↕
PostgreSQL Database
```

- Frontend and backend are **fully decoupled**
- All communication via JSON REST APIs
- JWT for authentication
- Frontend is already deployed or will be deployed to Vercel

---

## Frontend — COMPLETE, DO NOT MODIFY

Tech stack: HTML5, Bootstrap 5.3 CDN, Bootstrap Icons, Vanilla JS ES6+.
No build tools, no Node, no bundler.

### What works:
- Login with email regex validation, show/hide password, remember me
- Patient registration with 16-field validation, photo upload, Nigerian states
- Patient search with live filter, column sort, CSV export, detail modal
- Patient connection page with animated ECG canvas (P/QRS/T waveform),
  vital signs fluctuation, connect by name or patient ID

### localStorage as API placeholder:
Every localStorage call is a placeholder for a real fetch() call.
The swap is the key integration task. Example:

```javascript
// Current (placeholder in new-patient.js)
localStorage.setItem('trackit_patients', JSON.stringify(list));

// Target (after backend integration)
const res = await fetch('/api/patients', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + localStorage.getItem('trackit_token')
  },
  body: JSON.stringify(patient)
});
```

### Patient data shape (must match backend API exactly):
```javascript
{
  id: "TRK-001",
  nationalId: "11165435916",   // 11 digits
  firstName: "John",
  lastName: "Doe",
  gender: "Male",
  age: 25,
  dob: "2000-09-11",           // YYYY-MM-DD
  mobile: "09015344428",
  telephone: null,             // optional
  email: "johndoe@gmail.com",
  bloodType: "O+",
  genotype: "AA",              // AA | AS | SS | AC only
  department: "Orthopedic",
  maritalStatus: "Single",
  doctor: null,                // optional
  country: "Nigeria",
  state: "Rivers State",
  city: "Port Harcourt",
  street: "10 Haven Avenue",
  zip: "500001",
  contacts: [],                // [{type: string, detail: string}]
  status: "Active",            // Active | Inactive
  registeredDate: "2024-01-15", // YYYY-MM-DD
  photo: null                  // base64 string or null
}
```

### Auth response shape expected by frontend:
```javascript
{
  token: "eyJhbGci...",   // JWT — stored as localStorage.getItem('trackit_token')
  user: {
    id: 1,
    email: "admin@trackit.com",
    name: "Dr. Adeyemi"
  }
}
```

---

## Backend — State Unknown, Audit First

Located at `/backend`. Caleb attempted to build this but is unsure
of what he actually produced.

**Before writing any new backend code:**
1. Read all files in /backend to understand what framework is being used,
   what's implemented, what's incomplete or broken
2. Check for: pom.xml or build.gradle (Maven vs Gradle),
   application.properties or application.yml (config),
   any existing controllers, models, repositories, security config
3. Report findings clearly — what exists, what works, what's missing,
   what needs to be fixed or deleted

**Target backend stack:**
- Java 17+
- Spring Boot 3.x
- Spring Web (REST controllers)
- Spring Data JPA (database layer)
- Spring Security + JJWT (JWT authentication)
- PostgreSQL (database)
- Maven (build tool)

**Required API endpoints:**
```
POST   /api/auth/login          → authenticate, return JWT
GET    /api/patients            → list all (supports ?search=, ?department=, ?status=)
POST   /api/patients            → create new patient
GET    /api/patients/{id}       → get single patient
PUT    /api/patients/{id}       → update patient
DELETE /api/patients/{id}       → delete patient
POST   /api/ecg/analyse         → relay ECG data to Python ML service, return result
GET    /api/ecg/leads/{id}      → get stored ECG lead data for a patient
```

**CORS must allow:** the Vercel frontend domain (and localhost:5500 for development)

---

## ML Model — State Unknown, Audit First

Located at `/model/theirs`. This is a model obtained from another group.

**Before integrating anything:**
1. List all files in /model/theirs
2. Identify the model format: .pkl (scikit-learn), .h5 (Keras),
   .pt or .pth (PyTorch), .onnx, or other
3. Look for any README, documentation, or sample code showing
   how to load and run the model
4. Identify what the model accepts as input and what it returns as output
5. Report all findings before writing any integration code

**Target ML service:**
- Python 3.10+
- FastAPI (serves the model as an HTTP API)
- Endpoint: POST /predict — accepts ECG signal data, returns classification

**Expected ML output shape (target):**
```json
{
  "classification": "Normal",
  "confidence": 0.94,
  "leads": [
    { "lead": "I",   "signal": [0.1, 0.3, 0.8, ...] },
    { "lead": "II",  "signal": [0.2, 0.4, 0.9, ...] },
    ...12 leads total
  ]
}
```

---

## Database Schema (target)

```sql
-- patients table
CREATE TABLE patients (
  id              SERIAL PRIMARY KEY,
  patient_code    VARCHAR(10) UNIQUE NOT NULL,  -- TRK-001 format
  national_id     VARCHAR(11) UNIQUE,
  first_name      VARCHAR(100) NOT NULL,
  last_name       VARCHAR(100) NOT NULL,
  gender          VARCHAR(10),
  age             INTEGER,
  dob             DATE,
  mobile          VARCHAR(15),
  telephone       VARCHAR(20),
  email           VARCHAR(255),
  blood_type      VARCHAR(5),
  genotype        VARCHAR(5),
  department      VARCHAR(100),
  marital_status  VARCHAR(20),
  doctor          VARCHAR(100),
  country         VARCHAR(100),
  state           VARCHAR(100),
  city            VARCHAR(100),
  street          VARCHAR(255),
  zip             VARCHAR(10),
  status          VARCHAR(20) DEFAULT 'Active',
  registered_date DATE DEFAULT CURRENT_DATE,
  created_at      TIMESTAMP DEFAULT NOW()
);

-- users table (medical staff)
CREATE TABLE users (
  id           SERIAL PRIMARY KEY,
  email        VARCHAR(255) UNIQUE NOT NULL,
  password     VARCHAR(255) NOT NULL,  -- bcrypt hashed
  full_name    VARCHAR(200),
  role         VARCHAR(50) DEFAULT 'STAFF',
  created_at   TIMESTAMP DEFAULT NOW()
);

-- ecg_sessions table
CREATE TABLE ecg_sessions (
  id              SERIAL PRIMARY KEY,
  patient_id      INTEGER REFERENCES patients(id),
  classification  VARCHAR(50),
  confidence      DECIMAL(5,4),
  lead_data       JSONB,             -- stores the 12 lead signal arrays
  recorded_at     TIMESTAMP DEFAULT NOW()
);
```

---

## Environment Variables Needed

```
# backend/src/main/resources/application.properties
spring.datasource.url=jdbc:postgresql://localhost:5432/trackit
spring.datasource.username=your_db_user
spring.datasource.password=your_db_password
spring.jpa.hibernate.ddl-auto=update
jwt.secret=your_jwt_secret_key_min_256_bits
jwt.expiration=86400000
ml.service.url=http://localhost:8000

# Python ML service (.env)
MODEL_PATH=../model/theirs/
PORT=8000
```

---

## Git Workflow

- Main branch: `main` (protected — requires PR)
- Working branch: `development`
- Always work on `development`
- Commit after each logical unit of work
- Commit message format: `type: description`
  - `feat:` new feature
  - `fix:` bug fix
  - `chore:` setup, config, dependencies
  - `docs:` documentation

---

## How Caleb Works

- Prefers direct, honest responses — no hedging
- Comfortable with vibe coding — generate, test, iterate
- Will test and report back with screenshots or error messages
- Works file by file, not everything at once
- When he says "Begin", "Yes", or "Go" — proceed immediately
- When he says "Talk to me" — he wants discussion not code

---

## Current Session Priority

1. Audit /backend — report what's there
2. Audit /model/theirs — report what's there
3. Based on findings, fix/complete the backend
4. Wrap the ML model in a FastAPI service
5. Connect frontend localStorage calls to real API calls
6. End-to-end demo working

**Start with the audit. Do not write any new code until you have
read and reported on what already exists in /backend and /model/theirs.**