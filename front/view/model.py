import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os
import base64
from datetime import datetime
import plotly.graph_objects as go
import textwrap

import pandas as pd
import numpy as np

# ─────────────────────────────────────────────
# MOCK DATA
# ─────────────────────────────────────────────
def generate_mock_learning_curve():
    np.random.seed(42)

    dates = pd.date_range("2024-07-01", periods=31, freq="D")

    auc = 0.72 + np.random.normal(0, 0.01, 31)

    # drift 시뮬레이션
    auc[10:15] -= 0.05
    auc[20:25] -= 0.08

    actions = []
    reasons = []

    for v in auc:
        if v > 0.71:
            actions.append("skip")
            reasons.append(
                f"AUC={v:.3f} → Model is stable. No update required."
            )
        elif v > 0.66:
            actions.append("warm-update")
            reasons.append(
                f"AUC={v:.3f} → Performance drop detected. Warm update recommended to adjust weights."
            )
        else:
            actions.append("full-retrain")
            reasons.append(
                f"AUC={v:.3f} → Significant degradation detected. Full retraining is required."
            )

    return pd.DataFrame({
        "date": dates,
        "auc": auc,
        "precision": auc - 0.02 + np.random.normal(0, 0.005, 31),
        "recall": auc - 0.03 + np.random.normal(0, 0.005, 31),
        "action": actions,
        "reason": reasons
    })


# ─────────────────────────────────────────────
# SESSION INIT
# ─────────────────────────────────────────────
start_date = pd.Timestamp("2024-07-01")

if "date_range" not in st.session_state:
    st.session_state.date_range = pd.Timestamp("2024-07-01").to_pydatetime()



