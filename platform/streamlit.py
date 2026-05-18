import streamlit as st

st.set_page_config(
    page_title="Persona Weave",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Styling ----------
st.markdown(
    """
    <style>
    /* Hide default Streamlit chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    .stApp {
        background-color: white;
    }

    /* Top bar */
    .topbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 18px 32px;
        border-bottom: 1px solid #e5e7eb;
        background: white;
    }
    .topbar-left {
        display: flex;
        gap: 24px;
        font-size: 26px;
        color: #a020a0;
        font-weight: 700;
    }
    .topbar-left span {
        cursor: pointer;
    }
    .leidos-logo {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 38px;
        font-weight: 800;
        color: #a020a0;
        letter-spacing: -0.02em;
    }

    /* Two-column layout */
    .main-grid {
        display: grid;
        grid-template-columns: 420px 1fr;
        min-height: calc(100vh - 80px);
    }

    /* Sidebar */
    .sidebar {
        background-color: #1a0d3d;
        padding: 28px 24px;
        position: relative;
        overflow: hidden;
    }
    .tab-toggle {
        background: white;
        border-radius: 999px;
        padding: 4px;
        display: flex;
        margin-bottom: 28px;
    }
    .tab-toggle button {
        flex: 1;
        padding: 12px 24px;
        border-radius: 999px;
        border: none;
        font-weight: 600;
        font-size: 16px;
        cursor: pointer;
        background: transparent;
        color: #1f2937;
        transition: all 0.2s;
    }
    .tab-toggle button.active {
        background: #a020a0;
        color: white;
    }

    .role-card {
        border-radius: 18px;
        padding: 18px;
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 14px;
        position: relative;
        cursor: pointer;
        transition: transform 0.15s;
    }
    .role-card:hover {
        transform: scale(1.01);
    }
    .role-card.active {
        background: #a020a0;
    }
    .role-card.inactive {
        background: #2d1b5e;
    }
    .role-icon {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: white;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        font-size: 24px;
        color: #1a0d3d;
    }
    .role-info h3 {
        color: white;
        font-weight: 700;
        font-size: 18px;
        margin: 0 0 4px 0;
    }
    .role-info p {
        color: rgba(255,255,255,0.8);
        font-size: 13px;
        margin: 0;
        line-height: 1.4;
    }
    .status-dot {
        position: absolute;
        top: 12px;
        right: 12px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    .status-dot.green { background: #22c55e; }
    .status-dot.red { background: #ef4444; }

    .paper-plane-bg {
        position: absolute;
        bottom: 0;
        left: 0;
        opacity: 0.2;
        pointer-events: none;
    }

    /* Main content */
    .main-content {
        padding: 48px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: calc(100vh - 80px);
    }
    .welcome {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .welcome h1 {
        font-size: 48px;
        font-weight: 700;
        color: #111827;
        margin: 0 0 12px 0;
    }
    .welcome p {
        font-size: 22px;
        color: #374151;
        margin: 0;
    }

    .model-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px;
        width: 320px;
        margin-left: auto;
        margin-bottom: 16px;
    }
    .model-card .label {
        font-size: 11px;
        font-weight: 700;
        color: #111827;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }
    .model-card .dropdown {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 999px;
        padding: 12px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 500;
        color: #1f2937;
    }

    .persona-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
    }
    .persona-card .label {
        font-size: 11px;
        font-weight: 700;
        color: #111827;
        letter-spacing: 0.08em;
        margin-bottom: 12px;
    }
    .persona-pills {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 16px;
    }
    .persona-pill {
        padding: 8px 24px;
        border-radius: 999px;
        font-weight: 600;
        font-size: 14px;
        border: 1px solid #e5e7eb;
        background: white;
        color: #1f2937;
        cursor: pointer;
    }
    .persona-pill.active {
        background: #a020a0;
        color: white;
        border-color: #a020a0;
    }

    .chat-input-wrap {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 999px;
        padding: 4px 20px;
        display: flex;
        align-items: center;
    }
    .chat-input-wrap input {
        flex: 1;
        border: none;
        outline: none;
        padding: 12px 0;
        font-size: 15px;
        background: transparent;
        color: #374151;
    }

    /* Streamlit button overrides for interactive controls */
    .stButton > button {
        border-radius: 999px !important;
        font-weight: 600 !important;
        border: 1px solid #e5e7eb !important;
        background: white !important;
        color: #1f2937 !important;
        padding: 8px 24px !important;
    }
    .stButton > button:hover {
        border-color: #a020a0 !important;
        color: #a020a0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- State ----------
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Settings"
if "active_role" not in st.session_state:
    st.session_state.active_role = "Defense Analyst"
if "active_persona" not in st.session_state:
    st.session_state.active_persona = "Persona 1"

ROLES = [
    {
        "name": "Defense Analyst",
        "description": "Defense systems, threat intelligence, strategic analysis.",
        "icon": "🛡️",
        "status": "green",
    },
    {
        "name": "Behavior Researcher",
        "description": "Human behavior analysis, stress testing, controlled experiments.",
        "icon": "🧠",
        "status": "red",
    },
    {
        "name": "Crisis Strategist",
        "description": "Media training, adversarial interviews, reputation management.",
        "icon": "💬",
        "status": "red",
    },
    {
        "name": "Therapy Trainer",
        "description": "De-escalation practice, active listening, emotional conversations.",
        "icon": "❤️",
        "status": "red",
    },
]

PERSONAS = ["Persona 1", "Persona 2", "Persona 3", "Persona 4"]

# ---------- Top bar ----------
st.markdown(
    """
    <div class="topbar">
        <div class="topbar-left">
            <span>☰</span>
            <span>🔍</span>
        </div>
        <div class="leidos-logo">
            <svg width="42" height="34" viewBox="0 0 40 32" fill="none">
                <path d="M2 20 L36 4 L20 18 L14 16 L12 28 L18 22 L26 26 L36 4"
                      stroke="#a020a0" stroke-width="2.5" fill="#a020a0"
                      fill-opacity="0.9" stroke-linejoin="round"/>
            </svg>
            leidos
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Layout ----------
sidebar_col, main_col = st.columns([1, 1.6], gap="small")

# ----- Sidebar -----
with sidebar_col:
    with st.container():
        st.markdown('<div class="sidebar">', unsafe_allow_html=True)

        # Tab toggle
        tab_cols = st.columns(2)
        with tab_cols[0]:
            if st.button(
                "History",
                key="tab_history",
                use_container_width=True,
                type="primary" if st.session_state.active_tab == "History" else "secondary",
            ):
                st.session_state.active_tab = "History"
                st.rerun()
        with tab_cols[1]:
            if st.button(
                "Settings",
                key="tab_settings",
                use_container_width=True,
                type="primary" if st.session_state.active_tab == "Settings" else "secondary",
            ):
                st.session_state.active_tab = "Settings"
                st.rerun()

        st.markdown("<div style='height: 18px'></div>", unsafe_allow_html=True)

        # Role cards
        for role in ROLES:
            is_active = role["name"] == st.session_state.active_role
            card_class = "active" if is_active else "inactive"
            dot_class = role["status"]

            card_html = f"""
            <div class="role-card {card_class}">
                <div class="status-dot {dot_class}"></div>
                <div class="role-icon">{role['icon']}</div>
                <div class="role-info">
                    <h3>{role['name']}</h3>
                    <p>{role['description']}</p>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

            # Invisible button for click handling
            if st.button(
                f"Select {role['name']}",
                key=f"role_{role['name']}",
                use_container_width=True,
            ):
                st.session_state.active_role = role["name"]
                st.rerun()

        # Decorative paper plane
        st.markdown(
            """
            <svg class="paper-plane-bg" width="280" height="180" viewBox="0 0 280 180">
                <path d="M10 130 L240 30 L120 110 L80 90 Z" fill="#a020a0" fill-opacity="0.6"/>
                <path d="M80 90 L120 110 L100 160 Z" fill="#a020a0" fill-opacity="0.4"/>
            </svg>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ----- Main content -----
with main_col:
    st.markdown(
        """
        <div class="welcome">
            <h1>Hello, User!</h1>
            <p>Welcome to Persona Weave.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Model selector card
    st.markdown(
        """
        <div class="model-card">
            <div class="label">MODEL</div>
            <div class="dropdown">
                <span>Persona Weave Beta</span>
                <span>▾</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Persona card
    st.markdown('<div class="persona-card">', unsafe_allow_html=True)
    st.markdown('<div class="label">PERSONA</div>', unsafe_allow_html=True)

    persona_cols = st.columns(4)
    for i, persona in enumerate(PERSONAS):
        with persona_cols[i]:
            is_active = persona == st.session_state.active_persona
            if st.button(
                persona,
                key=f"persona_{persona}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.active_persona = persona
                st.rerun()

    # Chat input
    user_msg = st.text_input(
        "chat",
        placeholder="How may we help you today?",
        label_visibility="collapsed",
        key="chat_input",
    )

    st.markdown("</div>", unsafe_allow_html=True)

    if user_msg:
        st.write(
            f"**{st.session_state.active_role}** ({st.session_state.active_persona}): "
            f"You said — *{user_msg}*"
        )
