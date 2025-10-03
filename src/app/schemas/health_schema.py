from pydantic import BaseModel, ConfigDict


class HealthSchema(BaseModel):
    """Schema Pydantic para resposta do endpoint de health check."""
    status: str
    database_connection: bool
    message: str

    model_config = ConfigDict(from_attributes=True)
