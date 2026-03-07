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
