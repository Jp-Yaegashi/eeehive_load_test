import logging

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,
    filename='debug.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s'
)