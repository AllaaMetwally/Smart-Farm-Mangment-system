# 🚀 Website Interface Setup Guide

## 📋 Overview
This guide provides step-by-step instructions to set up and run the SmartFarm web interface locally.

## 🛠️ Prerequisites
- Python 3.8+ installed

- PostgreSQL installed and running

- Streamlit (will be installed in Step 1)


## 📥 Installation Steps
      pip install streamlit pandas psycopg2-binary

    
## 🗄️ Database Setup

      CREATE DATABASE smartfarmfinal;
      CREATE ROLE farm_owner WITH LOGIN PASSWORD 'owner123';
      GRANT CONNECT ON DATABASE smartfarmfinal TO farm_owner;


## ⚙️ Configure
   - In streamlit_app.py, update the DB_CONFIG_FALLBACK section:
    
         DB_CONFIG_FALLBACK = {
          "dbname": "smartfarmfinal",
          "user": "postgres",
          "password": "your_password",
          "host": "localhost",
          "port": "5432", }
    
## ▶️ Run

      streamlit run streamlit_app.py


## 🔐 Login Credentials

      Role	Username	Password	Access
      Owner	farm_owner	owner123	Full
      Worker	farm_worker	worker123	Operations
      Visitor	farm_visitor	visitor123	View Only

## 🌐 Access the Application
Once running, open your browser and navigate to:
👉 http://localhost:8501


## 🚨 Quick Fixes
- DB not running: sudo service postgresql start

- Port busy: streamlit run app.py --server.port 8502

- Import errors: pip install -r requirements.txt

