import datetime
import re
from unittest import mock
from unittest.mock import patch

import pytest
from telegram import Update, Message, User, Chat, MessageEntity
from telegram.ext import Application

from handlers.handlers import register_handlers
from tests.comparators import AndPatternsComparator


@pytest.fixture
def database_service():
    yield mock.Mock()


@pytest.fixture
def llama_service():
    yield mock.Mock()


@pytest.fixture
def telegram_bot():
    telegram_bot = mock.AsyncMock()
    telegram_bot.username = "BotUsername"
    yield telegram_bot


@pytest.fixture
async def telegram_application(llama_service, database_service, telegram_bot):
    application = Application.builder().bot(telegram_bot).build()
    register_handlers(application, llama_service, database_service)
    application.updater = None

    await application.initialize()
    yield application


def assert_last_reply_message(telegram_bot, *, text=mock.ANY):
    telegram_bot.send_message.assert_called_with(
        chat_id=mock.ANY,
        text=text,
        parse_mode=mock.ANY,
        entities=mock.ANY,
        disable_notification=mock.ANY,
        protect_content=mock.ANY,
        reply_markup=mock.ANY,
        message_thread_id=mock.ANY,
        link_preview_options=mock.ANY,
        reply_parameters=mock.ANY,
        business_connection_id=mock.ANY,
        allow_sending_without_reply=mock.ANY,
        disable_web_page_preview=mock.ANY,
        read_timeout=mock.ANY,
        write_timeout=mock.ANY,
        connect_timeout=mock.ANY,
        pool_timeout=mock.ANY,
        api_kwargs=mock.ANY,
    )


def create_command_message(telegram_application, message_id, text):
    message = Message(
        message_id=message_id,
        date=datetime.datetime.utcnow(),
        chat=Chat(id=1, type="PRIVATE"),
        text=text,
        from_user=User(
            id=1,
            first_name="Tester",
            is_bot=False,
            username="Tester",
        ),
        entities=[
            MessageEntity(
                type=MessageEntity.BOT_COMMAND,
                offset=0,
                length=len(text),
            ),
        ],
    )
    message.set_bot(telegram_application.bot)
    return message


def create_text_message(telegram_application, message_id, text):
    message = Message(
        message_id=message_id,
        date=datetime.datetime.utcnow(),
        chat=Chat(id=1, type="PRIVATE"),
        text=text,
        from_user=User(
            id=1,
            first_name="Tester",
            is_bot=False,
            username="Tester",
        ),
    )
    message.set_bot(telegram_application.bot)
    return message


async def test_exercise_conversation(telegram_application, telegram_bot, llama_service):
    await telegram_application.process_update(
        Update(
            update_id=1,
            message=create_command_message(telegram_application, message_id=1, text="/start_exercise"),
        )
    )

    assert_last_reply_message(
        telegram_bot,
        text="Hi! Please type your prompt for the exercise. Type /cancel to cancel this exercise",
    )
    assert len(telegram_bot.send_message.mock_calls) == 1

    llama_message = "llama message"
    llama_service.generate_exercise = mock.Mock(return_value=llama_message)
    user_message = "hello"
    await telegram_application.process_update(
        Update(
            update_id=2,
            message=create_text_message(telegram_application, message_id=2, text=user_message),
        )
    )

    assert_last_reply_message(
        telegram_bot,
        text=llama_message,
    )
    assert len(telegram_bot.send_message.mock_calls) == 3

    llama_service.generate_exercise.assert_called_once_with(user_message)

    await telegram_application.process_update(
        Update(
            update_id=3,
            message=create_text_message(telegram_application, message_id=3, text="hello"),
        )
    )
    assert len(telegram_bot.send_message.mock_calls) == 4
    assert len(llama_service.generate_exercise.mock_calls) == 1


@patch("handlers.handlers.DEVELOPER_CHAT_ID", "111")
@patch("handlers.handlers.DEVELOPER_MENTIONS", "@mention")
async def test_error_handler(telegram_application, telegram_bot):
    send_message_calls = 0

    def send_message_side_effect(*args, **kwargs):
        nonlocal send_message_calls
        send_message_calls += 1
        if send_message_calls <= 1:
            raise ValueError("Could not send data :u")

    telegram_bot.send_message = mock.AsyncMock(side_effect=send_message_side_effect)

    await telegram_application.process_update(
        Update(
            update_id=1,
            message=create_text_message(telegram_application, message_id=1, text="Some text"),
        )
    )

    assert len(telegram_bot.send_message.mock_calls) == 3
    telegram_bot.send_message.assert_any_call(
        chat_id='111',
        text=AndPatternsComparator(
            re.compile("@mention"),
            re.compile(r"ValueError: Could not send data :u"),
        ),
        parse_mode=mock.ANY,
    )
