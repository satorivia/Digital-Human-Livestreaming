from pathlib import Path

PROMPT_DIR = Path("packages/prompt-templates")


def test_product_answer_prompt_forbids_made_up_price_and_inventory() -> None:
    prompt = (PROMPT_DIR / "product_answer_v1.md").read_text(encoding="utf-8")

    assert "不得编造价格、库存" in prompt
    assert "{{ structured_facts }}" in prompt
    assert "{{ retrieved_chunks }}" in prompt
    assert "{{ comment }}" in prompt


def test_comment_classify_prompt_declares_required_variables() -> None:
    prompt = (PROMPT_DIR / "comment_classify_v1.md").read_text(encoding="utf-8")

    assert "{{ comment }}" in prompt
    assert "{{ product_title }}" in prompt
