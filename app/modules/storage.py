import json
import sqlite3

from utils.search_flags import contains_pattern


class LogStorage:
    def __init__(self, db_path: str = 'db.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
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

    def add_new_entry(self, entry: dict) -> int:
        request_json = json.dumps(entry["request"])
        response_json = json.dumps(entry["response"])

        flag_in = contains_pattern(entry["request"])
        flag_out = contains_pattern(entry["response"])

        with self.conn:
            cursor = self.conn.execute('''
                INSERT INTO logs (service_ip, service_port, client_ip, client_port, request, response, timestamp, flag_in, flag_out)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry["service_ip"],
                entry["service_port"],
                entry["client_ip"],
                entry["client_port"],
                request_json,
                response_json,
                entry["timestamp"],
                flag_in,
                flag_out
            ))
            log_id = cursor.lastrowid
        return log_id

    def fetch_all_logs(self):
        with self.conn:
            logs = self.conn.execute('SELECT * FROM logs').fetchall()
            return logs

    def __del__(self):
        self.conn.close()


class ChainStorage:
    def __init__(self, db_path: str = 'db.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS chains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_ip TEXT,
                    service_port TEXT,
                    client_ip TEXT,
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

    def add_new_chain(self, client_ip: str, service_ip: str, service_port: str, log_id: int, timestamp: int):
        flag_in, flag_out = self.conn.execute('SELECT flag_in, flag_out FROM logs WHERE id = ?', (log_id,)).fetchone()

        with self.conn:
            cursor = self.conn.execute('''
                INSERT INTO chains (service_ip, service_port, client_ip, start_timestamp, end_timestamp, flag_in, flag_out)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (service_ip, service_port, client_ip, timestamp, timestamp, flag_in, flag_out))
            chain_id = cursor.lastrowid

            self.conn.execute('''
                INSERT INTO chain_logs (chain_id, log_id) VALUES (?, ?)
            ''', (chain_id, log_id))

    def add_request_to_chain(self, chain_id: int, log_id: int, timestamp: int):
        with self.conn:
            self.conn.execute('''
                INSERT INTO chain_logs (chain_id, log_id) VALUES (?, ?)
            ''', (chain_id, log_id))

            self.conn.execute('''
                UPDATE chains SET end_timestamp = ? WHERE id = ?
            ''', (timestamp, chain_id))

            flag_in, flag_out = self.conn.execute('SELECT flag_in, flag_out FROM logs WHERE id = ?',
                                                  (log_id,)).fetchone()
            if flag_in:
                self.conn.execute('''
                    UPDATE chains SET flag_in = 1 WHERE id = ?
                ''', (chain_id,))

            if flag_out:
                self.conn.execute('''
                    UPDATE chains SET flag_out = 1 WHERE id = ?
                ''', (chain_id,))

    def get_last_chain_for_service(self, client_ip: str, service_ip: str, service_port: str) -> dict | None:
        result = self.conn.execute('''
            SELECT id, start_timestamp, end_timestamp FROM chains
            WHERE client_ip = ? AND service_ip = ? AND service_port = ?
            ORDER BY end_timestamp DESC LIMIT 1
        ''', (client_ip, service_ip, service_port)).fetchone()

        if result:
            return {"chain_id": result[0], "start_timestamp": result[1], "end_timestamp": result[2]}
        return None

    def fetch_chain_requests(self, chain_id: int):
        with self.conn:
            result = self.conn.execute('''
                SELECT logs.* FROM logs
                JOIN chain_logs ON chain_logs.log_id = logs.id
                WHERE chain_logs.chain_id = ?
                ORDER BY logs.timestamp ASC
            ''', (chain_id,)).fetchall()
            return [dict(row) for row in result]

    def __del__(self):
        self.conn.close()
