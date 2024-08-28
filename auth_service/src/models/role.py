# models/role.py
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session
from src.db.postgres import Base
import uuid

class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String(50), unique=True, nullable=False)

    def __init__(self, name: str) -> None:
        self.name = name

    def __repr__(self) -> str:
        return f'<Role {self.name}>'

    @classmethod
    def seed_roles(cls, session: Session):
        roles = ['subscriber', 'premium', 'admin']
        for role_name in roles:
            role = session.query(cls).filter_by(name=role_name).first()
            if not role:
                session.add(cls(name=role_name))
        session.commit()
