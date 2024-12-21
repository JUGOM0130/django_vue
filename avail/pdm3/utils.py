import logging
from .models import Prefix, CodeCounter, CodeVersion, CodeVersionHistory

def get_logger(name):
    """
    ロガーを生成し、返す
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(levelname)s %(asctime)s %(module)s %(message)s')
    console_handler.setFormatter(formatter)
    
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger

logger = get_logger(__name__)

from .models import CodeCounter, Prefix

def generate_code(prefix: Prefix) -> str:
    code_counter, _ = CodeCounter.objects.get_or_create(prefix=prefix)
    current_number = code_counter.current_number + 1
    code_counter.current_number = current_number
    code_counter.save()

    if prefix.code_type == '1':  # 組
        code = f"{prefix.name}-A{current_number:04d}Z0000"
    elif prefix.code_type == '2':  # 部品
        code = f"{prefix.name}-AA{current_number:04d}Z0000"
    elif prefix.code_type == '3':  # 購入品
        code = f"{prefix.name}-A{current_number:04d}Z0000"
    else:
        raise ValueError('Unexpected code type.')

    return code