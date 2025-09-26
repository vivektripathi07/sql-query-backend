#Importing required libs
from langchain.utilities import SQLDatabase
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import create_sql_query_chain
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os
import re

load_dotenv(override=True)



host = 'sql12.freesqldatabase.com'
port = '3306'
username = 'sql12799932'
password = os.getenv('SQL_PASS')
database_schema = 'sql12799932'

my_sql_uri = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_schema}"


db = SQLDatabase.from_uri(my_sql_uri)


#Creating LLM prompt template
template =  """  Based on the table schema below, write a SQL query that would answer user's question:
                Remember: Only Provide the SQL query nothing else. Give query in single line dont add line breaks.
                Table Schema: {schema}
                Question: {question}
                SQL Query: 
            """

prompt = PromptTemplate.from_template(template)


def get_schema(db):
    schema = db.get_table_info()
    return schema


llm = ChatGoogleGenerativeAI(
    model = 'gemini-2.0-flash',
    api_key = os.getenv('GEMINI_API_KEY')
)


sql_chain = (
    RunnablePassthrough.assign(schema=lambda _: get_schema(db))
    | prompt
    | llm.bind(stop=["\nSQLResult:"])
    | StrOutputParser()
)


def get_query(question: str):
    resp = sql_chain.invoke({"question": question})

    query = re.search(r"```sql\s*(.*?)\s*```", resp,  re.DOTALL | re.IGNORECASE)

    if(query):
        query = query.group(1).strip()

    return query


q = get_query("Find the sum of total for Walmart")

print(q)
