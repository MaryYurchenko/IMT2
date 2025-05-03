from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class MeasurementBase(BaseModel):
    weight: float
    height: float
    notes: Optional[str] = None

class MeasurementCreate(MeasurementBase):
    pass

class MeasurementUpdate(BaseModel):
    weight: Optional[float] = None
    height: Optional[float] = None
    notes: Optional[str] = None

class MeasurementInDBBase(MeasurementBase):
    id: int
    user_id: int
    measured_at: datetime

    class Config:
        orm_mode = True

class Measurement(MeasurementInDBBase):
    pass

class MeasurementInDB(MeasurementInDBBase):
    pass