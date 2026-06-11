from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st

from tests_parser import load_all_tests, parse_test_text


TESTS_DIR = Path("tests")
CHOICE_LETTERS = ["A", "B", "C", "D", "E"]


st.set_page_config(
    page_title="Test Çözme Arayüzü",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
:root {
    --bg: #EEF3F8;
    --card: #FFFFFF;
    --primary: #2563EB;
    --primary-dark: #1E40AF;
    --accent: #14B8A6;
    --text: #1E293B;
    --muted: #64748B;
    --border: #CBD5E1;
    --soft: #F8FAFC;
    --success: #15803D;
    --danger: #B45309;
}

.stApp {
    background: var(--bg);
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

.quiz-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 22px;
    padding: 1.4rem 1.6rem;
    box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
}

.question-box {
    background: var(--soft);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1rem 1.1rem;
    color: var(--text);
    font-size: 1.04rem;
    line-height: 1.65;
    white-space: pre-wrap;
}

.meta-pill {
    display: inline-block;
    background: #E0F2FE;
    color: var(--primary-dark);
    border: 1px solid #BFDBFE;
    padding: 0.25rem 0.65rem;
    border-radius: 999px;
    font-size: 0.86rem;
    font-weight: 700;
    margin-bottom: 0.8rem;
}

/* YENİ EKLENEN ROZET STİLİ */
.tag-pill {
    display: inline-block;
    background: #F1F5F9;
    color: #475569;
    border: 1px solid #E2E8F0;
    padding: 0.25rem 0.6rem;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 600;
    margin-right: 0.5rem;
    margin-bottom: 0.6rem;
}

.small-muted {
    color: var(--muted);
    font-size: 0.92rem;
}

.correct-box {
    border-left: 5px solid var(--success);
    background: #ECFDF5;
    border-radius: 12px;
    padding: 0.9rem 1rem;
}

.wrong-box {
    border-left: 5px solid var(--danger);
    background: #FFF7ED;
    border-radius: 12px;
    padding: 0.9rem 1rem;
}

.reveal-box {
    border-left: 5px solid var(--primary);
    background: #EFF6FF;
    border-radius: 12px;
    padding: 0.9rem 1rem;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def load_tests_from_uploads(uploaded_files) -> Dict[str, List[dict]]:
    parsed: Dict[str, List[dict]] = {}
    for file in uploaded_files or []:
        try:
            text = file.getvalue().decode("utf-8")
            parsed[file.name] = parse_test_text(text)
        except UnicodeDecodeError:
            parsed[file.name] = [{"error": "Dosya UTF-8 olarak okunamadı."}]
        except Exception as exc:
            parsed[file.name] = [{"error": str(exc)}]
    return parsed


@st.cache_data(show_spinner=False)
def load_local_tests() -> Dict[str, List[dict]]:
    return load_all_tests(str(TESTS_DIR))


def init_state() -> None:
    defaults = {
        "current_test_name": "",
        "current_index": 0,
        "answers": {},
        "feedback_mode": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_question_state() -> None:
    st.session_state.feedback_mode = None


def set_test(name: str) -> None:
    if st.session_state.current_test_name != name:
        st.session_state.current_test_name = name
        st.session_state.current_index = 0
        reset_question_state()


def go_previous(total: int) -> None:
    if total <= 0:
        return
    st.session_state.current_index = (st.session_state.current_index - 1) % total
    reset_question_state()


def go_next(total: int) -> None:
    if total <= 0:
        return
    st.session_state.current_index = (st.session_state.current_index + 1) % total
    reset_question_state()


def score_for_test(test_name: str, questions: List[dict]) -> int:
    answers = st.session_state.answers.get(test_name, {})
    return sum(
        1
        for idx, question in enumerate(questions)
        if answers.get(idx) and answers.get(idx) == question.get("correct")
    )


def current_answer_key(test_name: str, index: int) -> str:
    return f"answer::{test_name}::{index}"


def store_answer(test_name: str, index: int, answer: Optional[str]) -> None:
    st.session_state.answers.setdefault(test_name, {})[index] = answer


def get_stored_answer(test_name: str, index: int) -> Optional[str]:
    return st.session_state.answers.get(test_name, {}).get(index)


def render_feedback(question: dict, selected: Optional[str]) -> None:
    mode = st.session_state.feedback_mode
    if not mode:
        return

    correct = question.get("correct") or "-"
    docref = question.get("docref") or ""
    rationale = question.get("rationale") or ""

    if mode == "correct":
        css_class = "correct-box"
        title = "✅ Doğru!"
    elif mode == "wrong":
        css_class = "wrong-box"
        title = f"❌ Yanlış. Doğru cevap: {correct}"
    else:
        css_class = "reveal-box"
        title = f"ℹ️ Doğru cevap: {correct}"

    body_parts = [f"<strong>{title}</strong>"]
    if selected and mode in {"correct", "wrong"}:
        body_parts.append(f"<p><strong>Senin cevabın:</strong> {selected}</p>")
    if docref:
        body_parts.append(f"<p style='margin-top: 8px;'><strong>Belge:</strong> {docref}</p>")
    if rationale:
        body_parts.append(f"<p><strong>Açıklama:</strong> {rationale}</p>")

    st.markdown(
        f"<div class='{css_class}'>" + "".join(body_parts) + "</div>",
        unsafe_allow_html=True,
    )


def render_empty_state() -> None:
    st.info(
        "Henüz soru bulunamadı. `tests` klasörüne `.txt` test dosyaları koyabilir "
        "veya sol menüden dosya yükleyebilirsin."
    )


def main() -> None:
    init_state()

    st.title("📝 Test Çözme Arayüzü")
    st.markdown(
        """
        <small>
        Bu arayüz yalnızca özel bir prompt ile NotebookLM’den üretilmiş test formatlarıyla çalışır.
        Kaynaklarınızı NotebookLM’e yükledikten sonra promptu chat kısmında kullanın.
        NotebookLM’in verdiği cevabı <code>.txt</code> olarak kaydedip bu arayüze yükleyerek çözebilirsiniz.
        </small>
        """,
        unsafe_allow_html=True 
    )
    st.link_button("Prompt için tıklayın!", "https://docs.google.com/document/d/1mdE6tZsboI-qEATvKEXzD_JNTWwMu4Qq9p3M9kNphFU/edit?usp=sharing")

    local_tests = load_local_tests()

    with st.sidebar:
        st.header("Test Dosyaları")
        uploaded_files = st.file_uploader(
            "TXT test dosyası yükle",
            type=["txt"],
            accept_multiple_files=True,
            help="Dosya yüklemezsen uygulama yerel `tests` klasörünü kullanır.",
        )

        uploaded_tests = load_tests_from_uploads(uploaded_files)
        tests = uploaded_tests if uploaded_tests else local_tests
        test_names = list(tests.keys())

        if test_names:
            default_index = 0
            if st.session_state.current_test_name in test_names:
                default_index = test_names.index(st.session_state.current_test_name)

            selected_test = st.selectbox(
                "Çözülecek test",
                test_names,
                index=default_index,
            )
            set_test(selected_test)
        else:
            tests = {}
            st.session_state.current_test_name = ""

        st.divider()

        if st.session_state.current_test_name:
            questions = tests.get(st.session_state.current_test_name, [])
            valid_questions = [q for q in questions if "error" not in q]
            total = len(valid_questions)

            st.metric("Toplam soru", total)
            st.metric("Doğru işaretlenen", score_for_test(st.session_state.current_test_name, valid_questions))

            if total:
                selected_number = st.number_input(
                    "Soru numarasına git",
                    min_value=1,
                    max_value=total,
                    value=min(st.session_state.current_index + 1, total),
                    step=1,
                )
                new_index = int(selected_number) - 1
                if new_index != st.session_state.current_index:
                    st.session_state.current_index = new_index
                    reset_question_state()
                    st.rerun()

                col_prev, col_next = st.columns(2)
                with col_prev:
                    if st.button("← Önceki", use_container_width=True):
                        go_previous(total)
                        st.rerun()
                with col_next:
                    if st.button("Sonraki →", type="primary", use_container_width=True):
                        go_next(total)
                        st.rerun()

                if st.button("Bu testteki cevaplarımı sıfırla", use_container_width=True):
                    st.session_state.answers[st.session_state.current_test_name] = {}
                    reset_question_state()
                    st.rerun()

    if not st.session_state.current_test_name:
        render_empty_state()
        return

    questions = tests.get(st.session_state.current_test_name, [])

    if questions and "error" in questions[0]:
        st.error(f"Bu test okunamadı: {questions[0]['error']}")
        return

    if not questions:
        render_empty_state()
        return

    total = len(questions)
    st.session_state.current_index = max(0, min(st.session_state.current_index, total - 1))
    question = questions[st.session_state.current_index]

    test_name = st.session_state.current_test_name
    index = st.session_state.current_index
    stored_answer = get_stored_answer(test_name, index)
    answer_key = current_answer_key(test_name, index)

    number = question.get("number") or index + 1
    header = question.get("header", "").strip()

    st.markdown(f"<span class='meta-pill'>Soru {index + 1} / {total}</span>", unsafe_allow_html=True)
    st.subheader(f"Soru {number}")
    
    # METADATA BÖLÜMÜNÜN İŞLENMESİ (ROZETLER)
    if header:
        tags = re.findall(r"\[(.*?)\]", header)
        if tags:
            # Sadece kısa çizgi olanları atlayıp geçerli tagleri filtrele
            valid_tags = [t for t in tags if t.strip() and t.strip() != "—"]
            tags_html = "".join([f"<span class='tag-pill'>{t}</span>" for t in valid_tags])
            st.markdown(f"<div>{tags_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='small-muted'>{header}</div>", unsafe_allow_html=True)

    st.markdown(
        f"<div class='question-box'>{question.get('stem', '').strip()}</div>",
        unsafe_allow_html=True,
    )

    st.write("")
    choices = question.get("choices", {})
    choice_labels = [f"{letter}) {choices[letter]}" for letter in CHOICE_LETTERS if letter in choices]
    label_to_letter = {f"{letter}) {choices[letter]}": letter for letter in CHOICE_LETTERS if letter in choices}

    if not choice_labels:
        st.warning("Bu soruda şık bulunamadı.")
        return

    default_choice_index = None
    if stored_answer:
        for i, label in enumerate(choice_labels):
            if label.startswith(f"{stored_answer})"):
                default_choice_index = i
                break

    selected_label = st.radio(
        "Cevabın",
        choice_labels,
        index=default_choice_index,
        key=answer_key,
    )
    selected_letter = label_to_letter.get(selected_label)
    store_answer(test_name, index, selected_letter)

    action_col1, action_col2, action_col3 = st.columns([1, 1, 1.4])
    with action_col1:
        if st.button("Cevabı Kontrol Et", type="primary", use_container_width=True):
            if not selected_letter:
                st.warning("Önce bir şık seç.")
            else:
                correct = question.get("correct")
                st.session_state.feedback_mode = "correct" if selected_letter == correct else "wrong"
                st.rerun()
    with action_col2:
        if st.button("Cevabı Göster", use_container_width=True):
            st.session_state.feedback_mode = "reveal"
            st.rerun()
    with action_col3:
        if st.button("Seçimi temizle", use_container_width=True):
            st.session_state.answers.setdefault(test_name, {}).pop(index, None)
            st.session_state.pop(answer_key, None)
            reset_question_state()
            st.rerun()

    render_feedback(question, selected_letter)


if __name__ == "__main__":
    main()