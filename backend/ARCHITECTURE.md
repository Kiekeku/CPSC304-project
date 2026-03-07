# Backend Extension Guide

## Where to Add SQL Tables and Seed Data
- Schema changes: `backend/sql/demotable_schema.sql`
- Optional sample rows: `backend/sql/demotable_seed.sql`
- These scripts run from `services/demotable_service.py::initiate_demotable()`.

## Where to Add New Backend Features
- Add new API route modules under `backend/routers/`.
- Add business logic under `backend/services/`.
- Register routers in `backend/main.py` with `app.include_router(...)`.

## ML Integration Path
- Request schema: `backend/models/schemas.py::PredictRequest`
- Route: `backend/routers/ml_router.py`
- Model logic: `backend/services/ml_service.py::predict`

Recommended pattern:
1. Define/extend request model in `models/schemas.py`
2. Keep route handler thin in `routers/*.py`
3. Put DB + ML logic in `services/*.py`
