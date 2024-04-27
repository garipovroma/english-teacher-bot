# import pytest
# from unittest.mock import patch, Mock
# from services.llama_service import LlamaService
# from utils.prompts import EXERCISE_PROMPT, QUESTION_ANSWER_PROMPT, SUMMARIZATION_PROMPT

# @pytest.fixture
# def llama_service():
#     with patch('services.llama_service.LlamaAPI'):
#         return LlamaService("dummy_token")

# def test_generate_exercise(llama_service):
#     user_prompt = "Practice verb tenses with this exercise."
#     expected_prompt = f"{EXERCISE_PROMPT}\n\nUser Prompt: {user_prompt}"
#     expected_result = "Generated exercise text"

#     with patch('services.llama_service.ChatLlamaAPI') as mock_chat_model:
#         mock_chat_model.return_value = expected_result
#         result = llama_service.generate_exercise(user_prompt)

#     assert result == expected_result
#     mock_chat_model.assert_called_with(expected_prompt)
