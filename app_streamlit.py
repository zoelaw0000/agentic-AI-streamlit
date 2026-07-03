import requests
import plotly.io as pio
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu

UPLOAD_WEBHOOK = "https://sq0000.app.n8n.cloud/webhook/upload-report"

INSIGHT_WEBHOOK = "https://sq0000.app.n8n.cloud/webhook/generate-insight"

QUERY_WEBHOOK = "https://sq0000.app.n8n.cloud/webhook/query"

def call_upload_workflow(uploaded_file):

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            "text/csv"
        )
    }

    try:
        response = requests.post(
            UPLOAD_WEBHOOK,
            files=files,
            timeout=180
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def call_insight_workflow(insight_input):

    try:
        response = requests.post(
            INSIGHT_WEBHOOK,
            json={
                "insight_input": insight_input
            },
            timeout=180
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


def call_query_workflow(question):

    try:
        response = requests.post(
            QUERY_WEBHOOK,
            json={
                "question": question
            },
            timeout=180
        )

        response.raise_for_status()

        return response.json()

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Page configuration
st.set_page_config(
    page_title="Hybrid Medical Data Management System",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>

/* Metric Cards */
[data-testid="stMetric"] {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 15px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    height: 45px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Title
st.title("🏥 Hybrid Medical Data Management & Analytics System")
st.caption(
    "Conversational Healthcare Data Analysis and Readmission Prediction"
)

st.divider()

# Sidebar navigation

with st.sidebar:

    page = option_menu(
        "Navigation",
        [
            "Upload Data",
            "Prediction",
            "Analytic Report",
            "Natural Language Analysis"
        ],
        icons=[
            "cloud-upload",
            "activity",
            "bar-chart",
            "robot"
        ],
        default_index=0
    )

#--------------------------------------------------------------------------------------------------------------------------------------------------------------

if page == "Upload Data":

    st.header("Upload Medical Dataset")

    st.markdown("""
    ### Processing Pipeline

    📂 Upload Dataset  
    ➡ Validate Dataset  
    ➡ Automated Preprocessing  
    ➡ Database Storage  
    ➡ Readmission Prediction  
    ➡ AI Analytics Generation  
    """)

    st.write(
        "Upload a CSV file. The system will automatically clean, validate, "
        "insert the data into the database, predict readmission risks, and show analytic report."
    )

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"]
    )

    if uploaded_file is not None:

        st.info("File uploaded successfully.")

        if st.button("Process and Insert Data"):

            with st.spinner("Uploading dataset and generating predictions..."):

                result = call_upload_workflow(uploaded_file)

            # Display pipeline result
            if result["process"]["status"] == "success":

                st.session_state["process_result"] = result["process"]

                st.session_state["analytics_result"] = result["analytics"]

                st.success("✅ Dataset processed successfully")

                col1,col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Rows Inserted",
                        result["process"]["inserted_rows"]
                    )

                with col2:
                    st.metric(
                        "Duplicates Removed",
                        result["process"]["duplicates_removed"]
                    )

                with st.container(border=True):

                    st.success(
                        "✅ Dataset processed successfully. "
                        "Please navigate to the Prediction page & Analytic Report page to view prediction and analytics."
                    )

            elif result["status"] == "warning":

                st.warning(result["message"])

            else:

                st.error("Upload failed.")
                st.json(result["details"])

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
elif page == "Prediction":

    st.subheader("📊 Prediction Summary")

    if "process_result" not in st.session_state:

        st.info(
            "No prediction results available. "
            "Please upload a dataset first."
        )

    else:

        result = st.session_state["process_result"]

        with st.container(border=True):

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "High-Risk Patients",
                    result['high_risk_count']
                )

            with col2:
                st.metric(
                    "High-Risk Rate",
                    f"{result['high_risk_rate']}%"
                )

            with col3:
                st.metric(
                    "Average Risk Score",
                    f"{result['average_probability']:.2%}"
                )

        high_risk_df = pd.DataFrame(result["prediction_result"])

        high_risk_df = high_risk_df[
            high_risk_df["risk_level"] == "High Risk"
        ]

        st.subheader("🔴 High-Risk Patients")

        display_columns = [
            "patient_nbr",
            "age",
            "time_in_hospital",
            "num_medications",
            "readmission_probability"
        ]

        available_columns = [
            col for col in display_columns
            if col in high_risk_df.columns
        ]

        st.dataframe(
            high_risk_df[available_columns],
            use_container_width=True
        )
#--------------------------------------------------------------------------------------------------------------------------------------------------------------
elif page == "Analytic Report":

    st.header("📈 Analytic Report")

    if "analytics_result" not in st.session_state:

        st.warning(
            "Please upload a dataset first."
        )

    else:

        analytics = st.session_state["analytics_result"]

        metrics = analytics["metrics"]

        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric(
                "Uploaded Cases",
                metrics["uploaded_cases"]
            )

        with col2:
            st.metric(
                "High-Risk Patients",
                metrics["high_risk_patients"]
            )

        with col3:
            st.metric(
                "Average Risk Score",
                f"{metrics['average_risk_score']:.2%}"
            )

        with col4:
            st.metric(
                "Average Stay",
                f"{metrics['average_stay']:.1f} days"
            )

        with col5:
            st.metric(
                "Avg Medications",
                f"{metrics['average_medications']:.1f}"
            )

        st.divider()

        st.subheader("👥 Demographic Analysis")

        col1, col2 = st.columns(2)

        with col1:
            fig = pio.from_json(
                analytics["charts"]["age_distribution"]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:
            fig = pio.from_json(
                analytics["charts"]["gender_distribution"]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        fig = pio.from_json(
            analytics["charts"]["race_distribution"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

        st.subheader("🏥 Clinical Analysis")

        col1, col2 = st.columns(2)

        with col1:
            fig = pio.from_json(
                analytics["charts"]["hospital_stay"]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        with col2:
            fig = pio.from_json(
                analytics["charts"]["medication_distribution"]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        st.divider()

        st.subheader("🎯 Readmission Risk Analysis")

        fig = pio.from_json(
            analytics["charts"]["risk_distribution"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.divider()

        st.subheader("🧩 Patient Segmentation")

        fig = pio.from_json(
            analytics["charts"]["cluster_heatmap"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        fig = pio.from_json(
            analytics["charts"]["cluster_risk"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )
        st.divider()

        st.subheader("🤖 AI-Generated Insights")

        if st.button("Generate Insight"):

            with st.spinner("Generating AI clinical insights..."):

                st.session_state["ai_insight"] = call_insight_workflow(
                    analytics["insight_input"]
                )

            if "ai_insight" in st.session_state:

                insight = st.session_state["ai_insight"]

            st.markdown("### Executive Summary")
            st.write(insight["executive_summary"])

            st.markdown("### Key Findings")
            for item in insight["key_findings"]:
                st.markdown(f"- {item}")

            st.markdown("### Clinical Recommendations")
            for item in insight["recommendations"]:
                st.markdown(f"- {item}")

#--------------------------------------------------------------------------------------------------------------------------------------------------------------
elif page == "Natural Language Analysis":

    st.header("Natural Language Query")
    st.caption(
        "Ask questions about the medical dataset using natural language."
    )

    # User input
    question = st.chat_input(
        "Example: How many patient was readmitted?"
    )

    clear_chat = st.button("🗑️ Clear Chat")

    if clear_chat:
        st.session_state.chat_history = []

    if question:

        with st.spinner("Processing query..."):

            result = call_query_workflow(question)

            st.session_state.chat_history.append({
                "question": question,
                "result": result
            })

    st.divider()

    for chat in reversed(st.session_state.chat_history):

        with st.chat_message("user"):
            st.write(chat["question"])

        with st.chat_message("assistant"):

            result = chat["result"]

            if result["status"] != "success":

                st.error(result.get("message", "Query failed."))

            else:

                st.success("Query executed successfully.")

                st.markdown("#### Generated SQL")

                st.code(result["sql"], language="sql")

                st.markdown(f"**Rows Returned:** {result['row_count']}")

                st.dataframe(
                    pd.DataFrame(result["data"]),
                    use_container_width=True
                )

                if result["visualization"] is not None:

                    if result["visualization"]["status"] == "chart":

                        fig = pio.from_json(
                            result["visualization"]["figure"]
                        )

                        st.plotly_chart(
                            fig,
                            use_container_width=True
                        )

#--------------------------------------------------------------------------------------------------------------------------------------------------------------

