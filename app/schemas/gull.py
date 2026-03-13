from pydantic import BaseModel, Field


class GullBase(BaseModel):
    tag_id: str = Field(..., min_length=1, max_length=100)
    species: str = Field(..., min_length=1, max_length=150)
    common_name: str | None = Field(default=None, max_length=150)
    study_name: str | None = Field(default=None, max_length=255)


class GullCreate(GullBase):
    pass


class GullUpdate(BaseModel):
    tag_id: str | None = Field(default=None, min_length=1, max_length=100)
    species: str | None = Field(default=None, min_length=1, max_length=150)
    common_name: str | None = Field(default=None, max_length=150)
    study_name: str | None = Field(default=None, max_length=255)


class GullRead(GullBase):
    id: int

    model_config = {"from_attributes": True}