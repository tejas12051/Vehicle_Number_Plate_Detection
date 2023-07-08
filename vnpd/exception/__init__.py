import os
import sys

class CustomException(Exception):
    def __init__(self,error_message:Exception, error_detail:sys):
        super().__init__(error_message)
        self.error_message = CustomException.prepare_error_message(error_message,error_detail)

    @staticmethod
    def prepare_error_message(error_message:Exception, error_detail:sys)->str:
        _,_,exc_tb = error_detail.exc_info()
        filename = exc_tb.tb_frame.f_code.co_filename
        line_no = exc_tb.tb_lineno

        error_message = f"Error occured script name [{filename}] at line number [{line_no}] and error message is [{error_message}]"
        return error_message

    def __repr__(self):
        return self.error_message

    def __str__(self):
        return self.error_message