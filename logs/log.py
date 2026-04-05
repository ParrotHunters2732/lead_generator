import logging

class CustomLogger:
    def __init__(self):
        logging.basicConfig(
            encoding='utf-8',
            level=logging.INFO,
            format='%(asctime)s | %(levelname)s | %(message)s',
            handlers=[
                logging.FileHandler('app.log'),
                logging.StreamHandler()
            ]
            )
    def get_logger(self, name=__name__):
        return logging.getLogger(name) 