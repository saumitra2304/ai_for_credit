from state_models import chat_memory
from sql_db.chat_store import persistable_chat


def test_persistable_chat_drops_probe_blobs():
    chat = chat_memory(
        user_id=1,
        chat_id="c1",
        sme_data={"U123": {"data": {"financials": [1, 2, 3]}}},
        message_trail=[{"query": "q", "response": "r"}],
        company_cache={"U123": {"label": "Acme", "flat": "METRIC | 2024"}},
    )
    stored = persistable_chat(chat)
    assert stored.sme_data == {}
    assert stored.company_cache["U123"]["flat"] == "METRIC | 2024"
    assert chat.sme_data["U123"]["data"]["financials"] == [1, 2, 3]


def test_cins_needing_fetch_skips_cached_flats():
    from sql_db.chat_store import cins_needing_fetch

    chat = chat_memory(
        user_id=1,
        chat_id="c1",
        sme_data={},
        message_trail=[{"query": "q", "response": "r"}],
        company_cache={"U123": {"label": "Acme", "flat": "tables"}},
    )
    assert cins_needing_fetch(chat, ["U123", "U999"]) == ["U999"]
