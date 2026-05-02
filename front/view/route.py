import streamlit as st

def show_route_page():
    # 0. 스타일 설정
    st.markdown(
        """
        <style>
            div.stButton > button[kind="primary"] {
                background-color: #001f3f !important;
                color: white !important;
                border: none !important;
            }
            div.stButton > button[kind="primary"]:hover {
                background-color: #003366 !important;
            }
            /* 멀티셀렉트 태그 색상 조절 (선택 사항) */
            span[data-baseweb="tag"] {
                background-color: #001f3f !important;
                color: white !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 2. 타이틀 영역
    st.markdown(
        """
        <div style="text-align: center; padding-top: 20px; padding-bottom: 20px;">
            <h2 style="color: #666; font-weight: 400; margin-bottom: 0px;">항공 예약 전 고객</h2>
            <h1 style="font-size: 45px; line-height: 1.3;">행복한 여행을 위한<br>최적의 노선 확인하기</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )

    st.markdown("<hr style='border: 0.5px solid #ddd;'>", unsafe_allow_html=True)

    # 데이터 리스트
    korea_airports = ["선택해주세요", "인천(ICN)", "김포(GMP)", "김해(PUS)", "제주(CJU)", "대구(TAE)", "청주(CJJ)"]
    usa_airports = ["선택해주세요", "로스앤젤레스(LAX)", "뉴욕(JFK)", "샌프란시스코(SFO)", "시카고(ORD)", "시애틀(SEA)", "호놀룰루(HNL)"]
    
    # 한국-미국 주요 운항 항공사 리스트
    airline_list = [
        "대한항공 (Korean Air)", "아시아나항공 (Asiana Airlines)", 
        "델타항공 (Delta Air Lines)", "유나이티드항공 (United Airlines)", 
        "아메리칸항공 (American Airlines)", "에어프레미아 (Air Premia)", 
        "하와이안항공 (Hawaiian Airlines)", "일본항공 (JAL)", 
        "전일본공수 (ANA)", "에어캐나다 (Air Canada)", "캐세이퍼시픽 (Cathay Pacific)"
    ]
    
    time_options = ["선택 안 함"] + [f"{i:02d}:00 이후" for i in range(24)]

    # 3. 필수 입력 사항 영역
    st.markdown("<h3 style='text-align: center; margin-top: 30px;'>✅ 필수 입력 사항</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<p style='text-align: center; margin-bottom: 5px;'>출발지 (한국)</p>", unsafe_allow_html=True)
        dep_airport = st.selectbox("출발지_hidden", options=korea_airports, label_visibility="collapsed", key="sel_dep")
    with col2:
        st.markdown("<p style='text-align: center; margin-bottom: 5px;'>목적지 (미국)</p>", unsafe_allow_html=True)
        arr_airport = st.selectbox("목적지_hidden", options=usa_airports, label_visibility="collapsed", key="sel_arr")

    # 4. 추가 입력 사항 영역
    st.markdown("<h3 style='text-align: center; margin-top: 50px;'>➕ 추가 입력 사항 (선택)</h3>", unsafe_allow_html=True)
    
    opt_col1, opt_col2 = st.columns(2)

    with opt_col1:
        # (1) 선호 항공사 (중복 선택 및 검색 가능)
        st.markdown("<p style='text-align: center; margin-bottom: 5px;'>1. 선호 항공사 (중복 선택 가능)</p>", unsafe_allow_html=True)
        selected_airlines = st.multiselect(
            "항공사_hidden", 
            options=airline_list, 
            placeholder="항공사를 검색하거나 선택하세요",
            label_visibility="collapsed", 
            key="opt_1_multi"
        )

    with opt_col2:
        # (2) 선호 시간대
        st.markdown("<p style='text-align: center; margin-bottom: 5px;'>2. 선호 시간대</p>", unsafe_allow_html=True)
        time_col1, time_col2 = st.columns(2)
        with time_col1:
            pref_dep_time = st.selectbox("출발시간_hidden", options=time_options, label_visibility="collapsed", key="opt_time_dep")
        with time_col2:
            pref_arr_time = st.selectbox("도착시간_hidden", options=time_options, label_visibility="collapsed", key="opt_time_arr")
        st.markdown("<p style='font-size: 11px; color: #999; text-align: center; margin-top: -10px;'>출발 시간 / 도착 시간</p>", unsafe_allow_html=True)

    st.write("\n" * 3)

    # 5. 분석 시작 버튼
    if st.button("🚀 최적의 노선 분석 시작하기", use_container_width=True, type="primary"):
        if dep_airport != "선택해주세요" and arr_airport != "선택해주세요":
            # 선택된 항공사 리스트는 selected_airlines 변수에 저장됨
            st.session_state.page = "routeload"
            st.rerun()
        else:
            st.error("출발지와 목적지를 목록에서 선택해 주세요!")

    st.write("\n" * 5)