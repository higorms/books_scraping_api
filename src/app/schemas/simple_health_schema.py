"""Schema para resposta do health check simples."""
from pydantic import BaseModel, ConfigDict


class SimpleHealthSchema(BaseModel):
    """Schema Pydantic para resposta do endpoint de health check simples."""
    status: str

    model_config = ConfigDict(from_attributes=True)
