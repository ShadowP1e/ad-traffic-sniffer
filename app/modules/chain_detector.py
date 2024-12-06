import logging
from modules.storage import ChainStorage

class ChainDetector:
    def __init__(self, db_path: str = 'db.db', max_time_diff: int = 5):
        self.max_time_diff = max_time_diff
        self.storage = ChainStorage(db_path)

    def add_request(self, client_ip: str, service_ip: str, service_port: str, request_data: dict):
        current_time = request_data['timestamp']
        log_id = request_data['log_id']  # Предполагаем, что log_id уже известен для каждого запроса

        last_chain = self.storage.get_last_chain_for_service(client_ip, service_ip, service_port)

        if last_chain:
            time_diff = current_time - last_chain["end_timestamp"]

            if time_diff <= self.max_time_diff:
                self.storage.add_request_to_chain(last_chain["chain_id"], log_id, current_time)
                logging.info(f"Добавлен запрос в существующую цепочку для {client_ip} -> {service_ip}:{service_port}")
            else:
                self._start_new_chain(client_ip, service_ip, service_port, log_id, current_time)
        else:
            self._start_new_chain(client_ip, service_ip, service_port, log_id, current_time)

    def _start_new_chain(self, client_ip: str, service_ip: str, service_port: str, log_id: int, timestamp: int):
        self.storage.add_new_chain(client_ip, service_ip, service_port, log_id, timestamp)
        logging.info(f"Создана новая цепочка для {client_ip} -> {service_ip}:{service_port}")
