import logging

class LogGen:
    
    @staticmethod
    def loggen(filename="wtlog.log", dev=False):
        '''
        basic logger function which will initilize logger
        '''
        format_str = None
        if dev:
            format_str = "%(levelname)s - %(asctime)s - %(filename)s - %(lineno)d - %(message)s"
        else:
            format_str = "%(levelname)s - %(asctime)s - %(message)s"
        
        logging.basicConfig(filename=filename,format=format_str,datefmt='%m/%d/%Y %I:%M:%S %p')

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        return logger
