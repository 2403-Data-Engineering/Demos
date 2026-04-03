# pip install loguru

from loguru import logger
# https://loguru.readthedocs.io/en/stable/api/logger.html#levels
# Logging Levels:
#   TRACE    =  5  — logger.trace()
#   DEBUG    = 10  — logger.debug()
#   INFO     = 20  — logger.info()
#   SUCCESS  = 25  — logger.success()
#   WARNING  = 30  — logger.warning()
#   ERROR    = 40  — logger.error()
#   CRITICAL = 50  — logger.critical()



# Works immediately — no config needed
logger.debug("Debug message")
logger.info("Server started on port 8080")
logger.warning("Disk space low")
logger.error("Connection failed")
logger.success("Pipeline complete")  # loguru-specific level

# Log to file with rotation and retention
logger.add("logs/loguru.log", rotation="500 MB", retention="10 days")
logger.add("logs/loguru-errors.log", level="ERROR", rotation="1 week")

# Structured context with bind
user_logger = logger.bind(user="Alice")
user_logger.info("Logged in")  # includes user="Alice" in the record

# Exception catching with full traceback
@logger.catch
def risky_function():
    return 1 / 0

risky_function()  # logs full traceback, doesn't crash

# Format with f-string style
name = "Alice"
logger.info("Processing user: {}", name)