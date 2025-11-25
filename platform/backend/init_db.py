from app.db import engine, Base
from app.models import Incident, IncidentMetric

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✓ Database tables created successfully!")
