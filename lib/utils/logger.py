import logging

def logger_init(filename, dev=False):
    
    format_str = None
    if dev:
        format_str = "%(levelname)s - %(asctime)s - %(filename)s - %(lineno)d - %(message)s"
    else:
        format_str = "%(levelname)s - %(asctime)s - %(message)s"
    
    logging.basicConfig(
        filename=filename,
        level=logging.INFO,
        format=format_str,
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(format_str)
    console.setFormatter(formatter)
    logging.getLogger("").addHandler(console)
    # marker to denote new log starting
    logging.info("------------------new---------------------")
