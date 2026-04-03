import logging

# Logging levels:
# CRITICAL = 50
# FATAL = CRITICAL
# ERROR = 40
# WARNING = 30
# WARN = WARNING
# INFO = 20
# DEBUG = 10
# NOTSET = 0


# Basic config
logging.basicConfig(
    level=logging.WARN,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

# Named logger (preferred)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) 


# Log to file
handler = logging.FileHandler("logs/app.log", mode="a")
handler.setLevel(logging.ERROR)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
logger.addHandler(handler)


logger.critical("This knows which module it came from")

x=1
# Using root logger
logging.debug("Variable x = %s", x)
logging.info("Server started")
logging.warning("Disk space low")
logging.error("Connection failed")
logging.critical("System crash")

logger.debug("Variable x = %s", x)
logger.info("Server started")
logger.warning("Disk space low")
logger.error("Connection failed")
logger.critical("System crash")





