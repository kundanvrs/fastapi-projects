from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app import models, schemas, crud, database, cache

app = FastAPI(title="Patient Records API")

@app.on_event("startup")
async def startup():
    async with database.engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

async def get_db_session():
    async for session in database.get_db():
        yield session

@app.post("/patients/", response_model=schemas.PatientResponse)
async def create_patient(patient: schemas.PatientCreate, db: AsyncSession = Depends(get_db_session)):
    new_patient = await crud.create_patient(db, patient)
    await cache.set_cache(f"patient:{new_patient.id}", schemas.PatientResponse.from_orm(new_patient).dict())
    return new_patient

@app.get("/patients/", response_model=List[schemas.PatientResponse])
async def read_patients(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db_session)):
    return await crud.get_patients(db, skip, limit)

@app.get("/patients/{patient_id}", response_model=schemas.PatientResponse)
async def read_patient(patient_id: int, db: AsyncSession = Depends(get_db_session)):
    cached = await cache.get_cache(f"patient:{patient_id}")
    if cached:
        return cached
    patient = await crud.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    await cache.set_cache(f"patient:{patient_id}", schemas.PatientResponse.from_orm(patient).dict())
    return patient

@app.put("/patients/{patient_id}", response_model=schemas.PatientResponse)
async def update_patient(patient_id: int, patient: schemas.PatientUpdate, db: AsyncSession = Depends(get_db_session)):
    updated = await crud.update_patient(db, patient_id, patient)
    if not updated:
        raise HTTPException(status_code=404, detail="Patient not found")
    await cache.set_cache(f"patient:{patient_id}", schemas.PatientResponse.from_orm(updated).dict())
    return updated

@app.delete("/patients/{patient_id}", response_model=schemas.PatientResponse)
async def delete_patient(patient_id: int, db: AsyncSession = Depends(get_db_session)):
    deleted = await crud.delete_patient(db, patient_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Patient not found")
    await cache.delete_cache(f"patient:{patient_id}")
    return deleted