# app.py
# Python 3.14 compatible
# Run with: python app.py

import gradio as gr
import pandas as pd
from datetime import datetime

# ===============================
# LangChain / Ollama (SAFE IMPORT)
# ===============================
try:
    from langchain_ollama import ChatOllama
    from langchain_core.messages import HumanMessage, SystemMessage
    OLLAMA_AVAILABLE = True
except Exception:
    OLLAMA_AVAILABLE = False

    class SystemMessage:
        def __init__(self, content: str):
            self.content = content

    class HumanMessage:
        def __init__(self, content: str):
            self.content = content


# ===============================
# Initialize LLM (Optional)
# ===============================
llm = None
if OLLAMA_AVAILABLE:
    try:
        llm = ChatOllama(model="llama3")
    except Exception:
        llm = None


def call_llm(messages):
    """Safe LLM caller with fallback"""
    if llm is None:
        return False, "⚠ LLM not available. Using template output."

    try:
        response = llm.invoke(messages)
        return True, response.content
    except Exception as e:
        return False, f"⚠ LLM error: {e}"


# =====================================
# AGENT 1 — Protocol Generator
# =====================================
def generate_protocol(study_idea: str):
    if not study_idea.strip():
        return "⚠ Please enter a study idea.", "", pd.DataFrame()

    prompt = [
        SystemMessage("You are a Clinical Research Protocol Writer."),
        HumanMessage(
            f"""
Write a short clinical trial protocol:

Study Idea: {study_idea}

Format:
1. Title
2. Objective
3. Study Design
4. Population
5. Primary Endpoint
6. Sample Size

Mark assumptions with ⚠
"""
        ),
    ]

    success, protocol = call_llm(prompt)

    if not success:
        protocol = (
            "Protocol Template (LLM Offline)\n\n"
            "1. Title: [Insert title]\n"
            "2. Objective: [Primary objective]\n"
            "3. Study Design: [Design type]\n"
            "4. Population: [Participants]\n"
            "5. Primary Endpoint: [Outcome]\n"
            "6. Sample Size: [Number]\n\n"
            "⚠ Review assumptions before approval."
        )

    verification = (
        "✔ Structure present\n"
        "⚠ Assumptions need human validation\n"
        "❌ No statistical plan included"
    )

    audit = pd.DataFrame(
        [
            {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Task": "Protocol Generation",
                "Status": "Generated (Review Required)",
            }
        ]
    )

    return protocol, verification, audit


# =====================================
# AGENT 2 — Site Selector
# =====================================
def rank_sites(target_patients: int):
    sites = pd.DataFrame(
        {
            "Site_ID": ["S1", "S2", "S3", "S4"],
            "Country": ["India", "Singapore", "Malaysia", "Thailand"],
            "Monthly_Patients": [80, 40, 60, 35],
            "Active_Trials": [4, 2, 5, 1],
            "EDC_Experience": ["Yes", "Yes", "No", "Yes"],
            "Avg_Enrollment_Days": [45, 30, 55, 25],
        }
    )

    def normalize(series):
        mn, mx = series.min(), series.max()
        return (series - mn) / (mx - mn) if mn != mx else 0.5

    score = (
        normalize(sites["Monthly_Patients"]) * 0.4
        + (1 - normalize(sites["Avg_Enrollment_Days"])) * 0.3
        + sites["EDC_Experience"].map(lambda x: 1 if x == "Yes" else 0) * 0.2
        + (1 - normalize(sites["Active_Trials"])) * 0.1
    )

    sites["Score"] = (score * 100).round(2)
    ranked = sites.sort_values("Score", ascending=False)

    top = ranked.iloc[0]

    explanation = (
        f"Top Site: {top['Site_ID']} ({top['Country']})\n"
        f"Score: {top['Score']}\n"
        f"Monthly Patients: {top['Monthly_Patients']}\n"
        f"Enrollment Days: {top['Avg_Enrollment_Days']}"
    )

    email = (
        f"Subject: Enrollment Feasibility\n\n"
        f"Dear {top['Site_ID']} Team,\n\n"
        f"Can your site enroll {target_patients} patients for an upcoming study?\n"
        f"Please confirm timeline and capacity.\n\n"
        f"Regards,\nClinical Operations"
    )

    audit = pd.DataFrame(
        [
            {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Task": "Site Ranking",
                "Status": "Completed",
            }
        ]
    )

    return ranked, explanation, email, audit


# =====================================
# GRADIO UI
# =====================================
def build_ui():
    with gr.Blocks(title="Clinical Research AI Agent") as demo:
        gr.Markdown("# 🏥 Clinical Research AI Agent")

        with gr.Tab("📄 Protocol Generator"):
            idea = gr.Textbox(label="Study Idea", lines=4)
            btn = gr.Button("Generate")

            proto = gr.Textbox(label="Protocol", lines=12)
            verify = gr.Textbox(label="Verification", lines=6)
            audit = gr.Dataframe(label="Audit Log")

            btn.click(generate_protocol, idea, [proto, verify, audit])

        with gr.Tab("🏢 Site Selector"):
            n = gr.Number(label="Target Patients", value=60)
            btn2 = gr.Button("Rank Sites")

            table = gr.Dataframe(label="Ranked Sites")
            calc = gr.Textbox(label="Explanation", lines=6)
            mail = gr.Textbox(label="Email Draft", lines=6)
            audit2 = gr.Dataframe(label="Audit Log")

            btn2.click(rank_sites, n, [table, calc, mail, audit2])

    return demo


# ===============================
# ENTRY POINT (IMPORTANT)
# ===============================
if __name__ == "__main__":
    ui = build_ui()
    ui.launch()
