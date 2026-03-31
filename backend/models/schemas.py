from typing import Any

from pydantic import BaseModel, Field


class InsertDemotableRequest(BaseModel):
    id: int
    name: str = Field(default="", max_length=20)


class UpdateNameDemotableRequest(BaseModel):
    oldName: str
    newName: str = Field(default="", max_length=20)


class PredictRequest(BaseModel):
    features: dict = Field(default_factory=dict)
    metadata: dict = Field(default_factory=dict)


class TableInsertRequest(BaseModel):
    tableName: str
    values: dict[str, Any] = Field(default_factory=dict)


class TableUpdateRequest(BaseModel):
    tableName: str
    keys: dict[str, Any] = Field(default_factory=dict)
    values: dict[str, Any] = Field(default_factory=dict)


class TableDeleteRequest(BaseModel):
    tableName: str
    keys: dict[str, Any] = Field(default_factory=dict)


class CreateDatasetRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)


class AddGestureLabelRequest(BaseModel):
    label: str = Field(..., min_length=1, max_length=50)


class RecognizeRequest(BaseModel):
    landmarks: list[dict] = Field(..., description="List of 21 MediaPipe landmark dicts.")

class RegisterRequest(BaseModel):
    email: str
    name: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
