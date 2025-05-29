from src.processing.task_executor import run_gpt_fallback

test_description = "Please notify HR that John Doe has accepted the offer and will start on July 10."
result = run_gpt_fallback(test_description, is_real=False)
print(f"[TEST RESULT] {result}")
