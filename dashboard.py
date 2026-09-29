import streamlit as st
import plotly.graph_objects as go
from database import get_sessions

def check_declining_trend(scores, window=3):
    """Returns True if there's a meaningful net decline over the last `window` sessions."""
    if len(scores) < window:
        return False
    recent = scores[-window:]
    net_change = recent[-1] - recent[0]
    return net_change < -10

def render_domain_section(patient_id, domain, label, icon):
    sessions = get_sessions(patient_id, domain=domain)

    st.subheader(f"{icon} {label}")

    if len(sessions) == 0:
        st.info(f"No {label.lower()} sessions logged yet.")
        return

    timestamps = [s[3] for s in sessions]
    scores = [s[8] for s in sessions]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=scores,
        mode="lines+markers",
        name=f"{label} Score",
        line=dict(color="royalblue"),
    ))

    is_declining = check_declining_trend(scores)

    if is_declining:
        fig.add_trace(go.Scatter(
            x=timestamps[-3:],
            y=scores[-3:],
            mode="markers",
            marker=dict(color="red", size=14, symbol="x"),
            name="Flagged decline",
        ))

    fig.update_layout(
        title=f"{label} Score Over Time",
        xaxis_title="Session date",
        yaxis_title="Score (%)",
        height=350,
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"Recent {label.lower()} sessions"):
        for s in reversed(sessions[-5:]):
            st.write(f"**{s[3][:10]}** — Score: {s[8]}% | Difficulty: {s[4]} | Correct: {s[5]} | Wrong: {s[6]}")

    if is_declining:
        st.error(
            f"⚠️ {label} score has declined over the last 3 sessions "
            f"({scores[-3]}% → {scores[-2]}% → {scores[-1]}%). Recommend caregiver follow-up."
        )
    else:
        st.success(f"No concerning trends detected in the {label.lower()} domain.")

    st.divider()

def render_dashboard(patient_id):
    st.header("👨‍⚕️ Caregiver Dashboard")

    render_domain_section(patient_id, "memory", "Memory Domain", "🧠")
    render_domain_section(patient_id, "attention", "Attention Domain", "🎯")