import streamlit as st
import time

from front.data import get_user_pref_reservations, set_rank_reservations_result
from front.api.app_client import AppClient

def show_routeload_page():
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
            <p class="load-subtitle">실시간 기상 데이터와 항공편 정보를 종합하여<br>최적의 노선을 계산 중입니다.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<div class='step-label'>분석 진행 상황</div>", unsafe_allow_html=True)

    # 로딩 애니메이션 및 메시지
    with st.status("🚀 최적의 노선을 분석 중입니다...", expanded=True) as status:
        st.write("기상 데이터를 수집하는 중...")
        time.sleep(0.5)
        st.write("항공편 일정을 확인하는 중...")
        time.sleep(0.5)
        st.write("최적의 추천 경로를 계산하는 중...")

        client = AppClient("http://localhost:8000")
        request = get_user_pref_reservations()
        result = client.get_reservation_rank(request)
        set_rank_reservations_result(result)

        status.update(label="분석 완료!", state="complete", expanded=False)

    # 분석 완료 후 잠시 대기했다가 결과 페이지로 이동
    time.sleep(1)
    st.session_state.page = "routeresult"
    time.sleep(0.1)
    st.rerun()
