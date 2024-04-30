import logging
import os

import dotenv
from telegram import Update
from telegram.ext import Application

from handlers.handlers import register_handlers
from services import LlamaService
from services.database_service import DatabaseService

dotenv.load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


def main() -> None:
    application = Application.builder() \
        .token(os.environ["TELEGRAM_API_TOKEN"]) \
        .build()
    database_service = DatabaseService(os.environ["DB_FILE"])
    llama_service = LlamaService(os.environ["LLAMA_API_TOKEN"])
    logger.info("Created services")

    register_handlers(application, llama_service, database_service)
    logger.info("Registered handlers")

    logger.info("Start polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
