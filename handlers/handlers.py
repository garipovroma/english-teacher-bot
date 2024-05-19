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

DEVELOPER_CHAT_ID = os.getenv("DEVELOPER_CHAT_ID")
DEVELOPER_MENTIONS = os.getenv("DEVELOPER_MENTIONS", "")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log_data = {}
    if isinstance(update, Update):
        log_data['chat.id'] = update.effective_chat.id
        log_data['user.name'] = update.effective_user.name

    logger.error(f"Exception during processing user request, log_data={log_data}",
                 exc_info=context.error)

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

    if DEVELOPER_CHAT_ID is not None:
        await context.bot.send_message(
            chat_id=DEVELOPER_CHAT_ID,
            text=message,
            parse_mode=ParseMode.HTML,
        )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f"Received /start command from {user.name}, chat.id = {chat.id}")
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Type /help to see what this bot can do!",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f"Received /help command from {user.name}, chat.id = {chat.id}")

    help_message = (
        "You can train your english language skills using these commands\n"
        "/help - show this message\n"
        "/theory - get theory information about a topic.\n"
        "/start_exercise - start an English exercise based on a topic.\n"
    )
    await update.message.reply_text(help_message)


class TheoryState:
    TOPIC_SELECTION = 1


def create_theory_command(database_service: DatabaseService):
    async def theory_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        chat = update.effective_chat
        logger.info(f"Received /theory command from {user.name}, chat.id = {chat.id}")

        topics = database_service.get_all_topics()

        data = ""
        for topic in topics:
            data += f"{topic[0]} - {topic[1]}\n"

        await update.message.reply_text(f"Please select a topic by entering its ID:\n\n{data}")

        return TheoryState.TOPIC_SELECTION

    return theory_command


def create_topic_selection(database_service: DatabaseService):
    async def topic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        topic_id = update.effective_message.text

        user = update.effective_user
        chat = update.effective_chat
        logger.info(f"User {user.name} selected topic {topic_id}, chat.id = {chat.id}")

        if topic_id.isdigit():
            card = database_service.get_theory_card_by_topic_id(int(topic_id))
            if card:
                await update.message.reply_text(card[0])
            else:
                await update.message.reply_text("No card found for the selected topic.")

            return ConversationHandler.END
        else:
            await update.message.reply_text("Wrong input. Try again.")
            return TheoryState.TOPIC_SELECTION

    return topic_selection


class ExerciseState:
    TOPIC_SELECTION = 1
    EXERCISE = 2


class ExerciseDataKey:
    SELECTED_TOPIC = "SELECTED_TOPIC"
    GENERATED_EXERCISE = "GENERATED_EXERCISE"


def create_start_exercise_command(database_service: DatabaseService):
    async def start_exercise_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        chat = update.effective_chat
        logger.info(f"Received /start_exercise command from {user.name}, chat.id = {chat.id}")

        context.chat_data[ExerciseDataKey.SELECTED_TOPIC] = None
        context.chat_data[ExerciseDataKey.GENERATED_EXERCISE] = None

        topics = database_service.get_all_topics()
        await update.message.reply_text("Hi! Please choose a topic for the exercise by entering its ID. "
                                        "Type /cancel to cancel this exercise.")

        data = ""
        for topic in topics:
            data += f"{topic[0]} - {topic[1]}\n"

        await update.message.reply_text(f"{data}")

        return ExerciseState.TOPIC_SELECTION

    return start_exercise_command


async def reply_with_exercise(update: Update, context: ContextTypes.DEFAULT_TYPE, llama_service: LlamaService, topic):
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f"Replying with exercise to {user.name}, topic id = {topic[0]}, chat.id = {chat.id}")

    await update.message.reply_text("Generating exercise...\n"
                                    "Tip: type /cancel to cancel this exercise")
    generated_exercise = llama_service.generate_exercise(topic)
    context.chat_data[ExerciseDataKey.GENERATED_EXERCISE] = generated_exercise

    await update.message.reply_text(generated_exercise)


def create_exercise_topic_selection(database_service: DatabaseService, llama_service: LlamaService):
    async def topic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        topic_id = update.effective_message.text

        user = update.effective_user
        chat = update.effective_chat
        logger.info(f"User {user.name} selected exercise topic {topic_id}, chat.id = {chat.id}")

        if topic_id.isdigit():
            topic = database_service.get_topic_by_id(int(topic_id))
            if not topic:
                await update.message.reply_text(f"Topic {topic_id} does not exist. Try again.")
                return ExerciseState.TOPIC_SELECTION

            context.chat_data[ExerciseDataKey.SELECTED_TOPIC] = int(topic_id)
            await reply_with_exercise(update, context, llama_service, topic)
            return ExerciseState.EXERCISE
        else:
            await update.message.reply_text("Wrong input. Try again.")
            return ExerciseState.TOPIC_SELECTION

    return topic_selection


def create_exercise_assessor(database_service: DatabaseService, llama_service: LlamaService):
    async def exercise_assessor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        user = update.effective_user
        chat = update.effective_chat
        logger.info(f"Received exercise solution text from {user.name}, chat.id = {chat.id}")

        await update.message.reply_text("Assessing answer...")

        topic_id = context.chat_data[ExerciseDataKey.SELECTED_TOPIC]
        topic = database_service.get_topic_by_id(int(topic_id))
        generated_exercise = context.chat_data[ExerciseDataKey.GENERATED_EXERCISE]
        user_answer = update.effective_message.text

        answer_assessment = llama_service.assess_exercise_answer(topic, generated_exercise, user_answer)
        await update.message.reply_text(answer_assessment)

        await reply_with_exercise(update, context, llama_service, topic)
        return ExerciseState.EXERCISE

    return exercise_assessor


async def cancel_exercise_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f"Received /cancel command from {user.name}, chat.id = {chat.id}")

    await update.message.reply_text("Thank you for using our English Teacher Bot! Hope to see you back soon!")

    return ConversationHandler.END


def register_handlers(application: Application, llama_service: LlamaService, database_service: DatabaseService):
    exercise_handler = ConversationHandler(
        per_chat=True,
        per_user=False,
        entry_points=[CommandHandler("start_exercise", create_start_exercise_command(database_service))],
        states={
            ExerciseState.TOPIC_SELECTION: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    create_exercise_topic_selection(database_service, llama_service),
                ),
            ],
            ExerciseState.EXERCISE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    create_exercise_assessor(database_service, llama_service),
                ),
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
            TheoryState.TOPIC_SELECTION: [
                MessageHandler(filters.TEXT & ~filters.Command(), create_topic_selection(database_service)),
            ]
        },
        fallbacks=[],
    ))

    application.add_error_handler(error_handler)
