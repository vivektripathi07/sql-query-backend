# import sys
# print(sys.executable)


from fastapi import FastAPI, HTTPException
from langchain.utilities import SQLDatabase
from sqlalchemy import create_engine, text
import pandas as pd
import os
from pydantic import BaseModel
from model.query import get_query
from dotenv import load_dotenv

from fastapi.middleware.cors import CORSMiddleware



load_dotenv(override=True)
app = FastAPI(title="MySQL Database API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)





host = 'sql12.freesqldatabase.com'
port = '3306'
username = 'sql12799932'
password = os.getenv('SQL_PASS')
database_schema = 'sql12799932'

my_sql_uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_schema}"


engine = create_engine(my_sql_uri)


@app.get("/")
def root():
    return {"message": "API is live"}


@app.get("/tables")
def list_tables():
    try:
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema=DATABASE()"
        with engine.connect() as conn:
            result = conn.execute(text(query)).fetchall()
        return {"tables": [row[0] for row in result]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

class QueryRequest(BaseModel):
    natural_text: str


@app.post("/query")
def run_query(req: QueryRequest):
    natural_text = req.natural_text
    query = get_query(natural_text)
    query_lower = query.strip().lower()
    if not query_lower.startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
    
    try:
        with engine.connect() as conn:
            df = pd.read_sql(text(query), conn)
        return {"query": query_lower,
                "rows": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    


