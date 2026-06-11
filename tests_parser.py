import os
import re
from typing import Dict, List

CHOICE_LETTERS = ["A", "B", "C", "D", "E"]

def parse_test_text(text: str) -> List[Dict]:
    """Parse NotebookLM-style markdown test text into question dictionaries."""
    
    # 1. Metnin sonundaki tabloyu atıyoruz, böylece son sorunun içerisine sızmaz.
    text = re.split(r"##\s*ANSWER KEY SUMMARY", text, flags=re.IGNORECASE)[0]

    parts = re.split(r"###\s*Question\s+", text, flags=re.IGNORECASE)
    questions = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        lines = part.split("\n")
        if not lines:
            continue

        header_line = lines[0]
        m = re.match(r"(\d+)\s*(.*)", header_line)
        if not m:
            continue

        qnum = int(m.group(1))
        header = m.group(2).strip()
        rest = "\n".join(lines[1:])

        # 2. Kalın yıldız işaretlerini (\*?\*?) opsiyonel yaptık. (Eski formata uyumluluk için)
        correct = None
        m_corr = re.search(r"\*?\*?Correct Answer:\*?\*?\s*([A-E])", rest, flags=re.IGNORECASE)
        if m_corr:
            correct = m_corr.group(1).upper()

        docref = None
        m_ref = re.search(r"\*?\*?Document Reference:\*?\*?\s*([^\n]+)", rest, flags=re.IGNORECASE)
        if m_ref:
            docref = m_ref.group(1).strip()

        # 3. Rationale'in yeni gelen yatay çizgilerde durmasını sağlıyoruz: (?=\n[─━\-]{3,}|\Z)
        rationale = None
        m_rat = re.search(r"\*?\*?Rationale:\*?\*?\s*(.*?)(?=\n[─━\-]{3,}|\Z)", rest, flags=re.S | re.IGNORECASE)
        if m_rat:
            rationale = m_rat.group(1).strip()

        choices = {}
        for i, letter in enumerate(CHOICE_LETTERS):
            next_letters = "|".join(CHOICE_LETTERS[i + 1 :])
            if next_letters:
                pattern = rf"(?:^|\n){letter}\)\s*(.*?)(?=\n(?:{next_letters})\)|\n\*?\*?Correct Answer:\*?\*?|\Z)"
            else:
                pattern = rf"(?:^|\n){letter}\)\s*(.*?)(?=\n\*?\*?Correct Answer:\*?\*?|\Z)"
            m_choice = re.search(pattern, rest, flags=re.S | re.IGNORECASE)
            if m_choice:
                choices[letter] = " ".join(m_choice.group(1).strip().split())

        # İlk şıkkı bulup öncesini soru gövdesi (stem) olarak alıyoruz.
        m_first_choice = re.search(r"(?:^|\n)A\)", rest, flags=re.IGNORECASE)
        if m_first_choice:
            stem = rest[: m_first_choice.start()].strip()
        else:
            stem = rest.strip()

        if not stem or not choices:
            continue

        questions.append(
            {
                "number": qnum,
                "header": header,
                "stem": stem,
                "choices": choices,
                "correct": correct,
                "docref": docref,
                "rationale": rationale,
            }
        )

    return questions

def parse_test_file(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return parse_test_text(f.read())

def load_all_tests(tests_dir: str) -> Dict[str, List[Dict]]:
    data = {}

    if not os.path.isdir(tests_dir):
        return data

    for fname in sorted(os.listdir(tests_dir)):
        if fname.lower().endswith(".txt"):
            path = os.path.join(tests_dir, fname)
            try:
                data[fname] = parse_test_file(path)
            except Exception as e:
                data[fname] = [{"error": str(e)}]

    return data