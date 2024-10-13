from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.models.login_history import Provider
from src.models.user import User

Base = declarative_base()

class UserSocialAccount(Base):
    __tablename__ = "user_social_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(Enum(Provider), nullable=False)
    social_id = Column(String, nullable=False, index=True, unique=True) 

    user = relationship("User", back_populates="social_accounts")