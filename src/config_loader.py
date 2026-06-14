import os
import yaml
from pathlib import Path


def load_config(config_path: str = "config.yaml") -> dict:
    base_dir = Path(__file__).resolve().parent.parent
    full_path = base_dir / config_path
    with open(full_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_output_dir(config: dict) -> Path:
    base_dir = Path(__file__).resolve().parent.parent
    report_dir = base_dir / config["output"]["report_dir"]
    report_dir.mkdir(parents=True, exist_ok=True)
    return report_dir


def flatten_keywords(config: dict) -> list:
    all_kw = []
    for cat, kws in config["keywords"].items():
        all_kw.extend(kws)
    return list(set(all_kw))


def match_keywords(text: str, keywords: list) -> list:
    if not text:
        return []
    text_lower = text.lower()
    matched = []
    for kw in keywords:
        if kw.lower() in text_lower:
            matched.append(kw)
    return matched
