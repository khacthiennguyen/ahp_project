import sqlite3
import json
from datetime import datetime
import numpy as np
import streamlit as st

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect('ahp_results.db')
    c = conn.cursor()
    
    # Check if lambda_max_values and consistency_indices columns exist
    c.execute("PRAGMA table_info(ahp_sessions)")
    columns = [column[1] for column in c.fetchall()]
    
    if "lambda_max_values" not in columns or "consistency_indices" not in columns:
        # Create a new table with all columns
        c.execute('''
        CREATE TABLE IF NOT EXISTS ahp_sessions_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            criteria TEXT,
            alternatives TEXT,
            criteria_matrix TEXT,
            alternative_matrices TEXT,
            criteria_weights TEXT,
            alternative_weights TEXT,
            final_scores TEXT,
            consistency_ratios TEXT,
            lambda_max_values TEXT,
            consistency_indices TEXT,
            timestamp TIMESTAMP
        )
        ''')
        
        # Copy data from old table if it exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ahp_sessions'")
        if c.fetchone():
            c.execute('''
            INSERT INTO ahp_sessions_new 
            (id, name, description, criteria, alternatives, criteria_matrix, alternative_matrices, 
            criteria_weights, alternative_weights, final_scores, consistency_ratios, timestamp)
            SELECT id, name, description, criteria, alternatives, criteria_matrix, alternative_matrices, 
            criteria_weights, alternative_weights, final_scores, consistency_ratios, timestamp
            FROM ahp_sessions
            ''')
            
            # Drop old table and rename new one
            c.execute("DROP TABLE ahp_sessions")
            c.execute("ALTER TABLE ahp_sessions_new RENAME TO ahp_sessions")
    else:
        # Just create the table if it doesn't exist yet
        c.execute('''
        CREATE TABLE IF NOT EXISTS ahp_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            criteria TEXT,
            alternatives TEXT,
            criteria_matrix TEXT,
            alternative_matrices TEXT,
            criteria_weights TEXT,
            alternative_weights TEXT,
            final_scores TEXT,
            consistency_ratios TEXT,
            lambda_max_values TEXT,
            consistency_indices TEXT,
            timestamp TIMESTAMP
        )
        ''')
    
    conn.commit()
    conn.close()

def save_results():
    """Save current results to database"""
    conn = sqlite3.connect('ahp_results.db')
    c = conn.cursor()
    
    # Check if lambda_max_values and consistency_indices exist in session state
    lambda_max_values = json.dumps(st.session_state.lambda_max_values) if hasattr(st.session_state, 'lambda_max_values') else None
    consistency_indices = json.dumps(st.session_state.consistency_indices) if hasattr(st.session_state, 'consistency_indices') else None
    
    # Check if the columns exist in the database
    c.execute("PRAGMA table_info(ahp_sessions)")
    columns = [column[1] for column in c.fetchall()]
    
    if "lambda_max_values" in columns and "consistency_indices" in columns:
        c.execute('''
        INSERT INTO ahp_sessions 
        (name, description, criteria, alternatives, criteria_matrix, alternative_matrices, 
        criteria_weights, alternative_weights, final_scores, consistency_ratios, 
        lambda_max_values, consistency_indices, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            st.session_state.current_session_name,
            st.session_state.current_session_description,
            json.dumps(st.session_state.criteria),
            json.dumps(st.session_state.alternatives),
            json.dumps(st.session_state.criteria_matrix.tolist()),
            json.dumps({k: v.tolist() for k, v in st.session_state.alternative_matrices.items()}),
            json.dumps(st.session_state.criteria_weights.tolist()),
            json.dumps({k: v.tolist() for k, v in st.session_state.alternative_weights.items()}),
            json.dumps(st.session_state.final_scores.tolist()),
            json.dumps(st.session_state.consistency_ratios),
            lambda_max_values,
            consistency_indices,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
    else:
        c.execute('''
        INSERT INTO ahp_sessions 
        (name, description, criteria, alternatives, criteria_matrix, alternative_matrices, 
        criteria_weights, alternative_weights, final_scores, consistency_ratios, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            st.session_state.current_session_name,
            st.session_state.current_session_description,
            json.dumps(st.session_state.criteria),
            json.dumps(st.session_state.alternatives),
            json.dumps(st.session_state.criteria_matrix.tolist()),
            json.dumps({k: v.tolist() for k, v in st.session_state.alternative_matrices.items()}),
            json.dumps(st.session_state.criteria_weights.tolist()),
            json.dumps({k: v.tolist() for k, v in st.session_state.alternative_weights.items()}),
            json.dumps(st.session_state.final_scores.tolist()),
            json.dumps(st.session_state.consistency_ratios),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
    
    conn.commit()
    conn.close()

def get_past_sessions():
    """Get list of past sessions"""
    conn = sqlite3.connect('ahp_results.db')
    c = conn.cursor()
    c.execute('SELECT id, name, timestamp FROM ahp_sessions ORDER BY timestamp DESC')
    past_sessions = c.fetchall()
    conn.close()
    return past_sessions

def get_session_data(session_id):
    """Get data for a specific session"""
    conn = sqlite3.connect('ahp_results.db')
    c = conn.cursor()
    
    # Get column names
    c.execute("PRAGMA table_info(ahp_sessions)")
    columns = [column[1] for column in c.fetchall()]
    
    c.execute('SELECT * FROM ahp_sessions WHERE id = ?', (session_id,))
    session_data_row = c.fetchone()
    conn.close()
    
    if session_data_row:
        # Create a dictionary mapping column names to values
        session_data = {}
        for i, column in enumerate(columns):
            if i < len(session_data_row):
                session_data[column] = session_data_row[i]
        
        # Parse JSON data for required fields
        session_data['criteria'] = json.loads(session_data['criteria'])
        session_data['alternatives'] = json.loads(session_data['alternatives'])
        # Lưu cả dạng list để xuất PDF dễ dàng
        session_data['criteria_matrix_list'] = json.loads(session_data['criteria_matrix'])
        session_data['alternative_matrices_list'] = {k: v for k, v in json.loads(session_data['alternative_matrices']).items()}
        # Dạng np.array cho tính toán
        session_data['criteria_matrix'] = np.array(session_data['criteria_matrix_list'])
        session_data['alternative_matrices'] = {k: np.array(v) for k, v in session_data['alternative_matrices_list'].items()}
        session_data['criteria_weights'] = np.array(json.loads(session_data['criteria_weights']))
        session_data['alternative_weights'] = {k: np.array(v) for k, v in json.loads(session_data['alternative_weights']).items()}
        session_data['final_scores'] = np.array(json.loads(session_data['final_scores']))
        session_data['consistency_ratios'] = json.loads(session_data['consistency_ratios'])
        
        # Parse JSON data for new fields if they exist
        if 'lambda_max_values' in session_data and session_data['lambda_max_values'] is not None:
            session_data['lambda_max_values'] = json.loads(session_data['lambda_max_values'])
        
        if 'consistency_indices' in session_data and session_data['consistency_indices'] is not None:
            session_data['consistency_indices'] = json.loads(session_data['consistency_indices'])
        
        return session_data
    
    return None

def delete_session(session_id):
    """Delete a session from the database by id"""
    conn = sqlite3.connect('ahp_results.db')
    c = conn.cursor()
    c.execute('DELETE FROM ahp_sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()