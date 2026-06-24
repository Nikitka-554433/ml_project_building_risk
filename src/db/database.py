import sqlite3
from datetime import datetime
from typing import Dict, Any, List

DB_PATH = "predictions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wall_material TEXT,
            avg_house_area REAL,
            avg_construction_period REAL,
            foundation_type TEXT,
            roof_type TEXT,
            usage_count INTEGER,
            predicted_cost REAL,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_prediction(params: Dict[str, Any], predicted_cost: float) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO predictions (
            wall_material, avg_house_area, avg_construction_period,
            foundation_type, roof_type, usage_count,
            predicted_cost, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        params['wall_material'], params['avg_house_area'],
        params['avg_construction_period'], params['foundation_type'],
        params['roof_type'], params['usage_count'],
        predicted_cost, datetime.now().isoformat()
    ))
    conn.commit()
    last_id = c.lastrowid
    conn.close()
    return last_id

def get_history(limit: int = 10) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM predictions ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]
