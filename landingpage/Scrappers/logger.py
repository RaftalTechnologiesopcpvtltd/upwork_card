import os
import logging



def setup_logger(scraper_name):
    """Create a separate logger for each scraper."""
    log_filename = os.path.join("Scrapper loggers", f"{scraper_name}.log")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)

    # Create logger
    logger = logging.getLogger(scraper_name)
    logger.setLevel(logging.INFO)

    # Create file handler
    file_handler = logging.FileHandler(log_filename, mode="a+")
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    # Add handler to logger
    logger.addHandler(file_handler)

    return logger