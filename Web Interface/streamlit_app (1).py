import streamlit as st
import pandas as pd
from datetime import date
import psycopg2
from psycopg2.extras import RealDictCursor

# -----------------------------
# Session state init
# -----------------------------
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'role' not in st.session_state:
    st.session_state.role = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"

# -----------------------------
# DB configuration
# -----------------------------
DB_CONFIG_FALLBACK = {
    "dbname": "smartfarmFinal",
    "user": "postgres",
    "password": "ShahdElsawy181204",
    "host": "localhost",
    "port": "5432",
}

ROLE_TO_DB_USER = {
    "owner": {"user": "farm_owner", "password": "owner123"},
    "worker": {"user": "farm_worker", "password": "worker123"},
    "visitor": {"user": "farm_visitor", "password": "visitor123"},
}

def connect_db():
    """
    Connect to PostgreSQL using the DB role of the current app user.
    Sets search_path to smartfarm so we can use unqualified table names.
    """
    try:
        creds = ROLE_TO_DB_USER.get(st.session_state.get("role"))
        cfg = DB_CONFIG_FALLBACK.copy()
        if creds:
            cfg["user"] = creds["user"]
            cfg["password"] = creds["password"]
        conn = psycopg2.connect(**cfg, options="-c search_path=smartfarm")
        return conn
    except Exception as e:
        st.error(f"Database connection error: {e}")
        return None

def execute_query(query, params=None, fetch=True):
    """
    Execute SQL and return:
      - DataFrame for SELECT
      - dict row for INSERT/UPDATE with RETURNING
      - True for other write operations
      - None on error
    """
    conn = connect_db()
    if not conn:
        return None
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            up = query.lstrip().upper()
            if up.startswith("SELECT"):
                rows = cursor.fetchall()
                return pd.DataFrame(rows)
            elif "RETURNING" in up:
                row = cursor.fetchone()
                conn.commit()
                return row
            else:
                conn.commit()
                return True
    except Exception as e:
        st.error(f"Query error: {e}")
        return None
    finally:
        conn.close()

# -----------------------------
# Role Configuration
# -----------------------------
ROLE_CONFIG = {
    "owner": {
        "title": "Owner Login",
        "header_class": "owner-header",
        "gradient": "linear-gradient(135deg, #16a34a, #22c55e)",
        "btn_gradient": "linear-gradient(135deg, #16a34a, #22c55e)",
        "color": "#166534",
        "light_color": "#f0fdf4",
        "border_color": "#bbf7d0",
        "default_username": "owner"
    },
    "worker": {
        "title": "Worker Login",
        "header_class": "worker-header",
        "gradient": "linear-gradient(135deg, #d97706, #f59e0b)",
        "btn_gradient": "linear-gradient(135deg, #d97706, #f59e0b)",
        "color": "#92400e",
        "light_color": "#fef3c7",
        "border_color": "#fde68a",
        "default_username": "worker"
    },
    "visitor": {
        "title": "Visitor Login",
        "header_class": "visitor-header",
        "gradient": "linear-gradient(135deg, #2563eb, #3b82f6)",
        "btn_gradient": "linear-gradient(135deg, #2563eb, #3b82f6)",
        "color": "#1e40af",
        "light_color": "#eff6ff",
        "border_color": "#bfdbfe",
        "default_username": "visitor"
    }
}

