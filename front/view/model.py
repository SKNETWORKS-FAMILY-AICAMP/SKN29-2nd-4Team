import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import os
import base64


def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()


def update_days():
    st.session_state.sim_days = st.session_state.temp_slider


def show_model_page():
    if 'sim_days' not in st.session_state:
        st.session_state.sim_days = 10

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

    # ── 데이터 계산 ─────────────────────────────────────────────────────────
    accumulated_days = st.session_state.sim_days
    improvement = (accumulated_days // 10) * 3
    base_error = [45, 38, 52, 41]
    current_error = [
        max(10, x - improvement + int(np.random.randint(-1, 2))) for x in base_error
    ]
    after_error = [round(x * 0.45, 1) for x in current_error]

    base_avg_error = round(np.mean(current_error), 1)
    updated_avg_error = round(np.mean(after_error), 1)
    improvement_pct = round((1 - updated_avg_error / base_avg_error) * 100, 1)

    labels = ['기온 오차', '습도 오차', '풍속 오차', '지연 오차']

    # ── 섹션 1: 오차율 비교 ─────────────────────────────────────────────────
    st.markdown(
        "<div class='section-heading'>📊 &nbsp;오차율 비교 분석</div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"<div style='font-size:13px;font-weight:700;color:#001f3f;margin-bottom:4px;'>📊 업데이트 전 오차율</div>"
            f"<div style='font-size:11px;color:#9CA3AF;margin-bottom:8px;'>{accumulated_days}일 누적 데이터 기반 현재 오차</div>",
            unsafe_allow_html=True,
        )
        error_df = pd.DataFrame({'지표': labels, '오차율(%)': current_error})
        chart1 = (
            alt.Chart(error_df)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color="#ef4444")
            .encode(
                x=alt.X('지표:N', sort=None, axis=alt.Axis(labelAngle=0, labelFontSize=11, title=None)),
                y=alt.Y('오차율(%):Q', axis=alt.Axis(title='오차율 (%)', labelFontSize=11), scale=alt.Scale(domain=[0, 60])),
                tooltip=['지표', '오차율(%)'],
            )
            .properties(height=240)
            .configure_view(strokeWidth=0)
            .configure_axis(grid=False)
        )
        st.altair_chart(chart1, use_container_width=True)

    with col2:
        st.markdown(
            "<div style='font-size:13px;font-weight:700;color:#001f3f;margin-bottom:4px;'>📈 Online Learning 적용 후</div>"
            "<div style='font-size:11px;color:#9CA3AF;margin-bottom:8px;'>실시간 모델 업데이트 결과</div>",
            unsafe_allow_html=True,
        )
        updated_df = pd.DataFrame({'지표': labels, '오차율(%)': after_error})
        chart2 = (
            alt.Chart(updated_df)
            .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color="#0057b8")
            .encode(
                x=alt.X('지표:N', sort=None, axis=alt.Axis(labelAngle=0, labelFontSize=11, title=None)),
                y=alt.Y('오차율(%):Q', axis=alt.Axis(title='오차율 (%)', labelFontSize=11), scale=alt.Scale(domain=[0, 60])),
                tooltip=['지표', '오차율(%)'],
            )
            .properties(height=240)
            .configure_view(strokeWidth=0)
            .configure_axis(grid=False)
        )
        st.altair_chart(chart2, use_container_width=True)

    # ── 섹션 2: 분석 결과 ──────────────────────────────────────────────────
    st.markdown(
        f"""
        <div class="result-banner">
            <div class="result-banner-icon">💡</div>
            <div class="result-banner-text">
                학습 데이터가 <span class="result-highlight">{accumulated_days}일</span>로 확장됨에 따라
                평균 오차율이 <span class="result-highlight">{base_avg_error}%</span>
                <span class="result-arrow">→</span>
                <span class="result-highlight">{updated_avg_error}%</span>로 개선되었습니다.&nbsp;
                Online Learning 적용 시 <strong>약 {improvement_pct}% 오차 감소</strong> 효과가 예측됩니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── 섹션 3: 학습 데이터 기간 확장 ─────────────────────────────────────
    st.markdown(
        "<div class='section-heading'>📅 &nbsp;학습 데이터 기간 확장</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='font-size:13px;font-weight:700;color:#374151;margin-bottom:2px;'>누적 학습 기간 조절</div>"
        "<div style='font-size:11px;color:#9CA3AF;margin-bottom:4px;'>슬라이더를 움직여 학습 데이터의 범위를 10일 단위로 조절하세요.</div>",
        unsafe_allow_html=True,
    )
    st.slider(
        "학습 기간",
        min_value=10,
        max_value=100,
        value=st.session_state.sim_days,
        step=10,
        key="temp_slider",
        on_change=update_days,
        label_visibility="collapsed",
    )

    # 날짜 범위 계산
    start_date = "2026-05-01"
    if accumulated_days <= 31:
        end_date = f"2026-05-{accumulated_days:02d}"
    else:
        end_date = f"2026-06-{accumulated_days - 31:02d}"

    st.markdown(
        f"""
        <div class="range-badge">
            <div class="range-badge-dot"></div>
            현재 학습 범위 &nbsp;·&nbsp; <strong>{start_date} ~ {end_date}</strong>
            &nbsp;(총 <strong>{accumulated_days}일</strong>간의 데이터 학습 중)
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
    st.info("💡 위 결과는 시뮬레이션 기반 예측 수치이며, 실제 운항 데이터와 차이가 있을 수 있습니다.")
    st.markdown("<div style='height: 60px'></div>", unsafe_allow_html=True)
