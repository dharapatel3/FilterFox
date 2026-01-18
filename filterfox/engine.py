from __future__ import annotations
from typing import Dict, Any, List

from .config import FilterFoxConfig
from .gmail_client import GmailClient
from .rules import classify_message
from .actions import plan_for_category, summarize_message, INBOX


def run_filterfox(cfg: FilterFoxConfig) -> Dict[str, Any]:
    client = GmailClient(cfg.credentials_path, cfg.token_path)
    msg_ids = client.list_message_ids(query=cfg.gmail_query, max_results=cfg.max_results)

    label_id_cache: Dict[str, str] = {}
    results: List[Dict[str, Any]] = []

    applied = 0
    skipped = 0

    for mid in msg_ids:
        msg = client.get_message_metadata(mid)
        cls = classify_message(msg)
        if not cls:
            skipped += 1
            continue

        plan = plan_for_category(cls.category, cfg.label_prefix)

        if plan.label_name not in label_id_cache:
            label_id_cache[plan.label_name] = client.ensure_label(plan.label_name)

        add_ids = [label_id_cache[plan.label_name]]
        remove_ids = [INBOX] if plan.archive else []

        results.append({
            "message_id": mid,
            "category": cls.category,
            "reason": cls.reason,
            "summary": summarize_message(msg),
            "action": {
                "label": plan.label_name,
                "archive": plan.archive
            }
        })

        if not cfg.dry_run:
            client.modify_message(mid, add_label_ids=add_ids, remove_label_ids=remove_ids)
            applied += 1

    return {
        "found": len(msg_ids),
        "classified": len(results),
        "skipped": skipped,
        "applied": applied,
        "results": results,
    }
