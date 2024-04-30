import logging

from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, Application, ConversationHandler

from services import LlamaService
from services.database_service import DatabaseService

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f"Received /start command from {user.name}")
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Type /help to see what this bot can do!",
    )


HELP_MESSAGE = """
You can train your english language skills using these commands:
/help - show this message
/question <prompt> - generate a response to the given question.
/summarize <prompt> - summarize the given text.
/start_exercise - start an English exercise based on a prompt.
"""


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    logger.info(f"Received /help command from {user.name}")
    await update.message.reply_text(HELP_MESSAGE)


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

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, help_command))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CommandHandler("start", start_command))

    application.add_handler(CommandHandler("question", create_question_command(llama_service)))
    application.add_handler(CommandHandler("summarize", create_summarize_command(llama_service)))
