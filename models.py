from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    salt = Column(String, index=True)
    
    # Relationship to samples
    samples = relationship("Sample", back_populates="owner")


class Sample(Base):
    """Model for microbiome samples"""
    __tablename__ = "samples"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    taxonomy = Column(String, index=True)  # e.g., "Bacteria;Proteobacteria;Gammaproteobacteria"
    abundance = Column(Float)  # Relative abundance (0-100%)
    location = Column(String)  # Sample location/source
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationship to user
    owner = relationship("User", back_populates="samples")