# -----------------------------
# Login Page
# -----------------------------
def login_page():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        font-family: 'Poppins', 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    }
    
    .landing-container {
        min-height: 100vh;
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }
    
    .main-title {
        font-size: 4rem;
        font-weight: 900;
        color: #166534;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .subtitle-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 3rem;
    }
    
    .subtitle-line {
        width: 80px;
        height: 3px;
        background-color: #86efac;
    }
    
    .subtitle {
        font-size: 1.8rem;
        font-weight: 600;
        color: #15803d;
        margin: 0 20px;
    }
    
    .role-title {
        font-size: 2.2rem;
        color: #1f2937;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .roles-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 2rem;
        max-width: 1200px;
        width: 100%;
        margin: 0 auto;
    }
    
    .role-card {
        background: white;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        height: 100%;
    }
    
    .role-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    }
    
    .owner-header {
        background: linear-gradient(135deg, #16a34a, #22c55e);
        padding: 3rem 2rem;
        text-align: center;
    }
    
    .worker-header {
        background: linear-gradient(135deg, #d97706, #f59e0b);
        padding: 3rem 2rem;
        text-align: center;
    }
    
    .visitor-header {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        padding: 3rem 2rem;
        text-align: center;
    }
    
    .role-icon {
        display: inline-block;
        padding: 1.5rem;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        margin-bottom: 1.5rem;
        font-size: 2.5rem;
    }
    
    .role-name {
        font-size: 2rem;
        font-weight: 700;
        color: white;
        margin-bottom: 0.5rem;
    }
    
    .role-body {
        padding: 2.5rem 2rem;
        text-align: center;
    }
    
    .role-description {
        color: #6b7280;
        margin-bottom: 2rem;
        line-height: 1.6;
    }
    
    .access-button {
        width: 100%;
        padding: 1rem 2rem;
        border: 2px solid;
        border-radius: 12px;
        font-size: 1.1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
    }
    
    .owner-button {
        background: linear-gradient(to right, #ffffff, #f0fdf4);
        color: #166534;
        border-color: #bbf7d0;
    }
    
    .owner-button:hover {
        background: linear-gradient(to right, #f0fdf4, #dcfce7);
    }
    
    .worker-button {
        background: linear-gradient(to right, #ffffff, #fef3c7);
        color: #92400e;
        border-color: #fde68a;
    }
    
    .worker-button:hover {
        background: linear-gradient(to right, #fef3c7, #fde68a);
    }
    
    .visitor-button {
        background: linear-gradient(to right, #ffffff, #eff6ff);
        color: #1e40af;
        border-color: #bfdbfe;
    }
    
    .visitor-button:hover {
        background: linear-gradient(to right, #eff6ff, #dbeafe);
    }
    
    .login-container {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 20px;
    }
    
    .login-card {
        width: 100%;
        max-width: 450px;
        background: white;
        border-radius: 24px;
        overflow: hidden;
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
    }
    
    .login-header {
        padding: 40px 30px;
        text-align: center;
        color: white;
    }
    
    .login-icon {
        display: inline-block;
        padding: 20px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 50%;
        margin-bottom: 20px;
        font-size: 2.5rem;
    }
    
    .login-title {
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 8px;
    }
    
    .login-subtitle {
        font-size: 14px;
        opacity: 0.9;
    }
    
    .login-form {
        padding: 40px 30px;
    }
    
    .form-group {
        margin-bottom: 24px;
    }
    
    .form-label {
        display: block;
        font-weight: 600;
        color: #374151;
        margin-bottom: 8px;
        font-size: 14px;
    }
    
    .input-group {
        position: relative;
    }
    
    .input-icon {
        position: absolute;
        left: 16px;
        top: 50%;
        transform: translateY(-50%);
        color: #9ca3af;
        font-size: 18px;
        z-index: 1;
    }
    
    .form-input {
        width: 100%;
        padding: 16px 16px 16px 48px;
        font-size: 16px;
        border: 2px solid #e5e7eb;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    .form-input:focus {
        outline: none;
        border-color: #10b981;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
    }
    
    .error-message {
        background-color: #fef2f2;
        border: 1px solid #fecaca;
        color: #dc2626;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 24px;
        font-size: 14px;
    }
    
    .login-button {
        width: 100%;
        padding: 16px 24px;
        color: white;
        border: none;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    
    .login-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
    }
    
    .owner-login-btn {
        background: linear-gradient(135deg, #16a34a, #22c55e);
    }
    
    .worker-login-btn {
        background: linear-gradient(135deg, #d97706, #f59e0b);
    }
    
    .visitor-login-btn {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
    }
    
    .back-link {
        text-align: center;
        margin-top: 32px;
    }
    
    .back-button {
        color: #6b7280;
        background: none;
        border: none;
        cursor: pointer;
        font-size: 14px;
        transition: color 0.3s ease;
        padding: 8px 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 100%;
    }
    
    .back-button:hover {
        color: #374151;
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

    # Role selection page
    if st.session_state.get('login_step') != 'credentials':
        st.markdown('<div class="landing-container">', unsafe_allow_html=True)
        
        st.markdown('<h1 class="main-title">SmartFarm Pro</h1>', unsafe_allow_html=True)
        
        st.markdown('<div class="subtitle-container">', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<h2 class="role-title">Select Your Role</h2>', unsafe_allow_html=True)
        
        st.markdown('<div class="roles-grid">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div class="role-card">
                <div class="owner-header">
                    <div class="role-icon">👑</div>
                    <h3 class="role-name">Owner</h3>
                    <p style="color: rgba(255,255,255,0.9);">Full Control</p>
                </div>
                <div class="role-body">
                    <p class="role-description">Complete access to all farm management features including financial data and employee management.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Access as Owner", key="owner_select", use_container_width=True):
                st.session_state.login_step = 'credentials'
                st.session_state.selected_role = 'owner'
                st.rerun()
        
        with col2:
            st.markdown(f"""
            <div class="role-card">
                <div class="worker-header">
                    <div class="role-icon">🛠️</div>
                    <h3 class="role-name">Worker</h3>
                    <p style="color: rgba(255,255,255,0.9);">Operations</p>
                </div>
                <div class="role-body">
                    <p class="role-description">Manage daily operations including plant care, animal management, and equipment usage.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Access as Worker", key="worker_select", use_container_width=True):
                st.session_state.login_step = 'credentials'
                st.session_state.selected_role = 'worker'
                st.rerun()
        
        with col3:
            st.markdown(f"""
            <div class="role-card">
                <div class="visitor-header">
                    <div class="role-icon">👁️</div>
                    <h3 class="role-name">Visitor</h3>
                    <p style="color: rgba(255,255,255,0.9);">Read Only</p>
                </div>
                <div class="role-body">
                    <p class="role-description">View farm data and reports without modification privileges.</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Access as Visitor", key="visitor_select", use_container_width=True):
                st.session_state.login_step = 'credentials'
                st.session_state.selected_role = 'visitor'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    else:
        # Login form page
        role = st.session_state.selected_role
        config = ROLE_CONFIG.get(role, ROLE_CONFIG['owner'])
        
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Header
        icon = "👑" if role == "owner" else "🛠️" if role == "worker" else "👁️"
        st.markdown(f"""
        <div class="login-header {config['header_class']}">
            <div class="login-icon">{icon}</div>
            <h1 class="login-title">{config['title']}</h1>
            <p class="login-subtitle">Enter your credentials to access</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Form
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        
        with st.form(key="login_form"):
            # Username field
            st.markdown('<div class="form-group">', unsafe_allow_html=True)
            st.markdown('<label class="form-label">Username</label>', unsafe_allow_html=True)
            st.markdown('<div class="input-group">', unsafe_allow_html=True)
            st.markdown('<div class="input-icon">👤</div>', unsafe_allow_html=True)
            username = st.text_input("", value=config['default_username'], 
                                    placeholder="Enter username", label_visibility="collapsed",
                                    key="username_input")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Password field
            st.markdown('<div class="form-group">', unsafe_allow_html=True)
            st.markdown('<label class="form-label">Password</label>', unsafe_allow_html=True)
            st.markdown('<div class="input-group">', unsafe_allow_html=True)
            st.markdown('<div class="input-icon">🔒</div>', unsafe_allow_html=True)
            password = st.text_input("", type="password", 
                                    placeholder="Enter password", label_visibility="collapsed",
                                    key="password_input")
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Error message placeholder
            error_placeholder = st.empty()
            
            # Login button
            if st.form_submit_button("Login", use_container_width=True):
                if role in ROLE_TO_DB_USER:
                    expected_user = ROLE_TO_DB_USER[role]["user"]
                    expected_pass = ROLE_TO_DB_USER[role]["password"]
                    
                    if username == expected_user and password == expected_pass:
                        st.session_state.authenticated = True
                        st.session_state.role = role
                        st.session_state.username = username
                        st.rerun()
                    else:
                        error_placeholder.error("Invalid credentials. Please try again.")
                else:
                    error_placeholder.error("Invalid role.")
        
        st.markdown('<div class="back-link">', unsafe_allow_html=True)
        if st.button("← Back to Home", use_container_width=True, key="back_home"):
            st.session_state.login_step = None
            st.session_state.selected_role = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Professional Dashboard Page (No Charts)
# -----------------------------
def dashboard_page():
    st.markdown(f"""
    <style>
    .dashboard-title {{
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 1rem;
    }}
    .welcome-text {{
        color: #6b7280;
        margin-bottom: 2rem;
    }}
    .metric-card {{
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-left: 4px solid;
        transition: transform 0.3s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }}
    .metric-value {{
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f2937;
        margin: 0.5rem 0;
    }}
    .metric-label {{
        color: #6b7280;
        font-size: 0.9rem;
        margin: 0;
    }}
    .feature-card {{
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }}
    .feature-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    }}
    .feature-title {{
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #1f2937;
    }}
    .feature-description {{
        color: #6b7280;
        font-size: 0.9rem;
        margin: 0;
    }}
    .status-indicator {{
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 8px;
    }}
    .status-active {{
        background-color: #10b981;
    }}
    .status-inactive {{
        background-color: #ef4444;
    }}
    .data-table {{
        width: 100%;
        border-collapse: collapse;
        margin-top: 1rem;
    }}
    .data-table th {{
        background-color: #f9fafb;
        padding: 0.75rem;
        text-align: left;
        font-weight: 600;
        color: #374151;
        border-bottom: 2px solid #e5e7eb;
    }}
    .data-table td {{
        padding: 0.75rem;
        border-bottom: 1px solid #e5e7eb;
        color: #1f2937;
    }}
    .data-table tr:hover {{
        background-color: #f9fafb;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="dashboard-title">🌱 SmartFarm Pro Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f'<p class="welcome-text">Welcome, {st.session_state.username} — Role: {st.session_state.role}</p>', unsafe_allow_html=True)
    st.markdown("---")

    # KPI Metrics Section
    st.subheader("📊 Farm Overview")
    
    try:
        # Get all metrics
        plants_count = execute_query("SELECT COUNT(*) AS c FROM plants")
        animals_count = execute_query("SELECT COUNT(*) AS c FROM animals")
        workers_count = execute_query("SELECT COUNT(*) AS c FROM workers")
        equipment_count = execute_query("SELECT COUNT(*) AS c FROM equipments")
        
        # Get health status
        animals_healthy = execute_query("SELECT COUNT(*) AS c FROM animals WHERE health_status = 'Healthy'")
        equipment_operational = execute_query("SELECT COUNT(*) AS c FROM equipments WHERE condition = 'Operational'")
        
        # Calculate percentages
        plants_total = int(plants_count['c'][0]) if plants_count is not None and not plants_count.empty else 0
        animals_total = int(animals_count['c'][0]) if animals_count is not None and not animals_count.empty else 0
        animals_healthy_count = int(animals_healthy['c'][0]) if animals_healthy is not None and not animals_healthy.empty else 0
        equipment_total = int(equipment_count['c'][0]) if equipment_count is not None and not equipment_count.empty else 0
        equipment_operational_count = int(equipment_operational['c'][0]) if equipment_operational is not None and not equipment_operational.empty else 0
        workers_total = int(workers_count['c'][0]) if workers_count is not None and not workers_count.empty else 0
        
        animal_health_percent = (animals_healthy_count / animals_total * 100) if animals_total > 0 else 0
        equipment_operational_percent = (equipment_operational_count / equipment_total * 100) if equipment_total > 0 else 0
        
        # Display metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #16a34a;">
                <p class="metric-label">Total Plants</p>
                <div class="metric-value">{plants_total}</div>
                <p style="color: #6b7280; font-size: 0.85rem; margin: 0;">Active in farm</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #d97706;">
                <p class="metric-label">Livestock</p>
                <div class="metric-value">{animals_total}</div>
                <p style="color: #6b7280; font-size: 0.85rem; margin: 0;">
                    <span class="status-indicator status-active"></span>
                    {animals_healthy_count} Healthy ({animal_health_percent:.1f}%)
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #2563eb;">
                <p class="metric-label">Workforce</p>
                <div class="metric-value">{workers_total}</div>
                <p style="color: #6b7280; font-size: 0.85rem; margin: 0;">Active employees</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: #8b5cf6;">
                <p class="metric-label">Equipment</p>
                <div class="metric-value">{equipment_total}</div>
                <p style="color: #6b7280; font-size: 0.85rem; margin: 0;">
                    <span class="status-indicator status-active"></span>
                    {equipment_operational_count} Operational ({equipment_operational_percent:.1f}%)
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        # Fallback metrics if database is not available
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.metric("Total Plants", "24", "+2")
        with col2: st.metric("Livestock", "18", "-1")
        with col3: st.metric("Workforce", "8", "0")
        with col4: st.metric("Equipment", "15", "+1")

    st.markdown("---")

    # Recent Activity Section
    st.subheader("📋 Recent Activity")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">📅 Today's Tasks</div>
            <div style="margin-top: 1rem;">
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                    <span class="status-indicator status-active"></span>
                    <span>Water plants in Section A</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                    <span class="status-indicator status-inactive"></span>
                    <span>Check animal health in Barn 2</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                    <span class="status-indicator status-active"></span>
                    <span>Equipment maintenance schedule</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🔔 Notifications</div>
            <div style="margin-top: 1rem;">
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem; padding: 0.5rem; background: #fef3c7; border-radius: 8px;">
                    <span style="margin-right: 8px;">⚠️</span>
                    <span>2 plants need fertilization</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem; padding: 0.5rem; background: #d1fae5; border-radius: 8px;">
                    <span style="margin-right: 8px;">✅</span>
                    <span>All workers checked in today</span>
                </div>
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem; padding: 0.5rem; background: #fef3c7; border-radius: 8px;">
                    <span style="margin-right: 8px;">📅</span>
                    <span>Quarterly report due in 3 days</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Recent Data Tables
    st.markdown("---")
    st.subheader("📈 Recent Data")
    
    tab1, tab2, tab3 = st.tabs(["🌿 Recent Plants", "🐄 Recent Animals", "👷 Recent Workers"])
    
    with tab1:
        try:
            recent_plants = execute_query("""
                SELECT name, type, plant_date, area
                FROM plants
                ORDER BY plant_date DESC
                LIMIT 5
            """)
            if recent_plants is not None and not recent_plants.empty:
                st.markdown("""
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Plant Name</th>
                            <th>Type</th>
                            <th>Plant Date</th>
                            <th>Area (m²)</th>
                        </tr>
                    </thead>
                    <tbody>
                """, unsafe_allow_html=True)
                
                for _, row in recent_plants.iterrows():
                    st.markdown(f"""
                    <tr>
                        <td>{row['name']}</td>
                        <td>{row['type'] if pd.notnull(row['type']) else 'N/A'}</td>
                        <td>{row['plant_date'] if pd.notnull(row['plant_date']) else 'N/A'}</td>
                        <td>{row['area'] if pd.notnull(row['area']) else '0'}</td>
                    </tr>
                    """, unsafe_allow_html=True)
                
                st.markdown("</tbody></table>", unsafe_allow_html=True)
            else:
                st.info("No plant data available.")
        except Exception:
            st.info("No plant data available.")
    
    with tab2:
        try:
            recent_animals = execute_query("""
                SELECT type, age, weight, health_status
                FROM animals
                ORDER BY animal_id DESC
                LIMIT 5
            """)
            if recent_animals is not None and not recent_animals.empty:
                st.markdown("""
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Type</th>
                            <th>Age (months)</th>
                            <th>Weight (kg)</th>
                            <th>Health Status</th>
                        </tr>
                    </thead>
                    <tbody>
                """, unsafe_allow_html=True)
                
                for _, row in recent_animals.iterrows():
                    health_color = "#10b981" if row['health_status'] == 'Healthy' else "#ef4444" if row['health_status'] == 'Needs Checkup' else "#f59e0b"
                    st.markdown(f"""
                    <tr>
                        <td>{row['type'] if pd.notnull(row['type']) else 'N/A'}</td>
                        <td>{row['age'] if pd.notnull(row['age']) else '0'}</td>
                        <td>{row['weight'] if pd.notnull(row['weight']) else '0'}</td>
                        <td><span style="color: {health_color};">{row['health_status']}</span></td>
                    </tr>
                    """, unsafe_allow_html=True)
                
                st.markdown("</tbody></table>", unsafe_allow_html=True)
            else:
                st.info("No animal data available.")
        except Exception:
            st.info("No animal data available.")
    
    with tab3:
        try:
            recent_workers = execute_query("""
                SELECT name, job, shift
                FROM workers
                ORDER BY worker_id DESC
                LIMIT 5
            """)
            if recent_workers is not None and not recent_workers.empty:
                st.markdown("""
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Job</th>
                            <th>Shift</th>
                        </tr>
                    </thead>
                    <tbody>
                """, unsafe_allow_html=True)
                
                for _, row in recent_workers.iterrows():
                    st.markdown(f"""
                    <tr>
                        <td>{row['name'] if pd.notnull(row['name']) else 'N/A'}</td>
                        <td>{row['job'] if pd.notnull(row['job']) else 'N/A'}</td>
                        <td>{row['shift'] if pd.notnull(row['shift']) else 'N/A'}</td>
                    </tr>
                    """, unsafe_allow_html=True)
                
                st.markdown("</tbody></table>", unsafe_allow_html=True)
            else:
                st.info("No worker data available.")
        except Exception:
            st.info("No worker data available.")

    # Quick Actions Section
    if st.session_state.role in ["owner", "worker"]:
        st.markdown("---")
        st.subheader("⚡ Quick Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🌿 Add New Plant", use_container_width=True):
                st.session_state.current_page = "Plants"
                st.rerun()
        
        with col2:
            if st.button("🐄 Add New Animal", use_container_width=True):
                st.session_state.current_page = "Animals"
                st.rerun()
        
        with col3:
            if st.button("📝 Assign Task", use_container_width=True):
                st.session_state.current_page = "Workers"
                st.rerun()

# -----------------------------
# Other pages remain the same (Plants, Animals, Workers, Equipment, Reports, Settings)
# -----------------------------
def plants_page():
    st.title("🌿 Plants & Crops Management")
    st.markdown("---")

    # View plants
    st.subheader("Current Plants")
    plants_data = execute_query("""
        SELECT plant_id, name, type, area, water_need, fertilizer, plant_date, harvest_date
        FROM plants
        ORDER BY plant_date DESC
    """)
    
    if plants_data is not None and not plants_data.empty:
        # Display with edit/delete options
        st.dataframe(plants_data, use_container_width=True)
        
        # Edit/Delete section (Owner only)
        if st.session_state.role == "owner":
            st.markdown("---")
            st.subheader("Edit / Delete Plant")
            
            # Create two columns for the form
            col1, col2 = st.columns(2)
            
            with col1:
                # Select plant to edit
                plant_options = [f"{row['plant_id']}: {row['name']}" for _, row in plants_data.iterrows()]
                selected_plant = st.selectbox("Select Plant", plant_options, key="plant_select")
                selected_id = int(selected_plant.split(":")[0])
                
                # Get selected plant data
                selected_data = plants_data[plants_data["plant_id"] == selected_id].iloc[0]
                
                # Edit form
                name = st.text_input("Name", value=selected_data["name"], key="edit_name")
                ptype = st.text_input("Type", value=selected_data["type"] if pd.notnull(selected_data["type"]) else "", key="edit_type")
                
            with col2:
                area_val = float(selected_data["area"]) if pd.notnull(selected_data["area"]) else 0.0
                area = st.number_input("Area (m²)", value=area_val, min_value=0.0, step=0.1, format="%.2f", key="edit_area")
                
                water_val = float(selected_data["water_need"]) if pd.notnull(selected_data["water_need"]) else 0.0
                water = st.number_input("Water Need", value=water_val, min_value=0.0, step=0.1, format="%.2f", key="edit_water")
            
            col3, col4 = st.columns(2)
            with col3:
                fert = st.text_input("Fertilizer", value=selected_data["fertilizer"] if pd.notnull(selected_data["fertilizer"]) else "", key="edit_fert")
                pdate = st.date_input("Plant Date", value=selected_data["plant_date"] if pd.notnull(selected_data["plant_date"]) else date.today(), key="edit_pdate")
            
            with col4:
                hdate = st.date_input("Harvest Date", value=selected_data["harvest_date"] if pd.notnull(selected_data["harvest_date"]) else None, key="edit_hdate")
            
            # Action buttons in a row
            col_edit, col_delete, col_space = st.columns([1, 1, 2])
            
            with col_edit:
                if st.button("💾 Save Changes", use_container_width=True, key="save_plant"):
                    ok = execute_query("""
                        UPDATE plants
                           SET name=%s, type=%s, area=%s, water_need=%s, fertilizer=%s, plant_date=%s, harvest_date=%s
                         WHERE plant_id=%s
                    """, (name, ptype or None, area or None, water or None, fert or None, pdate, hdate, selected_id), fetch=False)
                    if ok: 
                        st.success("✅ Plant updated successfully!")
                        st.rerun()
            
            with col_delete:
                if st.button("🗑️ Delete Plant", use_container_width=True, key="delete_plant"):
                    ok = execute_query("DELETE FROM plants WHERE plant_id=%s", (selected_id,), fetch=False)
                    if ok: 
                        st.success("✅ Plant deleted successfully!")
                        st.rerun()
    else:
        st.info("No plants found.")

    # Add New Plant (Owner + Worker)
    if st.session_state.role in ["owner", "worker"]:
        st.markdown("---")
        st.subheader("Add New Plant")
        
        with st.form("add_plant_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                plant_name = st.text_input("Name", key="new_plant_name")
                plant_type = st.text_input("Type", key="new_plant_type")
                area = st.number_input("Area (m²)", min_value=0.0, step=0.1, format="%.2f", key="new_area")
                water_need = st.number_input("Water Need", min_value=0.0, step=0.1, format="%.2f", key="new_water_need")
            with col2:
                fertilizer = st.text_input("Fertilizer", key="new_fertilizer")
                plant_date = st.date_input("Plant Date", value=date.today(), key="new_plant_date")
                harvest_date = st.date_input("Harvest Date", value=None, key="new_harvest_date")
            
            if st.form_submit_button("➕ Add Plant", use_container_width=True):
                row = execute_query(
                    """
                    INSERT INTO plants (name, type, area, water_need, fertilizer, plant_date, harvest_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING plant_id
                    """,
                    (plant_name, plant_type or None, area or None, water_need or None,
                     fertilizer or None, plant_date, harvest_date)
                )
                if row:
                    st.success(f"✅ Plant added with ID {row['plant_id']}")
                    st.rerun()

def animals_page():
    st.title("🐄 Livestock Management")
    st.markdown("---")

    # View animals
    st.subheader("Current Animals")
    animals_data = execute_query("""
        SELECT animal_id, type, age, weight, health_status, vaccination_date
        FROM animals
        ORDER BY type
    """)
    
    if animals_data is not None and not animals_data.empty:
        # Display with edit/delete options
        st.dataframe(animals_data, use_container_width=True)
        
        # Edit/Delete section (Owner only)
        if st.session_state.role == "owner":
            st.markdown("---")
            st.subheader("Edit / Delete Animal")
            
            # Create two columns for the form
            col1, col2 = st.columns(2)
            
            with col1:
                # Select animal to edit
                animal_options = [f"{row['animal_id']}: {row['type']}" for _, row in animals_data.iterrows()]
                selected_animal = st.selectbox("Select Animal", animal_options, key="animal_select")
                selected_id = int(selected_animal.split(":")[0])
                
                # Get selected animal data
                selected_data = animals_data[animals_data["animal_id"] == selected_id].iloc[0]
                
                # Edit form
                atype = st.text_input("Type", value=selected_data["type"] if pd.notnull(selected_data["type"]) else "", key="edit_animal_type")
                
                age_val = int(selected_data["age"]) if pd.notnull(selected_data["age"]) else 0
                age = st.number_input("Age (months)", value=age_val, min_value=0, max_value=240, key="edit_animal_age")
            
            with col2:
                weight_val = int(selected_data["weight"]) if pd.notnull(selected_data["weight"]) else 0
                weight = st.number_input("Weight (kg)", value=weight_val, min_value=0, key="edit_animal_weight")
                
                health_options = ["Healthy", "Needs Checkup", "Under Treatment", "Recovering"]
                current_health = selected_data["health_status"]
                health_index = health_options.index(current_health) if current_health in health_options else 0
                health = st.selectbox("Health Status", health_options, index=health_index, key="edit_animal_health")
                
                vdate = st.date_input("Vaccination Date", 
                                    value=selected_data["vaccination_date"] if pd.notnull(selected_data["vaccination_date"]) else None,
                                    key="edit_animal_vdate")
            
            # Action buttons in a row
            col_edit, col_delete, col_space = st.columns([1, 1, 2])
            
            with col_edit:
                if st.button("💾 Save Changes", use_container_width=True, key="save_animal"):
                    ok = execute_query("""
                        UPDATE animals
                           SET type=%s, age=%s, weight=%s, health_status=%s, vaccination_date=%s
                         WHERE animal_id=%s
                    """, (atype or None, age or None, weight or None, health or None, vdate, selected_id), fetch=False)
                    if ok: 
                        st.success("✅ Animal updated successfully!")
                        st.rerun()
            
            with col_delete:
                if st.button("🗑️ Delete Animal", use_container_width=True, key="delete_animal"):
                    ok = execute_query("DELETE FROM animals WHERE animal_id=%s", (selected_id,), fetch=False)
                    if ok: 
                        st.success("✅ Animal deleted successfully!")
                        st.rerun()
    else:
        st.info("No animals found.")

    # Add New Animal (Owner only)
    if st.session_state.role == "owner":
        st.markdown("---")
        st.subheader("Add New Animal")
        
        with st.form("add_animal_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                atype = st.text_input("Type (e.g., Cow, Chicken)", key="new_animal_type")
                age = st.number_input("Age (months)", min_value=0, max_value=240, value=12, key="new_animal_age")
                weight = st.number_input("Weight (kg)", min_value=0, value=0, key="new_animal_weight")
            with col2:
                health = st.selectbox("Health Status", ["Healthy","Needs Checkup","Under Treatment","Recovering"], key="new_animal_health")
                vdate = st.date_input("Vaccination Date", value=None, key="new_animal_vdate")
            
            if st.form_submit_button("➕ Add Animal", use_container_width=True):
                row = execute_query("""
                    INSERT INTO animals (type, age, weight, health_status, vaccination_date)
                    VALUES (%s,%s,%s,%s,%s)
                    RETURNING animal_id
                """, (atype, age, weight, health, vdate))
                if row:
                    st.success(f"✅ Animal added with ID {row['animal_id']}")
                    st.rerun()

def workers_page():
    st.title("👷 Farm Workers Management")
    st.markdown("---")

    workers_data = execute_query("""
        SELECT worker_id, name, job, phone, salary, shift
        FROM workers
        ORDER BY name
    """)
    
    if workers_data is not None and not workers_data.empty:
        st.dataframe(workers_data, use_container_width=True)
    else:
        st.info("No workers found.")

    # Assign tasks (Owner + Worker)
    if st.session_state.role in ["owner", "worker"]:
        st.markdown("---")
        st.subheader("Assign New Task")
        
        with st.form("assign_task_form", clear_on_submit=True):
            # Get available workers
            worker_options = workers_data["worker_id"].tolist() if workers_data is not None else []
            worker_names = workers_data.set_index("worker_id")["name"].to_dict() if workers_data is not None else {}
            
            # Get available plants and animals
            plants = execute_query("SELECT plant_id, name FROM plants")
            animals = execute_query("SELECT animal_id, type FROM animals")
            
            col1, col2 = st.columns(2)
            with col1:
                if worker_options:
                    wid = st.selectbox("Worker", worker_options, format_func=lambda x: f"{x}: {worker_names.get(x, 'Unknown')}")
                else:
                    wid = st.number_input("Worker ID", min_value=1, value=1)
                
                if plants is not None and not plants.empty:
                    plant_options = plants["plant_id"].tolist()
                    plant_names = plants.set_index("plant_id")["name"].to_dict()
                    plant = st.selectbox("Plant (optional)", [0] + plant_options, 
                                       format_func=lambda x: "None" if x == 0 else f"{x}: {plant_names.get(x, 'Unknown')}")
                else:
                    plant = st.number_input("Plant ID (optional)", min_value=0, value=0)
            
            with col2:
                if animals is not None and not animals.empty:
                    animal_options = animals["animal_id"].tolist()
                    animal_types = animals.set_index("animal_id")["type"].to_dict()
                    animal = st.selectbox("Animal (optional)", [0] + animal_options,
                                        format_func=lambda x: "None" if x == 0 else f"{x}: {animal_types.get(x, 'Unknown')}")
                else:
                    animal = st.number_input("Animal ID (optional)", min_value=0, value=0)
                
                task = st.text_input("Task Description")
                d = st.date_input("Date", date.today())
            
            if st.form_submit_button("📝 Assign Task", use_container_width=True):
                row = execute_query("""
                    INSERT INTO worker_assignments (worker_id, plant_id, animal_id, task, date)
                    VALUES (%s, NULLIF(%s,0), NULLIF(%s,0), %s, %s)
                    RETURNING assignment_id
                """, (int(wid), int(plant), int(animal), task, d))
                if row:
                    st.success(f"✅ Task assigned (ID {row['assignment_id']})")
                    st.rerun()

def equipment_page():
    st.title("🚜 Equipment Management")
    st.markdown("---")

    equipment_data = execute_query("""
        SELECT equipment_id, name, condition, purchase_date, maintenance_date
        FROM equipments
        ORDER BY condition
    """)
    
    if equipment_data is not None and not equipment_data.empty:
        st.dataframe(equipment_data, use_container_width=True)
    else:
        st.info("No equipment found.")

    # Add equipment (Owner only)
    if st.session_state.role == "owner":
        st.markdown("---")
        st.subheader("Add New Equipment")
        
        with st.form("add_equipment_form", clear_on_submit=True):
            name = st.text_input("Equipment Name")
            cond = st.selectbox("Condition", ["Operational","Maintenance","Retired","In Storage"])
            pdate = st.date_input("Purchase Date", value=None)
            mdate = st.date_input("Maintenance Date", value=None)
            
            if st.form_submit_button("➕ Add Equipment", use_container_width=True):
                row = execute_query("""
                    INSERT INTO equipments (name, condition, purchase_date, maintenance_date)
                    VALUES (%s,%s,%s,%s)
                    RETURNING equipment_id
                """, (name, cond, pdate, mdate))
                if row:
                    st.success(f"✅ Equipment added with ID {row['equipment_id']}")
                    st.rerun()

def reports_page():
    st.title("📊 Reports & Analytics")
    st.markdown("---")

    st.subheader("Farm Summary")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Overview")
        try:
            # Get summary statistics
            total_plants = execute_query("SELECT COUNT(*) as count FROM plants")
            total_animals = execute_query("SELECT COUNT(*) as count FROM animals")
            total_workers = execute_query("SELECT COUNT(*) as count FROM workers")
            total_equipment = execute_query("SELECT COUNT(*) as count FROM equipments")
            
            st.metric("Total Plants", total_plants['count'][0] if total_plants is not None else 0)
            st.metric("Total Animals", total_animals['count'][0] if total_animals is not None else 0)
            st.metric("Total Workers", total_workers['count'][0] if total_workers is not None else 0)
            st.metric("Total Equipment", total_equipment['count'][0] if total_equipment is not None else 0)
        except Exception:
            st.info("Unable to load summary statistics")
    
    with col2:
        st.markdown("### 🏥 Health Status")
        try:
            # Get health statistics
            healthy_animals = execute_query("SELECT COUNT(*) as count FROM animals WHERE health_status = 'Healthy'")
            operational_equipment = execute_query("SELECT COUNT(*) as count FROM equipments WHERE condition = 'Operational'")
            
            st.metric("Healthy Animals", healthy_animals['count'][0] if healthy_animals is not None else 0)
            st.metric("Operational Equipment", operational_equipment['count'][0] if operational_equipment is not None else 0)
            
            # Plant types distribution
            plant_types = execute_query("SELECT type, COUNT(*) as count FROM plants GROUP BY type")
            if plant_types is not None and not plant_types.empty:
                st.markdown("#### Plant Types")
                for _, row in plant_types.iterrows():
                    st.write(f"• {row['type']}: {row['count']}")
        except Exception:
            st.info("Unable to load health statistics")
    
    st.markdown("---")
    st.subheader("📋 Detailed Reports")
    
    # Generate report options
    report_type = st.selectbox("Select Report Type", [
        "Plant Inventory",
        "Animal Inventory", 
        "Worker Assignments",
        "Equipment Status"
    ])
    
    if st.button("Generate Report", use_container_width=True):
        st.info(f"Generating {report_type} report...")
        
        if report_type == "Plant Inventory":
            data = execute_query("SELECT * FROM plants ORDER BY plant_date DESC")
            if data is not None and not data.empty:
                st.dataframe(data, use_container_width=True)
            else:
                st.info("No plant data available.")
        
        elif report_type == "Animal Inventory":
            data = execute_query("SELECT * FROM animals ORDER BY type")
            if data is not None and not data.empty:
                st.dataframe(data, use_container_width=True)
            else:
                st.info("No animal data available.")
        
        elif report_type == "Worker Assignments":
            data = execute_query("""
                SELECT w.name, wa.task, wa.date, p.name as plant_name, a.type as animal_type
                FROM worker_assignments wa
                LEFT JOIN workers w ON w.worker_id = wa.worker_id
                LEFT JOIN plants p ON p.plant_id = wa.plant_id
                LEFT JOIN animals a ON a.animal_id = wa.animal_id
                ORDER BY wa.date DESC
            """)
            if data is not None and not data.empty:
                st.dataframe(data, use_container_width=True)
            else:
                st.info("No assignment data available.")
        
        elif report_type == "Equipment Status":
            data = execute_query("SELECT * FROM equipments ORDER BY condition")
            if data is not None and not data.empty:
                st.dataframe(data, use_container_width=True)
            else:
                st.info("No equipment data available.")

def settings_page():
    st.title("⚙️ Settings")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("User Information")
        st.info(f"""
        **Username:** {st.session_state.username}
        **Role:** {st.session_state.role}
        **Access Level:** {'Full' if st.session_state.role == 'owner' else 'Limited' if st.session_state.role == 'worker' else 'Read-only'}
        """)
    
    with col2:
        st.subheader("Database Connection")
        if st.button("Test Connection", use_container_width=True):
            conn = connect_db()
            if conn:
                st.success("✅ Connected successfully!")
                conn.close()
            else:
                st.error("❌ Connection failed")
    
    st.markdown("---")
    st.subheader("Logout")
    if st.button("🔒 Logout", use_container_width=True, type="primary"):
        st.session_state.authenticated = False
        st.session_state.role = None
        st.session_state.username = None
        st.session_state.selected_role = None
        st.session_state.login_step = None
        st.session_state.current_page = "Dashboard"
        st.rerun()

# -----------------------------
# Sidebar Navigation
# -----------------------------
def create_sidebar():
    role = st.session_state.role
    config = ROLE_CONFIG.get(role, ROLE_CONFIG['owner'])
    
    st.markdown(f"""
    <style>
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {config['color']} 0%, {config['color']} 100%);
    }}
    
    [data-testid="stSidebar"] * {{
        color: white !important;
    }}
    
    .sidebar-header {{
        padding: 2rem 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1rem;
    }}
    
    .sidebar-title {{
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }}
    
    .sidebar-subtitle {{
        color: {config['light_color']};
        font-size: 0.9rem;
        opacity: 0.8;
    }}
    
    .stButton > button {{
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        border: none;
        width: 100%;
        padding: 12px;
        border-radius: 12px;
        margin-bottom: 8px;
        text-align: left;
        font-size: 16px;
        transition: all 0.3s ease;
    }}
    
    .stButton > button:hover {{
        background-color: rgba(255, 255, 255, 0.2);
    }}
    
    .active-button {{
        background-color: rgba(255, 255, 255, 0.15) !important;
        font-weight: 600;
    }}
    </style>
    """, unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-header">
            <div class="sidebar-title">SmartFarm Pro</div>
            <div class="sidebar-subtitle">{config['title']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.write(f"**User:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.role}")
        st.markdown("---")
        
        # Navigation buttons
        pages = {
            "Dashboard": "🏠 Dashboard",
            "Plants": "🌿 Plants",
            "Animals": "🐄 Animals",
            "Workers": "👷 Workers",
            "Equipment": "🚜 Equipment",
            "Reports": "📊 Reports",
            "Settings": "⚙️ Settings"
        }
        
        # Filter pages based on role
        if role == "visitor":
            pages = {k: v for k, v in pages.items() if k in ["Dashboard", "Reports"]}
        elif role == "worker":
            pages = {k: v for k, v in pages.items() if k not in ["Settings"]}
        
        current_page = st.session_state.current_page
        
        for page_name, page_label in pages.items():
            if st.button(page_label, key=f"nav_{page_name}", use_container_width=True):
                st.session_state.current_page = page_name
                st.rerun()
        
        st.markdown("---")
        
        # Logout button
        if st.button("🔒 Logout", key="logout_btn", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.session_state.username = None
            st.session_state.selected_role = None
            st.session_state.login_step = None
            st.session_state.current_page = "Dashboard"
            st.rerun()

# -----------------------------
# Main App
# -----------------------------
def main():
    st.set_page_config(
        page_title="SmartFarm Pro",
        page_icon="🌱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply global styles
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Poppins', 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
    }
    
    .stButton > button {
        font-weight: 600;
        border-radius: 12px;
        transition: all 0.3s ease;
    }
    
    h1, h2, h3, h4 {
        font-weight: 600;
    }
    
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state.authenticated:
        login_page()
        return
    
    create_sidebar()
    
    # Route to selected page
    current_page = st.session_state.current_page
    if current_page == "Dashboard":
        dashboard_page()
    elif current_page == "Plants":
        plants_page()
    elif current_page == "Animals":
        animals_page()
    elif current_page == "Workers":
        workers_page()
    elif current_page == "Equipment":
        equipment_page()
    elif current_page == "Reports":
        reports_page()
    elif current_page == "Settings":
        settings_page()

if __name__ == "__main__":
    main()