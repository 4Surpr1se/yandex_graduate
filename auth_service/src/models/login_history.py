import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Enum

from sqlalchemy import (Column, DateTime, ForeignKey, Text, UniqueConstraint,
                        text)
from sqlalchemy.dialects.postgresql import UUID

from src.db.postgres import Base
from enum import Enum as PyEnum



class Provider(PyEnum):
    GOOGLE = "google"
    PASSWORD = "password"

class UserLogin(Base):
    __tablename__ = 'user_login'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow)
    provider = Column(Enum(Provider), nullable=True)

    def __init__(self, user_id: UUID, provider: Provider):
        self.user_id = user_id
        self.provider = provider

    def __repr__(self):
        return f'Logged in at <{self.logged_at}> via {self.provider.value}'

def create_device_partitions(target, connection, **kw) -> None:
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "user_sign_in_web" PARTITION OF "user_sign_in" 
               FOR VALUES IN ('web')"""
        )
    )
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "user_sign_in" 
               FOR VALUES IN ('mobile')"""
        )
    )
    connection.execute(
        text(
            """CREATE TABLE IF NOT EXISTS "user_sign_in_smart" PARTITION OF "user_sign_in" 
               FOR VALUES IN ('smart')"""
        )
    )

def create_single_month_partition(connection, device_type: str, year: int, month: int, **kw) -> None:
    month_start = f"'{year}-{month:02d}-01'"
    month_end = f"'{year}-{(month % 12) + 1:02d}-01'"

    table_name = f"user_sign_in_{device_type}_{year}_{month:02d}"

    connection.execute(
        text(
            f"""
            CREATE TABLE IF NOT EXISTS "{table_name}" PARTITION OF "user_sign_in_{device_type}" 
            FOR VALUES FROM ({month_start}) TO ({month_end});
            """
        )
    )


class UserSignIn(Base):
    __tablename__ = 'user_sign_in'
    __table_args__ = (
        UniqueConstraint('id', 'user_device_type', 'logged_in_at'),
        {
            'postgresql_partition_by': 'LIST (user_device_type)',
            'listeners': [('after_create', create_device_partitions)],
        }
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    logged_in_at = Column(DateTime, default=datetime.utcnow)
    user_device_type = Column(Text, primary_key=True)

    def __repr__(self):
        return f'<UserSignIn {self.user_id}:{self.logged_in_at}>'


def create_partitions_for_all_devices(connection) -> None:
    current_year = datetime.now().year
    current_month = datetime.now().month

    device_types = ['web', 'mobile', 'smart']

    for device in device_types:
        for year in range(2020, current_year + 1):
            for month in range(1, 13):
                if year == current_year and month >= current_month:
                    break
                create_single_month_partition(connection, device, year, month)
