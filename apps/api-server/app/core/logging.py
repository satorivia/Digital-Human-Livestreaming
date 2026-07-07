import logging, json

def configure_logging(level: str='INFO') -> None:
    logging.basicConfig(level=level, format='%(message)s')

def log_json(**fields):
    logging.getLogger('digital_human').info(json.dumps(fields, ensure_ascii=False))
