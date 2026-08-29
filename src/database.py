import sqlite3
import pandas as pd
from datetime import datetime
from src.config import DB_PATH

def init_db():
    """
    Initializes the SQLite database and creates the history table if it doesn't exist.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            source TEXT NOT NULL,
            total_persons INTEGER NOT NULL,
            mask_count INTEGER NOT NULL,
            no_mask_count INTEGER NOT NULL,
            confidence REAL NOT NULL,
            alert_triggered INTEGER NOT NULL,
            screenshot_path TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_detection(
    source: str,
    total_persons: int,
    mask_count: int,
    no_mask_count: int,
    confidence: float,
    alert_triggered: bool,
    screenshot_path: str = None
):
    """
    Inserts a single detection record into the SQLite history log.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        """
        INSERT INTO history (
            timestamp, source, total_persons, mask_count, no_mask_count, confidence, alert_triggered, screenshot_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            source,
            total_persons,
            mask_count,
            no_mask_count,
            confidence,
            1 if alert_triggered else 0,
            screenshot_path
        )
    )
    conn.commit()
    conn.close()

def get_history_df(
    search_query: str = None,
    filter_category: str = "All",
    sort_by: str = "Newest First"
) -> pd.DataFrame:
    """
    Retrieves the detection history as a Pandas DataFrame, with search, filtering, and sorting support.
    
    Args:
        search_query: String to search in the source column.
        filter_category: 'All', 'Violations Only', or 'No Violations'.
        sort_by: Sorting preference.
    """
    conn = sqlite3.connect(DB_PATH)
    
    query = "SELECT * FROM history"
    params = []
    conditions = []
    
    if search_query:
        conditions.append("source LIKE ?")
        params.append(f"%{search_query}%")
        
    if filter_category == "Violations Only":
        conditions.append("no_mask_count > 0")
    elif filter_category == "No Violations":
        conditions.append("no_mask_count = 0")
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    if sort_by == "Newest First":
        query += " ORDER BY timestamp DESC"
    elif sort_by == "Oldest First":
        query += " ORDER BY timestamp ASC"
    elif sort_by == "Highest Violation Count":
        query += " ORDER BY no_mask_count DESC"
    elif sort_by == "Highest Confidence":
        query += " ORDER BY confidence DESC"
        
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def clear_history():
    """
    Truncates the history table.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM history")
    conn.commit()
    conn.close()
