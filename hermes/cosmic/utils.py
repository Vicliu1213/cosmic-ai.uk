import logging

def setup_logging(level="INFO", log_file=None):
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        filename=log_file
    )
