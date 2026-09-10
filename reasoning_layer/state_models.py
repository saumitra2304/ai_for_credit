from types import SimpleNamespace


def chat_memory(*, user_id, chat_id, sme_data, message_trail, company_cache=None):
    return SimpleNamespace(
        user_id=user_id,
        chat_id=str(chat_id),
        sme_data=sme_data if isinstance(sme_data, dict) else {},
        message_trail=list(message_trail or []),
        company_cache=company_cache if isinstance(company_cache, dict) else {},
    )
