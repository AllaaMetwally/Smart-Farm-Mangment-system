# 🚀 Website Interface Setup Guide

## 📋 Overview
This guide provides step-by-step instructions to set up and run the SmartFarm web interface locally.

## 🛠️ Prerequisites
- Python 3.8+ installed

- PostgreSQL installed and running

- Streamlit (will be installed in Step 1)


## 📥 Installation Steps
### 1. Install Python Dependencies
   - pip install streamlit pandas psycopg2-binary
    
### 2. Setup PostgreSQL Database
   - Run these commands in PostgreSQL:
      - CREATE DATABASE smartfarmfinal;
      - CREATE ROLE farm_owner WITH LOGIN PASSWORD 'owner123';
      - CREATE ROLE farm_worker WITH LOGIN PASSWORD 'worker123';
      - CREATE ROLE farm_visitor WITH LOGIN PASSWORD 'visitor123';
      - GRANT CONNECT ON DATABASE smartfarmfinal TO farm_owner, farm_worker, farm_visitor;

### 3. Configure Database Connection
    In streamlit_app.py, update the DB_CONFIG_FALLBACK section:
    DB_CONFIG_FALLBACK = {
    "dbname": "smartfarmfinal",
    "user": "postgres",           # Your PostgreSQL username
    "password": "your_password",  # Your PostgreSQL password
    "host": "localhost",
    "port": "5432",
}
### 4. 
