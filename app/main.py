import logging
import os

import pyshark
from config import config
from modules.sniffer import Sniffer
from utils.filter import convert_to_decode_as, create_bpf_filter, rename_traffic_dump

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Начало захвата HTTP трафика на хосте...")

traffic_dump_file_path = config.TRAFFIC_DUMP_FILE_PATH
database_path = config.DATABASE_PATH
services = config.SERVICES


def main():
    os.makedirs(os.path.join('..', 'database'), exist_ok=True)
    os.makedirs(os.path.join('..', 'dump'), exist_ok=True)

    interface = config.INTERFACE
    bpf_filter = create_bpf_filter(services)
    decode_as = convert_to_decode_as(services)

    logging.info(f"Фильтр захвата трафика: {bpf_filter}")
    logging.info(f"Фильтр захвата трафика: {decode_as}")

    rename_traffic_dump(config.TRAFFIC_DUMP_FILE_PATH)

    capture = pyshark.LiveCapture(interface=interface,
                                  output_file=traffic_dump_file_path,
                                  bpf_filter=bpf_filter,
                                  decode_as=decode_as)
    sniffer = Sniffer(database_path=database_path)

    for packet in capture.sniff_continuously():
        sniffer.process_packet(packet)


if __name__ == '__main__':
    main()
