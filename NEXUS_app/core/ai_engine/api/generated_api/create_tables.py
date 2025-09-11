from database.config import Base, engine
from database.models import User, Workflow

Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully")
