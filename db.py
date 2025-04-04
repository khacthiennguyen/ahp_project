import sqlite3
import json
from datetime import datetime
import numpy as np

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect('ahp_results.db')
    c = conn.cursor()
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
        timestamp TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def save_results():
    """Save current results to database"""
    conn = sqlite3.connect('ahp_results.db')
    c = conn.cursor()
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
    c.execute('SELECT * FROM ahp_sessions WHERE id = ?', (session_id,))
    session_data = c.fetchone()
    conn.close()
    
    if session_data:
        # Extract data
        session_id, name, description, criteria, alternatives, criteria_matrix, alternative_matrices, criteria_weights, alternative_weights, final_scores, consistency_ratios, timestamp = session_data
        
        # Parse JSON data
        criteria = json.loads(criteria)
        alternatives = json.loads(alternatives)
        criteria_matrix = np.array(json.loads(criteria_matrix))
        alternative_matrices = {k: np.array(v) for k, v in json.loads(alternative_matrices).items()}
        criteria_weights = np.array(json.loads(criteria_weights))
        alternative_weights = {k: np.array(v) for k, v in json.loads(alternative_weights).items()}
        final_scores = np.array(json.loads(final_scores))
        consistency_ratios = json.loads(consistency_ratios)
        
        return {
            'id': session_id,
            'name': name,
            'description': description,
            'criteria': criteria,
            'alternatives': alternatives,
            'criteria_matrix': criteria_matrix,
            'alternative_matrices': alternative_matrices,
            'criteria_weights': criteria_weights,
            'alternative_weights': alternative_weights,
            'final_scores': final_scores,
            'consistency_ratios': consistency_ratios,
            'timestamp': timestamp
        }
    
    return None