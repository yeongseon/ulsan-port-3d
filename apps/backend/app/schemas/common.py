from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProblemDetail(APIModel):
    type: str = "about:blank"
    title: str
    status: int
    detail: str
    instance: str | None = None
