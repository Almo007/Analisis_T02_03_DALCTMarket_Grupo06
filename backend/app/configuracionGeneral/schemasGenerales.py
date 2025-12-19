from pydantic import BaseModel
from typing import Any, Optional

class respuestaApi(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
