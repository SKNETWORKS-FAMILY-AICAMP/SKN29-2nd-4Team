import streamlit as st
import time

from front.api.app_client import AppClient
from front.data import get_user_reservation, set_check_my_reservation

def show_delayload_page():
    st.markdown(
        """
        <style>
            /* === 컨테이너 중앙 정렬 === */
            [data-testid="stAppViewBlockContainer"] {
                max-width: 680px !important;
                padding: 0 2rem 4rem !important;
                margin: 0 auto !important;
            }

            /* === 버튼 === */
            div.stButton > button[kind="primary"] {
                background-color: #001f3f !important;
                color: white !important;
                border: none !important;
                border-radius: 10px !important;
                font-weight: 600 !important;
            }
            div.stButton > button[kind="primary"]:hover {
                background-color: #003366 !important;
            }

            /* === st.status 커스텀 === */
            [data-testid="stStatusWidget"] {
                border: 1px solid #E8ECF2 !important;
                border-radius: 14px !important;
                box-shadow: 0 2px 16px rgba(0, 31, 63, 0.06) !important;
                background: white !important;
                padding: 8px 4px !important;
            }

            /* status 내부 텍스트 */
            [data-testid="stStatusWidget"] p {
                font-size: 14px !important;
                color: #374151 !important;
            }

            /* === 페이지 헤더 === */
            .load-header {
                padding: 64px 0 48px;
                text-align: center;
                border-bottom: 1px solid #EAECF0;
                margin-bottom: 40px;
            }

            .load-eyebrow {
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 2.5px;
                text-transform: uppercase;
                color: #007bff;
                margin-bottom: 16px;
            }

            .load-title {
                font-size: 28px;
                font-weight: 800;
                color: #001f3f;
                line-height: 1.3;
                letter-spacing: -0.5px;
                margin: 0 0 12px 0;
            }

            .load-subtitle {
                font-size: 14px;
                color: #6B7280;
                font-weight: 400;
                line-height: 1.6;
                margin: 0;
            }

            /* === 진행 단계 카드 === */
            .step-label {
                font-size: 12px;
                font-weight: 600;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                color: #9CA3AF;
                margin-bottom: 12px;
                text-align: center;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # === 페이지 헤더 ===
    st.markdown(
        """
        <div class="load-header">
            <div class="load-eyebrow">✈ SKY CASTER</div>
            <h1 class="load-title">데이터를 기반으로<br>분석하고 있습니다</h1>
            <p class="load-subtitle">실시간 기상 데이터와 과거 운항 기록을 대조하여<br>지연 가능성을 계산 중입니다.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='step-label'>분석 진행 상황</div>", unsafe_allow_html=True)

    # 로딩 애니메이션 및 메시지
    with st.status("🔍 지연 요인을 정밀 분석 중입니다...", expanded=True) as status:
        st.write("📡 실시간 현지 기상 상황을 수집하는 중...")
        time.sleep(0.6)
        st.write("✈️ 해당 항공기 경로의 정체 여부를 확인하는 중...")
        time.sleep(0.6)
        st.write("📊 머신러닝 알고리즘 기반 지연 확률을 계산하는 중...")
        
        # 실제 api 호출
        client = AppClient("http://localhost:8000")
        user_reservation = get_user_reservation()
        result = client.check_my_reservation(user_reservation)
        set_check_my_reservation(result)
        status.update(label="분석 완료!", state="complete", expanded=False)

    # 분석 완료 후 결과 페이지로 이동
    time.sleep(1)
    st.session_state.page = "delayresult"
    time.sleep(0.1)
    st.rerun()
