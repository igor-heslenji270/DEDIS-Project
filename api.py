from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .database import SessionLocal, engine
from . import models, auth, schemas
from .strategy import (
    SearchContext, 
    ExactMatchStrategy, 
    ApproximateMatchStrategy, 
    HierarchicalMatchStrategy,
    AbundanceFilterStrategy
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    """Dependency Injection - FastAPI's built-in pattern"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




@app.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    
    salt = auth.generate_salt()
    hashed_password = auth.hash_password(user.password, salt)
    
    db_user = models.User(username=user.username, hashed_password=hashed_password, salt=salt)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.post("/login")
def login_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    hashed_attempt = auth.hash_password(user.password, db_user.salt)

    if hashed_attempt != db_user.hashed_password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {"message": "Login successful", "user_id": db_user.id, "username": user.username}




@app.post("/samples/", response_model=schemas.SampleOut)
def create_sample(sample: schemas.SampleCreate, user_id: int, db: Session = Depends(get_db)):
    """Create a new microbiome sample"""
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create sample
    db_sample = models.Sample(
        name=sample.name,
        taxonomy=sample.taxonomy,
        abundance=sample.abundance,
        location=sample.location,
        user_id=user_id
    )
    db.add(db_sample)
    db.commit()
    db.refresh(db_sample)
    return db_sample


@app.get("/samples/", response_model=List[schemas.SampleOut])
def get_all_samples(db: Session = Depends(get_db)):
    """Get all samples"""
    return db.query(models.Sample).all()


@app.get("/samples/user/{user_id}", response_model=List[schemas.SampleOut])
def get_user_samples(user_id: int, db: Session = Depends(get_db)):
    """Get all samples for a specific user"""
    return db.query(models.Sample).filter(models.Sample.user_id == user_id).all()


@app.delete("/samples/{sample_id}")
def delete_sample(sample_id: int, user_id: int, db: Session = Depends(get_db)):
    """Delete a sample"""
    sample = db.query(models.Sample).filter(models.Sample.id == sample_id).first()
    if not sample:
        raise HTTPException(status_code=404, detail="Sample not found")
    if sample.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(sample)
    db.commit()
    return {"message": "Sample deleted successfully"}




@app.get("/search", response_model=List[schemas.SampleOut])
def search_samples(
    query: str,
    strategy: str = "exact",  # Strategy selector: "exact", "approximate", "hierarchical", "abundance"
    min_abundance: float = 0.0,
    max_abundance: float = 100.0,
    db: Session = Depends(get_db)
):
    """
    Unified search endpoint demonstrating Strategy Pattern.
    Strategy is selected at runtime based on the 'strategy' parameter.
    """
    # Get all samples from database
    samples = db.query(models.Sample).all()
    
    # Select strategy based on parameter
    if strategy == "exact":
        search_strategy = ExactMatchStrategy()
    elif strategy == "approximate":
        search_strategy = ApproximateMatchStrategy()
    elif strategy == "hierarchical":
        search_strategy = HierarchicalMatchStrategy()
    elif strategy == "abundance":
        search_strategy = AbundanceFilterStrategy(min_abundance, max_abundance)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid strategy: {strategy}. Valid options: exact, approximate, hierarchical, abundance")
    
    # Execute search using selected strategy
    context = SearchContext(search_strategy)
    results = context.execute_search(query, samples)
    
    return results