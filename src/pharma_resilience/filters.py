import re
import unicodedata
from difflib import SequenceMatcher

PARENTERAL_PATTERNS = (
    r"ENJEK|INFUZ|(?<![A-Z0-9])I\.?V\.?(?![A-Z0-9])|LIYOF|FLAKON|AMPUL"
)

TARGET_ACTIVE_ROOTS = ("omepraz", "pantopr", "esomepraz")


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    s = str(value).strip().casefold()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", s)


def normalize_registry_token(value: object) -> str:
    s = normalize_text(value).upper()
    return (
        s.replace("İ", "I")
         .replace("Ş", "S")
         .replace("Ğ", "G")
         .replace("Ü", "U")
         .replace("Ö", "O")
         .replace("Ç", "C")
    )


def is_parenteral_name(product_name: object) -> bool:
    s = normalize_registry_token(product_name)
    return bool(re.search(PARENTERAL_PATTERNS, s))


def fuzzy_active_ingredient_review(
    ingredient: object,
    roots=TARGET_ACTIVE_ROOTS,
    similarity_threshold: float = 0.78,
):
    """
    Returns manual-review candidates.
    This function never silently accepts fuzzy matches.
    """
    s = normalize_text(ingredient)
    compact = re.sub(r"[^a-z0-9]+", "", s)
    out = []
    for root in roots:
        if root in compact:
            out.append({"root": root, "reason": "root_match", "score": 1.0})
            continue
        score = SequenceMatcher(None, compact[: max(len(root) + 5, len(compact))], root).ratio()
        if score >= similarity_threshold:
            out.append({"root": root, "reason": "fuzzy_review", "score": score})
    return out
