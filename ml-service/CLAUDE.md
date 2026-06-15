# CLAUDE.md — ECG ML Service

A FastAPI microservice that classifies cardiac rhythm from a raw ECG signal
and returns 12-lead data derived from that input. Called internally by the
Spring Boot backend; not exposed directly to the frontend.

---

## Stack

- Python 3.12, FastAPI, Uvicorn
- neurokit2 — R-peak detection and signal cleaning
- numpy / scipy

No PyTorch. The other group's `ecg_wearable_triage.ipynb` (WearableTriageModel,
Conv1d + BiLSTM) was **not used** — no trained weights exist in the repo, it
requires PPG input that Trackit doesn't collect, and its output schema doesn't
match `{classification, confidence, leads}`.

---

## Endpoints

### GET /health
```json
{ "status": "ok" }
```

### POST /predict

**Request:**
```json
{
  "patientId": "TRK-001",
  "signal": [0.1, 0.3, 0.8]
}
```
`signal` is a raw float array treated as Lead II at 360 Hz.
Minimum 500 samples; shorter signals return `"Unavailable"`.

**Response:**
```json
{
  "patientId": "TRK-001",
  "classification": "Normal",
  "confidence": 0.95,
  "leads": {
    "I":   [500 floats],
    "II":  [500 floats],
    "III": [500 floats],
    "aVR": [500 floats], "aVL": [500 floats], "aVF": [500 floats],
    "V1":  [500 floats], "V2":  [500 floats], "V3":  [500 floats],
    "V4":  [500 floats], "V5":  [500 floats], "V6":  [500 floats]
  }
}
```

---

## Classification logic (`ecg_processor.py`)

Input signal is treated as Lead II at 360 Hz.

1. `len(signal) < 500` → `"Unavailable", 0.0`
2. `nk.ecg_clean()` → `nk.ecg_peaks()` to find R-peaks
3. `< 2` R-peaks → `"Chaotic", 0.2`
4. Compute mean RR interval and CV (`std_RR / mean_RR`):

| Condition | Label | Confidence |
|---|---|---|
| CV > 0.50 | Chaotic | 0.2–0.4 |
| 0.15 < CV ≤ 0.50 | Atrial Fibrillation | 0.5–0.95 |
| HR > 100 BPM | Tachycardia | 0.6–0.95 |
| HR < 60 BPM | Bradycardia | 0.6–0.95 |
| else | Normal | 0.7–0.95 |

Confidence scales with rhythm regularity (`1 − CV / threshold`).

---

## Lead derivation (`ecg_processor.py`)

Input truncated/padded to exactly 500 samples → used as Lead II.

| Lead | Formula |
|---|---|
| I | `0.7 × II` |
| III | `II − I` (Einthoven: I + III = II) |
| aVR | `−(I + II) / 2` |
| aVL | `I − II / 2` |
| aVF | `II − I / 2` |
| V1–V6 | `ratio × II` with ratios −0.3, −0.1, 0.2, 0.5, 0.8, 0.9 |

V1–V6 are stylised approximations of normal R-wave progression.

---

## File structure

```
ml-service/
├── main.py                  — FastAPI app, Pydantic models, routes
├── ecg_processor.py         — classify() + derive_leads() + analyse()
├── requirements.txt         — production dependencies
├── requirements-dev.txt     — pytest (dev only)
├── Dockerfile               — container image
├── conftest.py              — pytest sys.path setup
└── tests/
    └── test_ecg_processor.py
```

---

## Running locally

```bash
cd ml-service
pip install -r requirements.txt
python main.py
# Uvicorn running on http://0.0.0.0:8000
```

## Running tests

```bash
cd ml-service
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Docker

```bash
cd ml-service
docker build -t trackit-ml .
docker run -p 8000:8000 trackit-ml
# Override port:  docker run -e PORT=9000 -p 9000:9000 trackit-ml
```

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8000` | Port Uvicorn listens on |
