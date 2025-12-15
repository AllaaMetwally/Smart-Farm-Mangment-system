
1. Install Dependencies
bash
pip install streamlit pandas psycopg2-binary
2. Setup PostgreSQL Database
sql
-- Run these commands in PostgreSQL
CREATE DATABASE smartfarmfinal;

-- Create roles for login
CREATE ROLE farm_owner WITH LOGIN PASSWORD 'owner123';
CREATE ROLE farm_worker WITH LOGIN PASSWORD 'worker123';
CREATE ROLE farm_visitor WITH LOGIN PASSWORD 'visitor123';

-- Grant database access
GRANT CONNECT ON DATABASE smartfarmfinal TO farm_owner, farm_worker, farm_visitor;
3. Update Configuration
In streamlit_app.py, find DB_CONFIG_FALLBACK and update:

python
DB_CONFIG_FALLBACK = {
    "dbname": "smartfarmfinal",
    "user": "postgres",           # Your PostgreSQL username
    "password": "your_password",  # Your PostgreSQL password
    "host": "localhost",
    "port": "5432",
}
4. Run the Application
bash
streamlit run streamlit_app.py



🔐 Login Credentials

Role	Username	Password	Access

Owner	farm_owner	owner123	Full control

Worker	farm_worker	worker123	Operations

Visitor	farm_visitor	visitor123	Read-only



📁 Application Structure

text
streamlit_app.py        # Main application
requirements.txt        # Python dependencies
README.md              # This file



🚨 Troubleshooting

Database error: Make sure PostgreSQL is running (sudo service postgresql start)

Port conflict: Use --server.port 8502

Missing tables: Create tables using provided SQL scripts



⚠️ Important Notes

Default URL: http://localhost:8501

For production: Store passwords in environment variables

This is a demo application with hardcoded credentials

Add proper error handling for production use



📞 Quick Help

Open http://localhost:8501 in browser

Select your role

Use credentials above to login

Start managing your farm data

