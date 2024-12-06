import logging
from pyshark.packet.packet import Packet

from config import config
from modules.storage import LogStorage
from modules.chain_detector import ChainDetector
from utils.normalize import normalize_http_data
from utils.time import get_current_unix_timestamp


class Sniffer:
    def __init__(self, database_path: str,
                 timeout_request: int = 30, timeout_chain: int = 5):
        self.http_pair = {}
        self.storage = LogStorage(db_path=database_path)
        self.timeout_request = timeout_request
        self.chain_detector = ChainDetector(
            db_path=database_path,
            max_time_diff=timeout_chain
        )

    def process_packet(self, packet: Packet):
        if 'http' in packet:

            self.clean_stale_requests()

            if hasattr(packet.http, 'request_method') and packet.tcp.dstport != config.APP_PORT:
                logging.info("===== HTTP ЗАПРОС =====")
                self.process_request(packet)

            if hasattr(packet.http, 'response_code') and packet.tcp.srcport != config.APP_PORT:
                logging.info("===== HTTP ОТВЕТ =====")
                self.process_response(packet)

    def process_request(self, packet: Packet):
        try:
            key = (packet.ip.src, packet.tcp.srcport, packet.ip.dst, packet.tcp.dstport)

            self.http_pair[key] = {}
            self.http_pair[key]['request'] = {"timestamp": get_current_unix_timestamp()}

            for field in packet.http.field_names:
                self.http_pair[key]['request'][field] = packet.http.get_field(field)

        except Exception as e:
            logging.error(f"Не удалось обработать пакет запроса. Ошибка: {str(e)}")

    def process_response(self, packet: Packet):
        try:
            key = (packet.ip.dst, packet.tcp.dstport, packet.ip.src, packet.tcp.srcport)

            if key in self.http_pair:
                self.http_pair[key]['response'] = {"timestamp": get_current_unix_timestamp()}
            else:
                self.http_pair[key] = {
                    'request': {"timestamp": get_current_unix_timestamp()},
                    'response': {"timestamp": get_current_unix_timestamp()},
                }

            for field in packet.http.field_names:
                self.http_pair[key]['response'][field] = packet.http.get_field(field)

            self.add_to_storage(key)

        except Exception as e:
            logging.error(f"Не удалось обработать пакет ответа. Ошибка: {str(e)}")

    def add_to_storage(self, key):
        if self.http_pair[key]['response'] and self.http_pair[key]['request']:
            self.http_pair[key]['timestamp'] = get_current_unix_timestamp()
            self.http_pair[key]['service_ip'] = key[2]
            self.http_pair[key]['service_port'] = key[3]
            self.http_pair[key]['client_ip'] = key[0]
            self.http_pair[key]['client_port'] = key[1]

            normalized_data = normalize_http_data(self.http_pair[key])

            log_id = self.storage.add_new_entry(normalized_data)

            normalized_data['log_id'] = log_id
            self.chain_detector.add_request(
                client_ip=normalized_data['client_ip'],
                service_ip=normalized_data['service_ip'],
                service_port=normalized_data['service_port'],
                request_data=normalized_data
            )

            del self.http_pair[key]

    def clean_stale_requests(self):
        current_time = get_current_unix_timestamp()
        stale_keys = []
        for key, pair in self.http_pair.items():
            request_timestamp = pair['request'].get('timestamp')
            if request_timestamp and 'response' not in pair:
                if current_time - request_timestamp > self.timeout_request:
                    stale_keys.append(key)

        for key in stale_keys:
            del self.http_pair[key]
            logging.info(f"Удалён устаревший запрос без ответа для ключа: {key}")
