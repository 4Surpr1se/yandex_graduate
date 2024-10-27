from uuid import UUID, uuid4
from datetime import datetime
from pydantic import Field
from beanie import Document


class BaseMixin(Document):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
