from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg://admin:password@localhost:5432/business_automation"

engine = create_engine(DATABASE_URL)