# def update_days():
#     st.session_state.sim_days = st.session_state.temp_slider

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def show_model_page():
    if 'sim_days' not in st.session_state:
        st.session_state.sim_days = datetime(2024, 7, 1)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(current_dir, "../resource", "airport.jpg")

    # ── 스타일 ──────────────────────────────────────────────────────────────
    st.markdown(
        """
        <style>
            /* === 컨테이너 === */
            [data-testid="stAppViewBlockContainer"] {
                max-width: 900px !important;
                padding: 0 2rem 4rem !important;
                margin: 0 auto !important;
            }

            /* === 배너 full-width === */
            .model-banner-outer {
                width: 100vw;
                position: relative;
                left: 50%;
                right: 50%;
                margin-left: -50vw;
                margin-right: -50vw;
                margin-bottom: 36px;
            }

            /* === 버튼 === */
            div.stButton > button[kind="primary"] {
                background-color: #001f3f !important;
                color: white !important;
                border: none !important;
                border-radius: 10px !important;
                font-weight: 600 !important;
                font-size: 15px !important;
                padding: 0.75rem 1rem !important;
                letter-spacing: 0.02em !important;
                transition: background-color 0.2s ease !important;
            }
            div.stButton > button[kind="primary"]:hover {
                background-color: #003366 !important;
            }

            /* === 섹션 헤딩 === */
            .section-heading {
                font-size: 15px;
                font-weight: 700;
                color: #001f3f;
                margin: 32px 0 16px;
                padding-bottom: 10px;
                border-bottom: 1px solid #EAECF0;
                display: flex;
                align-items: center;
                gap: 8px;
            }

            /* === 결과 배너 (success 대체) === */
            .result-banner {
                background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
                border: 1px solid #BFDBFE;
                border-radius: 14px;
                padding: 20px 24px;
                display: flex;
                align-items: flex-start;
                gap: 14px;
                margin: 8px 0 28px;
            }
            .result-banner-icon {
                font-size: 22px;
                flex-shrink: 0;
                margin-top: 1px;
            }
            .result-banner-text {
                font-size: 14px;
                color: #1E3A5F;
                line-height: 1.65;
            }
            .result-banner-text strong {
                color: #001f3f;
            }
            .result-highlight {
                display: inline-flex;
                align-items: center;
                gap: 4px;
                background: #001f3f;
                color: white;
                border-radius: 6px;
                padding: 1px 8px;
                font-size: 13px;
                font-weight: 700;
            }
            .result-arrow {
                display: inline-block;
                margin: 0 4px;
                color: #6B7280;
            }

            /* === 학습 범위 배지 === */
            .range-badge {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: #F0F4FF;
                border: 1px solid #DBEAFE;
                border-radius: 10px;
                padding: 10px 18px;
                font-size: 13px;
                color: #1E40AF;
                font-weight: 600;
                margin-top: 12px;
            }
            .range-badge-dot {
                width: 8px;
                height: 8px;
                background: #0057b8;
                border-radius: 50%;
                flex-shrink: 0;
            }

            /* === streamlit 차트 여백 제거 === */
            [data-testid="stVegaLiteChart"] {
                border-radius: 8px;
                overflow: hidden;
            }

            /* === info 박스 === */
            [data-testid="stAlert"] {
                border-radius: 12px !important;
                border: 1px solid #DBEAFE !important;
                background-color: #EFF6FF !important;
                color: #1E40AF !important;
                font-size: 14px !important;
            }

            /* 배너 애니메이션 */
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(20px); }
                to   { opacity: 1; transform: translateY(0); }
            }
            .banner-text { animation: fadeInUp 1s ease-out; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── 히어로 배너 ────────────────────────────────────────────────────────
    if os.path.exists(img_path):
        img_base64 = get_base64_of_bin_file(img_path)
        bg = f"linear-gradient(rgba(0,31,63,0.5), rgba(0,31,63,0.5)), url('data:image/jpg;base64,{img_base64}')"
    else:
        bg = "linear-gradient(rgba(0,31,63,0.82), rgba(0,31,63,0.82))"

    st.markdown(
        f"""
        <div class="model-banner-outer">
            <div style="
                height: 280px;
                background-image: {bg};
                background-size: cover;
                background-position: center;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                color: white;
            ">
                <div class="banner-text">
                    <h1 style="font-size:40px;margin:0;font-weight:900;letter-spacing:-1.5px;color:white;">
                        Online Learning 시뮬레이션
                    </h1>
                    <div style="width:40px;height:2px;background:rgba(255,255,255,0.7);margin:18px auto;"></div>
                    <p style="font-size:16px;line-height:1.7;font-weight:300;opacity:0.9;margin:0;">
                        누적 데이터 증가에 따른 모델 오차율 변화를 실시간으로 확인합니다.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # 히어로 배너 끝

    # 메인 시각화 line chart 부분
    df = generate_mock_learning_curve()
    df["date"] = pd.to_datetime(df["date"])

    st.markdown("### 📈 Online Learning Performance")

    # ── 날짜 범위 (고정: 7/1 ~ 7/31) ──
    min_date = pd.Timestamp("2024-07-01")
    max_date = pd.Timestamp("2024-07-31")

    # slider (🔥 key만 사용)
    date_range = st.slider(
        "학습 기간",
        min_value=min_date.to_pydatetime(),
        max_value=max_date.to_pydatetime(),
        step=pd.Timedelta(days=1),
        key="date_range"
    )

    # 바로 사용 (변환만)
    start_date = pd.Timestamp("2024-07-01")
    end_date = pd.to_datetime(date_range)

    mask = (df["date"] >= start_date) & (df["date"] <= end_date)
    df_view = df[mask]

    # ── plot ──
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_view["date"],
        y=df_view["auc"],
        mode="lines+markers",
        name="AUC"
    ))

    fig.add_trace(go.Scatter(
        x=df_view["date"],
        y=df_view["precision"],
        mode="lines",
        name="Precision"
    ))

    fig.add_trace(go.Scatter(
        x=df_view["date"],
        y=df_view["recall"],
        mode="lines",
        name="Recall"
    ))

    # ── event markers ──
    color_map = {
        "skip": "gray",
        "warm-update": "orange",
        "full-retrain": "red"
    }

    for _, row in df_view.iterrows():
        fig.add_trace(go.Scatter(
            x=[row["date"]],
            y=[row["auc"]],
            mode="markers",
            marker=dict(size=10, color=color_map[row["action"]]),
            name=row["action"],
            showlegend=False,
            hovertext=row["reason"]
        ))

    # ── legend (고정) ──
    for k, v in color_map.items():
        fig.add_trace(go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            marker=dict(size=10, color=v),
            name=k
        ))

    fig.update_layout(
        height=450,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis_title="Score"
    )

    st.plotly_chart(fig, use_container_width=True)

    # reason 출력
    latest = df_view.iloc[-1]

    action = latest["action"]
    reason = latest["reason"]
    date = latest["date"].strftime("%Y-%m-%d")

    icon_map = {
        "skip": "✅",
        "warm-update": "⚠️",
        "full-retrain": "🚨"
    }

    message = f"""
    **📌 Latest Model Decision ({date})**

    **Action:** {action.upper()} {icon_map[action]}

    {reason}
    """

    # action별로 박스 타입 다르게
    if action == "skip":
        st.info(message)
    elif action == "warm-update":
        st.warning(message)
    else:
        st.error(message)