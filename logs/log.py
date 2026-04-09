import logging

class CustomLogger:
    _configured = False
    def __init__(self):
        if not CustomLogger._configured:
            logging.basicConfig(
                encoding='utf-8',
                level=logging.INFO,
                format='%(asctime)s | %(levelname)s | %(message)s',
                handlers=[
                    logging.FileHandler('app.log'),
                    logging.StreamHandler()
                ]
                )
            CustomLogger._configured=True
            
    def get_logger(self, name=__name__):
        return logging.getLogger(name) 