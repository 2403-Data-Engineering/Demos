import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # let everything through to handlers

handler = logging.FileHandler("test.log")
handler.setLevel(logging.ERROR)  # handler filters to ERROR+
logger.addHandler(handler)

logger.error("This should appear in test.log")