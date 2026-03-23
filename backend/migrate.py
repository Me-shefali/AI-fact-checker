import os
from dotenv import load_dotenv
load_dotenv()

from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text('ALTER TABLE fact_checks ADD COLUMN IF NOT EXISTS confidence FLOAT'))
    conn.execute(text('ALTER TABLE fact_checks ADD COLUMN IF NOT EXISTS evidence_text TEXT'))
    conn.execute(text('ALTER TABLE fact_checks ADD COLUMN IF NOT EXISTS evidence_url TEXT'))
    conn.execute(text('ALTER TABLE fact_checks ADD COLUMN IF NOT EXISTS evidence_source VARCHAR(100)'))
    conn.commit()

print('Migration done.')