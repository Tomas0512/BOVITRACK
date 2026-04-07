import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReactivationRequestCreate(BaseModel):
    email: str
    reason: str | None = None


class ReactivationRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    reason: str | None
    status: str
    created_at: datetime
    reviewed_at: datetime | None


class ReactivationRequestDetail(ReactivationRequestResponse):
    user_email: str
    user_name: str
