import streamlit as st
from pathlib import Path
#Accepts nlp as input-convert it into sql queries-execute them-return them as nl results
from langchain.agents import create_sql_agent
from langchain.agents.agent_types import AgentType
from langchain.sql_database import SQLDatabase
from langchain.callbacks import StreamlitCallbackHandler
import sqlite3
from sqlalchemy import create_engine
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_groq import ChatGroq

st.title("Langchain: Chat with SQL DB")

LOCAL_DB="USE_LOCAL"
MYSQL="USE_MYSQL"

radio_opt=['Use sqlite3 Database-student.db',
           'Connect to your SQL Database']
selected_opt=st.sidebar.radio("Choose a Database that you want to chat with",options=radio_opt)
if radio_opt.index(selected_opt)==1:
    db_uri=MYSQL
    sql_host=st.sidebar.text_input("Enter your MYSQL host")
    sql_user=st.sidebar.text_input("MYSQL username")
    sql_password=st.sidebar.text_input("MYSQL password",type="password")
    sql_db=st.sidebar.text_input("MYSQL database")
else:
    db_uri=LOCAL_DB

api_key=st.sidebar.text_input("Enter your GROQ api key",type="password")

if not db_uri:
    st.info("Please provide the database information and the uri")

if not api_key:
    st.info("Please provide your GROQ api key")
    st.stop()
if api_key:
    model=ChatGroq(groq_api_key=api_key,model='llama3-8b-8192',streaming=True)



@st.cache_resource(ttl="2h")
def configure_db(db_uri,sql_host=None,sql_user=None,sql_password=None,sql_db=None):
    if db_uri==LOCAL_DB:
        dbfilepath=(Path(__file__).parent/'student.db').absolute()
        print(dbfilepath)
        creator=lambda:sqlite3.connect(f'file:{dbfilepath}?mode=ro',uri=True)
        return SQLDatabase(create_engine('sqlite:///',creator=creator))
    elif db_uri==MYSQL:
        if not(sql_host and sql_db and sql_password and sql_user):
            st.error("Please provide all the required information for MYSQL connection")
            st.stop()
        return SQLDatabase(create_engine(f'mysql+mysqlconnector://{sql_user}:{sql_password}@{sql_host}/{sql_db}'))
    
if db_uri==LOCAL_DB:
    db=configure_db(db_uri)
else:
    db=configure_db(db_uri,sql_host,sql_user,sql_password,sql_db)

# create_engine: creating a uri to connect to database
# SQL database : a wrapper wrapping the db_uri into a form that langchain can use or a bridge between langchain and db
# sql database toolkit: provides tools to access that db that sql database provides
# agent : finnaly will take the query from input and execute it using the toolkit
# all of these have to be used together always

#Toolkit
toolkit=SQLDatabaseToolkit(db=db,llm=model)

#Agent
agent=create_sql_agent(
    llm=model,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True
    
)

if "messages" not in st.session_state or st.button('Clear message History'):
    st.session_state['messages']=[
        {'role':'assistant',
        'content':'How can I help you today?'}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg['role']).write(msg['content'])

user_prompt=st.chat_input("Ask any query realted to the Database")
if user_prompt:
    st.session_state.messages.append({'role':'user','content':user_prompt})
    st.chat_message('user').write(user_prompt)
    with st.chat_message('assistant'):
        st_cl=StreamlitCallbackHandler(st.container())
        response=agent.run(user_prompt,callbacks=[st_cl])
        st.session_state.messages.append({'role':'assistant','content':response})
        st.write(response)