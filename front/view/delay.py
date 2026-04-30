import streamlit as st

def show_delay_page():
    # 1. 상단 내비게이션
    if st.button("🏠 메인으로"):
        st.session_state.page = "main"
        st.rerun()
    
    # 2. 타이틀 영역
    st.markdown(
        """
        <div style="text-align: center; padding-top: 20px; padding-bottom: 20px;">
            <h2 style="color: #666; font-weight: 400; margin-bottom: 0px;">항공 예약 완료 고객</h2>
            <h1 style="font-size: 45px; line-height: 1.3;">내 비행기 예상 지연 시간<br>확인하기</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )

    st.markdown("<hr style='border: 0.5px solid #ddd;'>", unsafe_allow_html=True)

    # 공항 데이터 리스트
    korea_airports = ["선택해주세요", "인천(ICN)", "김포(GMP)", "김해(PUS)", "제주(CJU)", "대구(TAE)", "청주(CJJ)"]
    usa_airports = ["선택해주세요", "로스앤젤레스(LAX)", "뉴욕(JFK)", "샌프란시스코(SFO)", "시카고(ORD)", "시애틀(SEA)", "호놀룰루(HNL)"]

    # 3. 필수 입력 사항 영역
    st.markdown("<h3 style='text-align: center; margin-top: 30px;'>✅ 항공 정보 입력</h3>", unsafe_allow_html=True)
    
    # 시간(0-23)과 분(0-59) 리스트 생성
    hour_options = [f"{i:02d}시" for i in range(24)]
    minute_options = [f"{i:02d}분" for i in range(60)]

    # --- [출발 정보 세트] ---
    st.markdown("<p style='text-align: center; margin-top: 20px; margin-bottom: 5px;'>출발 날짜</p>", unsafe_allow_html=True)
    dep_date = st.date_input("출발 날짜_delay", label_visibility="collapsed", key="delay_dep_date")

    st.markdown("<p style='text-align: center; margin-top: 10px; margin-bottom: 5px;'>출발 시간</p>", unsafe_allow_html=True)
    col_dep_h, col_dep_m = st.columns(2) # 시간과 분을 나란히 배치
    with col_dep_h:
        dep_hour = st.selectbox("출발 시", options=hour_options, label_visibility="collapsed", key="delay_dep_h")
    with col_dep_m:
        dep_min = st.selectbox("출발 분", options=minute_options, label_visibility="collapsed", key="delay_dep_m")

    st.markdown("<hr style='border: 0.5px dashed #eee; width: 50%; margin: 20px auto;'>", unsafe_allow_html=True)

    # --- [도착 정보 세트] ---
    st.markdown("<p style='text-align: center; margin-top: 10px; margin-bottom: 5px;'>도착 날짜</p>", unsafe_allow_html=True)
    arr_date = st.date_input("도착 날짜_delay", label_visibility="collapsed", key="delay_arr_date")

    st.markdown("<p style='text-align: center; margin-top: 10px; margin-bottom: 5px;'>도착 시간</p>", unsafe_allow_html=True)
    col_arr_h, col_arr_m = st.columns(2)
    with col_arr_h:
        arr_hour = st.selectbox("도착 시", options=hour_options, label_visibility="collapsed", key="delay_arr_h")
    with col_arr_m:
        arr_min = st.selectbox("도착 분", options=minute_options, label_visibility="collapsed", key="delay_arr_m")

    st.markdown("<hr style='border: 0.5px dashed #eee; width: 50%; margin: 20px auto;'>", unsafe_allow_html=True)

    # 공항 데이터 리스트
    korea_airports = ["선택해주세요", "인천(ICN)", "김포(GMP)", "김해(PUS)", "제주(CJU)", "대구(TAE)", "청주(CJJ)"]
    usa_airports = ["선택해주세요", "로스앤젤레스(LAX)", "뉴욕(JFK)", "샌프란시스코(SFO)", "시카고(ORD)", "시애틀(SEA)", "호놀룰루(HNL)"]

    # [공항 선택 세트]
    st.markdown("<h3 style='text-align: center; margin-top: 30px;'>📍 공항 및 항공사 선택</h3>", unsafe_allow_html=True)

    # 출발 공항 (한국)
    st.markdown("<p style='text-align: center; margin-top: 15px; margin-bottom: 5px;'>출발 공항 (한국)</p>", unsafe_allow_html=True)
    dep_airport_delay = st.selectbox(
        "출발공항_delay", 
        options=korea_airports, 
        label_visibility="collapsed", 
        key="delay_dep_airport"
    )

    # 도착 공항 (미국)
    st.markdown("<p style='text-align: center; margin-top: 15px; margin-bottom: 5px;'>도착 공항 (미국)</p>", unsafe_allow_html=True)
    arr_airport_delay = st.selectbox(
        "도착공항_delay", 
        options=usa_airports, 
        label_visibility="collapsed", 
        key="delay_arr_airport"
    )

    # 항공사 리스트 데이터
    airline_options = [
        "선택해주세요", "대한항공(KAL)", "아시아나항공(AAR)", "델타항공(DAL)", 
        "유나이티드항공(UAL)", "아메리칸항공(AAL)", "하와이안항공(HAL)", "에어부산(ABL)"
    ]

    # 항공사 선택
    st.markdown("<p style='text-align: center; margin-top: 15px; margin-bottom: 5px;'>항공사 선택</p>", unsafe_allow_html=True)
    airline_delay = st.selectbox(
        "항공사_delay", 
        options=airline_options, 
        label_visibility="collapsed", 
        key="delay_airline"
    )

    st.write("\n" * 3)

    # 5. 분석 시작 버튼
    if st.button("⏰ 지연 시간 예측 시작하기", use_container_width=True, type="primary"):
        # 필수 값(공항 선택) 확인
        if dep_airport_delay != "선택해주세요" and arr_airport_delay != "선택해주세요":
            st.session_state.page = "delayload" # 지연 로딩 페이지로 이동
            st.rerun()
        else:
            st.error("출발 공항과 도착 공항을 모두 선택해 주세요!")

    st.write("\n" * 5)