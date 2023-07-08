import sys
from vnpd.exception import CustomException
from vnpd.logger import logging

def test():
    try:
        logging.info('Testing the model')
        a = 1/0
    except Exception as e:
        raise CustomException(e,sys)
    
if __name__=="__main__":
    try:
        test()
    except Exception as e:
        print(e)