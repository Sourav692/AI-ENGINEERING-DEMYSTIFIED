from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from bson import ObjectId
from datetime import datetime


class Equipment(BaseModel):
    id: Optional[str] = Field(None, alias="_id", serialization_alias="_id")
    name: str
    description: str
    tenant_id: str

    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    )
