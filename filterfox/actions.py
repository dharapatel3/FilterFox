from __future__ import annotations
from dataclasses import dataclass

INBOX = "INBOX"
TRASH = "TRASH"


@dataclass
class ActionPlan:
    label_name: str
    archive: bool = True
    trash: bool = False  # off in Path A


def plan_for_category(category: str, label_prefix: str) -> ActionPlan:
    label_name = f"{label_prefix}/{category}"

    if category == "Receipts":
        # receipts: label but keep in inbox
        return ActionPlan(label_name=label_name, archive=False, trash=False)

    if category in {"Newsletters", "Promotions", "Social"}:
        return ActionPlan(label_name=label_name, archive=True, trash=False)

    return ActionPlan(label_name=label_name, archive=False, trash=False)


def summarize_message(msg) -> str:
    headers = (msg.get("payload", {}) or {}).get("headers", []) or []

    def get(name: str) -> str:
        for h in headers:
            if h.get("name", "").lower() == name.lower():
                return (h.get("value") or "").strip()
        return ""

    return f'From="{get("From")}" Subject="{get("Subject")}"'