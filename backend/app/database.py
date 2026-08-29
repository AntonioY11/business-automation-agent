import psycopg

DATABASE_URL = (
    "postgresql://admin:password@localhost:5432/business_automation"
)


def get_connection():
    return psycopg.connect(DATABASE_URL)
