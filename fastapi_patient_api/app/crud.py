from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Patient
from .schemas import PatientCreate, PatientUpdate

async def get_patient(db: AsyncSession, patient_id: int):
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    return result.scalar_one_or_none()

async def get_patients(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Patient).offset(skip).limit(limit))
    return result.scalars().all()

async def create_patient(db: AsyncSession, patient: PatientCreate):
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    await db.commit()
    await db.refresh(db_patient)
    return db_patient

async def update_patient(db: AsyncSession, patient_id: int, patient: PatientUpdate):
    db_patient = await get_patient(db, patient_id)
    if not db_patient:
        return None
    for key, value in patient.dict().items():
        setattr(db_patient, key, value)
    await db.commit()
    await db.refresh(db_patient)
    return db_patient

async def delete_patient(db: AsyncSession, patient_id: int):
    db_patient = await get_patient(db, patient_id)
    if not db_patient:
        return None
    await db.delete(db_patient)
    await db.commit()
    return db_patient