import html
import logging
import os
import traceback

import dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, Application, ConversationHandler

from services import LlamaService
from services.database_service import DatabaseService

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

DEVELOPER_CHAT_ID = int(os.environ["DEVELOPER_CHAT_ID"])
DEVELOPER_MENTIONS = os.getenv("DEVELOPER_MENTIONS", "")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception during processing user request", exc_info=context.error)

    traceback_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    traceback_string = "".join(traceback_list)

    username = update.effective_user.username if isinstance(update, Update) else None
    message = (
        f"{DEVELOPER_MENTIONS}\n"
        "Unexpected error occurred during request processing\n"
        f"<pre>update.effective_user.username = {html.escape(str(username))}</pre>\n\n"
        f"<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n"
        f"<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n"
        f"<pre>{html.escape(traceback_string)}</pre>"
    )

    if isinstance(update, Update):
        await update.message.reply_text(
            "Unexpected error occurred during request processing. Please, try again later.",
        )

    await context.bot.send_message(
        chat_id=DEVELOPER_CHAT_ID,
        text=message,
        parse_mode=ParseMode.HTML,
    )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f"Received /start command from {user.name}")
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Type /help to see what this bot can do!",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f"Received /help command from {user.name}")

    help_message = (
        "You can train your english language skills using these commands\n"
        "/help - show this message\n"
        "/question <prompt> - generate a response to the given question.\n"
        "/summarize <prompt> - summarize the given text.\n"
        "/theory - get rheory information about some topic.\n"
        "/start_exercise - start an English exercise based on a prompt.\n"
    )
    await update.message.reply_text(help_message)


def create_question_command(llama_service: LlamaService):
    async def question_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        logger.info(f"Received /question command from {user.name}")

        await update.message.reply_text("Working...")
        user_prompt = ' '.join(context.args)
        generated_exercise = llama_service.answer_question(user_prompt)
        await update.message.reply_text(generated_exercise)

    return question_command


def create_summarize_command(llama_service: LlamaService):
    async def summarize_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        logger.info(f"Received /summarize command from {user.name}")

        await update.message.reply_text("Working...")
        user_prompt = ' '.join(context.args)
        generated_exercise = llama_service.summarize_text(user_prompt)
        await update.message.reply_text(generated_exercise)

    return summarize_command


class ExerciseState:
    IN_PROGRESS = 1
    TOPIC_SELECTION = 2

def create_theory_command(database_service: DatabaseService):
    async def theory_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.effective_user
        logger.info(f"Received /theory command from {user.name}")

        topics = database_service.get_all_topics()

        data = ""
        for topic in topics:
            data += f"{topic[0]} - {topic[1]}\n"

        await update.message.reply_text(f"Please select a topic by entering its ID:\n\n{data}")

        return ExerciseState.TOPIC_SELECTION

    return theory_command

def create_topic_selection(database_service: DatabaseService):
    async def topic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        topic_id = update.message.text

        user = update.effective_user
        logger.info(f"User {user.name} selected topic {topic_id}")

        if topic_id.isdigit():
            card = database_service.get_theory_card_by_topic_id(int(topic_id))
            if card:
                await update.message.reply_text(card[0])
            else:
                await update.message.reply_text("No card found for the selected topic.")
            
            return ConversationHandler.END
        else:
            await update.message.reply_text("Wrong input. Try again.")
            return ExerciseState.TOPIC_SELECTION

    return topic_selection

async def start_exercise_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info(f"Received /start_exercise command from {user.name}")

    await update.message.reply_text("Hi! Please type your prompt for the exercise. "
                                    "Type /cancel to cancel this exercise")
    return ExerciseState.IN_PROGRESS


async def cancel_exercise_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info(f"Received /cancel_exercise command from {user.name}")

    await update.message.reply_text("Thank you for using our English Teacher Bot! Hope to see you back soon!")

    return ConversationHandler.END


def create_exercise_replier(llama_service: LlamaService):
    async def exercise_replier(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        logger.info(f"Received exercise conversation text from {user.name}")

        await update.message.reply_text("Working...")
        generated_exercise = llama_service.generate_exercise(update.effective_message.text)
        await update.message.reply_text(generated_exercise)
        return ConversationHandler.END

    return exercise_replier

def register_handlers(application: Application, llama_service: LlamaService, database_service: DatabaseService):
    exercise_handler = ConversationHandler(
        entry_points=[CommandHandler("start_exercise", start_exercise_command)],
        states={
            ExerciseState.IN_PROGRESS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_exercise_replier(llama_service)),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_exercise_command)],
    )
    application.add_handler(exercise_handler)

    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CommandHandler("start", start_command))

    application.add_handler(ConversationHandler(
         entry_points=[CommandHandler("theory", create_theory_command(database_service))],
         states={
            ExerciseState.TOPIC_SELECTION: [MessageHandler(filters.TEXT & ~filters.Command(), create_topic_selection((database_service)))]
        },
        fallbacks=[],
    ))

    application.add_handler(CommandHandler("question", create_question_command(llama_service)))
    application.add_handler(CommandHandler("summarize", create_summarize_command(llama_service)))
    application.add_error_handler(error_handler)
