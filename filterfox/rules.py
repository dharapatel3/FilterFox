from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import re


@dataclass(frozen=True)
class Classification:
    category: str
    reason: str


def _get_header(msg: Dict[str, Any], name: str) -> str:
    headers = (msg.get("payload", {}) or {}).get("headers", []) or []
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "") or ""
    return ""


def classify_message(msg: Dict[str, Any]) -> Optional[Classification]:
    subject = _get_header(msg, "Subject")
    from_ = _get_header(msg, "From")
    list_unsub = _get_header(msg, "List-Unsubscribe")
    precedence = _get_header(msg, "Precedence")

    subject_l = subject.lower()
    from_l = from_.lower()

    if list_unsub:
        return Classification("Newsletters", "Has List-Unsubscribe header")
    if "bulk" in (precedence or "").lower():
        return Classification("Newsletters", "Precedence: bulk")

    promo_patterns = [
        r"\bdeal\b", r"\bsale\b", r"\boffer\b", r"\bpromo\b",
        r"\bdiscount\b", r"\bclearance\b", r"\b% off\b", r"\bfree shipping\b"
    ]
    if any(re.search(p, subject_l) for p in promo_patterns):
        return Classification("Promotions", "Promo keywords in subject")

    receipt_patterns = [
        r"\breceipt\b", r"\binvoice\b", r"\border\b", r"\bpayment\b",
        r"\bshipped\b", r"\bdelivered\b", r"\btracking\b", r"\bconfirmation\b"
    ]
    if any(re.search(p, subject_l) for p in receipt_patterns):
        return Classification("Receipts", "Receipt/order keywords in subject")

    social_senders = ["linkedin", "facebook", "instagram", "x.com", "twitter", "reddit", "discord", "github"]
    if any(s in from_l for s in social_senders):
        return Classification("Social", "Sender matches social/platform list")

    return None