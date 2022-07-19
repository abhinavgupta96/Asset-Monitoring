import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        log_record['@timestamp'] = now
        del log_record['timestamp']
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

def custom_logging(log_level):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    log_handler = logging.StreamHandler()
    formatter = CustomJsonFormatter('%(timestamp) %(level) %(name) %(message)')
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)