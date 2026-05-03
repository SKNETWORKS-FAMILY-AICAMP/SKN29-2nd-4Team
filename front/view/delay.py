import streamlit as st
import os
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def show_delay_page():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(current_dir, "../resource", "airport.jpg")

    # 0. 스타일 설정
    st.markdown(
        """
        <style>
            /* === 전체 배경 및 컨테이너 === */
            [data-testid="stAppViewBlockContainer"] {
                max-width: 860px !important;
                padding: 0 2rem 4rem !important;
                margin: 0 auto !important;
            }

            /* 배너는 컨테이너 밖으로 full-width 처리 */
            .delay-banner-outer {
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

            /* === selectbox 테두리 === */
            [data-baseweb="select"] > div {
                border-radius: 10px !important;
                border-color: #D1D9E6 !important;
                transition: border-color 0.2s ease;
            }
            [data-baseweb="select"] > div:focus-within {
                border-color: #001f3f !important;
                box-shadow: 0 0 0 2px rgba(0, 31, 63, 0.1) !important;
            }

            /* === date_input 테두리 === */
            [data-baseweb="input"] > div {
                border-radius: 10px !important;
                border-color: #D1D9E6 !important;
            }
            [data-baseweb="input"] > div:focus-within {
                border-color: #001f3f !important;
                box-shadow: 0 0 0 2px rgba(0, 31, 63, 0.1) !important;
            }

            .field-label {
                font-size: 13px;
                font-weight: 600;
                color: #374151;
                margin-bottom: 6px;
            }

            /* 섹션 구분 텍스트 */
            .section-heading {
                font-size: 15px;
                font-weight: 700;
                color: #001f3f;
                margin: 32px 0 16px;
                padding-bottom: 10px;
                border-bottom: 1px solid #EAECF0;
            }



            /* 배너 텍스트 애니메이션 */
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .banner-text { animation: fadeInUp 1s ease-out; }
        </style>
        """,
        unsafe_allow_html=True
    )

    # === 히어로 배너 (route_page.py와 동일한 스타일) ===
    if os.path.exists(img_path):
        img_base64 = get_base64_of_bin_file(img_path)
        bg = f"linear-gradient(rgba(0, 31, 63, 0.5), rgba(0, 31, 63, 0.5)), url('data:image/jpg;base64,{img_base64}')"
    else:
        bg = "linear-gradient(rgba(0, 31, 63, 0.8), rgba(0, 31, 63, 0.8))"

    st.markdown(
        f"""
        <div class="delay-banner-outer">
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
                    <h1 style="font-size: 40px; margin: 0; font-weight: 900; letter-spacing: -1.5px; color: white;">내 비행기 예상 지연 시간<br>확인하기</h1>
                    <div style="width: 40px; height: 2px; background: rgba(255,255,255,0.7); margin: 18px auto;"></div>
                    <p style="font-size: 16px; line-height: 1.7; font-weight: 300; opacity: 0.9; margin: 0;">
                        항공 예약 완료 고객을 위한 실시간 지연 예측 서비스입니다.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 데이터 리스트
    korea_airports = ["선택해주세요", "인천(ICN)", "김포(GMP)", "김해(PUS)", "제주(CJU)", "대구(TAE)", "청주(CJJ)"]
    usa_airports = ["선택해주세요", "로스앤젤레스(LAX)", "뉴욕(JFK)", "샌프란시스코(SFO)", "시카고(ORD)", "시애틀(SEA)", "호놀룰루(HNL)"]
    airline_options = ["선택해주세요", "대한항공(KAL)", "아시아나항공(AAR)", "델타항공(DAL)", "유나이티드항공(UAL)", "아메리칸항공(AAL)", "하와이안항공(HAL)", "에어부산(ABL)"]
    hour_options = [f"{i:02d}시" for i in range(24)]
    minute_options = [f"{i:02d}분" for i in range(60)]

    # === 섹션 1: 항공 일정 입력 ===
    st.markdown("<div class='section-heading'>✅ 항공 일정 입력</div>", unsafe_allow_html=True)

    # 출발 정보
    st.markdown("<div class='field-label'>🛫 출발 정보</div>", unsafe_allow_html=True)
    col_dep_date, col_dep_time = st.columns([1, 1])
    with col_dep_date:
        st.markdown("<div class='field-label'>출발 날짜</div>", unsafe_allow_html=True)
        dep_date = st.date_input("출발 날짜_delay", label_visibility="collapsed", key="delay_dep_date")
    with col_dep_time:
        st.markdown("<div class='field-label'>출발 시각</div>", unsafe_allow_html=True)
        col_h, col_m = st.columns(2)
        with col_h:
            dep_hour = st.selectbox("출발 시", options=hour_options, label_visibility="collapsed", key="delay_dep_h")
        with col_m:
            dep_min = st.selectbox("출발 분", options=minute_options, label_visibility="collapsed", key="delay_dep_m")

    st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)

    # 도착 정보
    st.markdown("<div class='field-label'>🛬 도착 정보</div>", unsafe_allow_html=True)
    col_arr_date, col_arr_time = st.columns([1, 1])
    with col_arr_date:
        st.markdown("<div class='field-label'>도착 날짜</div>", unsafe_allow_html=True)
        arr_date = st.date_input("도착 날짜_delay", label_visibility="collapsed", key="delay_arr_date")
    with col_arr_time:
        st.markdown("<div class='field-label'>도착 시각</div>", unsafe_allow_html=True)
        col_h, col_m = st.columns(2)
        with col_h:
            arr_hour = st.selectbox("도착 시", options=hour_options, label_visibility="collapsed", key="delay_arr_h")
        with col_m:
            arr_min = st.selectbox("도착 분", options=minute_options, label_visibility="collapsed", key="delay_arr_m")

    # === 섹션 2: 공항 및 항공사 선택 ===
    st.markdown("<div class='section-heading'>📍 공항 및 항공사 선택</div>", unsafe_allow_html=True)

    col_air1, col_air2, col_air3 = st.columns(3)
    with col_air1:
        st.markdown("<div class='field-label'>출발 공항 (한국)</div>", unsafe_allow_html=True)
        dep_airport_delay = st.selectbox("출발공항_delay", options=korea_airports, label_visibility="collapsed", key="delay_dep_airport")
    with col_air2:
        st.markdown("<div class='field-label'>도착 공항 (미국)</div>", unsafe_allow_html=True)
        arr_airport_delay = st.selectbox("도착공항_delay", options=usa_airports, label_visibility="collapsed", key="delay_arr_airport")
    with col_air3:
        st.markdown("<div class='field-label'>항공사</div>", unsafe_allow_html=True)
        airline_delay = st.selectbox("항공사_delay", options=airline_options, label_visibility="collapsed", key="delay_airline")

    st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)

    # === 분석 버튼 ===
    if st.button("⏰ 지연 시간 예측 시작하기", use_container_width=True, type="primary"):
        if dep_airport_delay != "선택해주세요" and arr_airport_delay != "선택해주세요":
            st.session_state.page = "delayload"
            st.rerun()
        else:
            st.error("출발 공항과 도착 공항을 모두 선택해 주세요!")
