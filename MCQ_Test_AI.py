import streamlit as st
import re
import time

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="AI MCQ Test",
    page_icon="🧠",
    layout="centered"
)

# =========================================
# CUSTOM CSS
# =========================================

st.markdown("""
<style>

.main {
    background: linear-gradient(to right, #0f172a, #1e293b);
    color: white;
}

.stApp {
    background: linear-gradient(to right, #0f172a, #1e293b);
}

h1, h2, h3, h4 {
    color: white !important;
}

.question-box {
    background-color: #111827;
    padding: 25px;
    border-radius: 15px;
    border: 2px solid #334155;
    margin-bottom: 20px;
    animation: fadeIn 0.5s ease-in-out;
}

.code-box {
    background-color: #0b1220;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #38bdf8;
    overflow-x: auto;
    color: #e2e8f0;
}

.result-card {
    background-color: #111827;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
}

.correct {
    color: #22c55e;
    font-weight: bold;
}

.wrong {
    color: #ef4444;
    font-weight: bold;
}

.option-box {
    padding: 10px;
    border-radius: 10px;
    background-color: #1e293b;
    margin-bottom: 10px;
}

@keyframes fadeIn {
    from {
        opacity:0;
        transform: translateY(10px);
    }
    to {
        opacity:1;
        transform: translateY(0px);
    }
}

</style>
""", unsafe_allow_html=True)

# =========================================
# LOAD TXT FILE
# =========================================

with open("MCQ.txt", "r", encoding="utf-8") as file:
    mcq_text = file.read()

# =========================================
# PARSER
# =========================================

def parse_mcqs(text):

    question_blocks = re.split(r'(?=Q\d+\.)', text)

    mcqs = []

    for block in question_blocks:

        block = block.strip()

        if not block:
            continue

        try:

            # QUESTION
            q_match = re.search(r'^(Q\d+\..*?)(?=\nA\.)', block, re.DOTALL)

            if not q_match:
                continue

            question = q_match.group(1).strip()

            # OPTIONS
            option_matches = re.findall(
                r'([A-D])\.\s(.*?)(?=\n[A-D]\.|\nAnswer:|\nExplanation:|$)',
                block,
                re.DOTALL
            )

            options = {}

            for key, value in option_matches:
                options[key] = value.strip()

            # ANSWER
            ans_match = re.search(
                r'Answer:\s*([A-D])\.\s*(.*)',
                block
            )

            if not ans_match:
                continue

            answer = ans_match.group(1).strip()
            answer_text = ans_match.group(2).strip()

            # EXPLANATION
            exp_match = re.search(
                r'Explanation:\s*(.*)',
                block,
                re.DOTALL
            )

            explanation = ""

            if exp_match:
                explanation = exp_match.group(1).strip()

            mcqs.append({
                "question": question,
                "options": options,
                "answer": answer,
                "answer_text": answer_text,
                "explanation": explanation
            })

        except:
            pass

    return mcqs

questions = parse_mcqs(mcq_text)

# =========================================
# SESSION STATE
# =========================================

if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "answered" not in st.session_state:
    st.session_state.answered = False

if "selected" not in st.session_state:
    st.session_state.selected = None

if "results" not in st.session_state:
    st.session_state.results = []

# =========================================
# HEADER
# =========================================

st.title("🧠 AI MCQ Test Platform")

st.markdown("### 🚀 Interactive AI Powered Quiz System")

total_questions = len(questions)

# =========================================
# SIDEBAR
# =========================================

with st.sidebar:

    st.header("📊 Live Stats")

    st.metric("Current Question", f"{st.session_state.current_q + 1}/{total_questions}")

    st.metric("Score", st.session_state.score)

    progress = st.session_state.current_q / total_questions

    st.progress(progress)

# =========================================
# RESULT PAGE
# =========================================

if st.session_state.current_q >= total_questions:

    st.balloons()

    st.success("🎉 Quiz Completed Successfully")

    percentage = (st.session_state.score / total_questions) * 100

    st.markdown(f"""
    <div class="result-card">
        <h2>🏆 Final Result</h2>
        <h3>Score: {st.session_state.score} / {total_questions}</h3>
        <h3>Percentage: {percentage:.2f}%</h3>
    </div>
    """, unsafe_allow_html=True)

    # RESULT ANALYSIS
    st.subheader("📋 Question Review")

    for idx, result in enumerate(st.session_state.results):

        status = "✅ Correct" if result["correct"] else "❌ Wrong"

        st.markdown(f"""
        <div class="result-card">
            <h4>Q{idx+1}: {status}</h4>
            <p><b>Your Answer:</b> {result['selected']}</p>
            <p><b>Correct Answer:</b> {result['correct_answer']}</p>
            <p><b>Explanation:</b> {result['explanation']}</p>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 Restart Quiz"):

        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.answered = False
        st.session_state.selected = None
        st.session_state.results = []

        st.rerun()

# =========================================
# QUIZ PAGE
# =========================================

else:

    q = questions[st.session_state.current_q]

    st.markdown(f"""
    <div class="question-box">
    <h3>Question {st.session_state.current_q + 1}</h3>
    </div>
    """, unsafe_allow_html=True)

    # CODE FORMAT SUPPORT
    if "class " in q["question"] or "print(" in q["question"]:

        st.markdown(
            f'<div class="code-box">{q["question"].replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True
        )

    else:
        st.markdown(f"### {q['question']}")

    options = list(q["options"].keys())

    selected = st.radio(
        "Choose your answer:",
        options,
        format_func=lambda x: f"{x}. {q['options'][x]}",
        key=f"q_{st.session_state.current_q}"
    )

    # =====================================
    # SUBMIT
    # =====================================

    if not st.session_state.answered:

        if st.button("✅ Submit Answer", use_container_width=True):

            st.session_state.selected = selected
            st.session_state.answered = True

            correct = selected == q["answer"]

            if correct:
                st.session_state.score += 1

            st.session_state.results.append({
                "selected": f"{selected}. {q['options'][selected]}",
                "correct_answer": f"{q['answer']}. {q['answer_text']}",
                "correct": correct,
                "explanation": q["explanation"]
            })

            st.rerun()

    # =====================================
    # EXPLANATION
    # =====================================

    else:

        if st.session_state.selected == q["answer"]:

            st.success("✅ Correct Answer")

        else:

            st.error("❌ Wrong Answer")

        st.info(f"💡 Explanation:\n\n{q['explanation']}")

        st.markdown(f"""
        ### ✅ Correct Answer:
        **{q['answer']}. {q['answer_text']}**
        """)

        time.sleep(0.3)

        col1, col2 = st.columns(2)

        with col1:

            if st.session_state.current_q > 0:

                    if st.button("⬅ Previous Question", use_container_width=True):

                        st.session_state.current_q -= 1
                        st.session_state.answered = False
                        st.session_state.selected = None

                        st.rerun()

        with col2:

            if st.button("➡ Next Question", use_container_width=True):

                st.session_state.current_q += 1
                st.session_state.answered = False
                st.session_state.selected = None

                st.rerun()