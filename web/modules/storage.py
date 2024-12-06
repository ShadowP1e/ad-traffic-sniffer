import logging
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

from utils.format import format_http_data


class Storage:
    def __init__(self, db_path: str = 'db.db'):
        logging.info(db_path)
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_ip TEXT,
                    service_port TEXT,
                    client_ip TEXT,
                    client_port TEXT,
                    request TEXT,
                    response TEXT,
                    timestamp INTEGER,
                    flag_in BOOLEAN DEFAULT 0,
                    flag_out BOOLEAN DEFAULT 0
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS chains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_ip TEXT,
                    service_ip TEXT,
                    service_port TEXT,
                    start_timestamp INTEGER,
                    end_timestamp INTEGER,
                    flag_in BOOLEAN DEFAULT 0,
                    flag_out BOOLEAN DEFAULT 0
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS chain_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chain_id INTEGER,
                    log_id INTEGER,
                    FOREIGN KEY (chain_id) REFERENCES chains(id),
                    FOREIGN KEY (log_id) REFERENCES logs(id)
                )
            ''')

    def fetch_logs(self, source_ip: str | None = None, port: int | None = None,
                   start_time: datetime | None = None, end_time: datetime | None = None,
                   limit: int = 1000, offset: int = 0) -> list[dict[str, Any]]:
        query = "SELECT * FROM logs WHERE 1=1"
        params = []

        if source_ip:
            query += " AND client_ip LIKE ?"
            params.append(f"%{source_ip}%")
        if port:
            query += " AND service_port = ?"
            params.append(port)
        if start_time:
            query += " AND timestamp >= ?"
            params.append(int(start_time.timestamp()))
        if end_time:
            query += " AND timestamp <= ?"
            params.append(int(end_time.timestamp()))

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()[::-1]]

    def get_new_logs(self, last_log_id: int, source_ip: str | None = None, port: int | None = None,
                     start_time: datetime | None = None, end_time: datetime | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM logs WHERE id > ?"
        params = [last_log_id]

        if source_ip:
            query += " AND client_ip LIKE ?"
            params.append(f"%{source_ip}%")
        if port:
            query += " AND service_port = ?"
            params.append(port)
        if start_time:
            query += " AND timestamp >= ?"
            params.append(int(start_time.timestamp()))
        if end_time:
            query += " AND timestamp <= ?"
            params.append(int(end_time.timestamp()))

        query += " ORDER BY timestamp ASC"
        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def fetch_chains(self, source_ip: str | None = None, port: int | None = None,
                     start_time: datetime | None = None, end_time: datetime | None = None,
                     limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        query = "SELECT * FROM chains WHERE 1=1"
        params = []

        if source_ip:
            query += " AND client_ip LIKE ?"
            params.append(f"%{source_ip}%")
        if port:
            query += " AND service_port = ?"
            params.append(port)
        if start_time:
            query += " AND start_timestamp >= ?"
            params.append(int(start_time.timestamp()))
        if end_time:
            query += " AND end_timestamp <= ?"
            params.append(int(end_time.timestamp()))

        query += " ORDER BY start_timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()[::-1]]


    def get_updated_chains(self, last_timestamp: int, source_ip: str | None = None,
                           port: int | None = None, start_time: datetime | None = None,
                           end_time: datetime | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM chains WHERE end_timestamp > ?"
        params = [last_timestamp]

        if source_ip:
            query += " AND client_ip LIKE ?"
            params.append(f"%{source_ip}%")
        if port:
            query += " AND service_port = ?"
            params.append(port)
        if start_time:
            query += " AND start_timestamp >= ?"
            params.append(int(start_time.timestamp()))
        if end_time:
            query += " AND end_timestamp <= ?"
            params.append(int(end_time.timestamp()))

        query += " ORDER BY end_timestamp ASC"
        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_log_by_id(self, log_id: int) -> Dict[str, Any]:
        cursor = self.conn.execute("SELECT * FROM logs WHERE id = ?", (log_id,))
        row = cursor.fetchone()
        return format_http_data(dict(row)) if row else None

    def get_chain_by_id(self, chain_id: int) -> Dict[str, Any]:
        cursor = self.conn.execute("""
            SELECT * FROM chains WHERE id = ?
        """, (chain_id,))
        chain = cursor.fetchone()
        if not chain:
            return None

        requests_cursor = self.conn.execute("""
            SELECT logs.* FROM logs
            JOIN chain_logs ON logs.id = chain_logs.log_id
            WHERE chain_logs.chain_id = ?
            ORDER BY logs.timestamp
        """, (chain_id,))

        chain_data = dict(chain)
        chain_data["requests"] = [format_http_data(dict(request)) for request in requests_cursor.fetchall()]
        return chain_data

    def __del__(self):
        self.conn.close()
