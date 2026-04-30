import streamlit as st

def show_route_page():
    # 1. 상단 내비게이션
    if st.button("🏠 메인으로"):
        st.session_state.page = "main"
        st.rerun()
    
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

    # 공항 데이터 리스트
    korea_airports = ["선택해주세요", "인천(ICN)", "김포(GMP)", "김해(PUS)", "제주(CJU)", "대구(TAE)", "청주(CJJ)"]
    usa_airports = ["선택해주세요", "로스앤젤레스(LAX)", "뉴욕(JFK)", "샌프란시스코(SFO)", "시카고(ORD)", "시애틀(SEA)", "호놀룰루(HNL)"]

    # 3. 필수 입력 사항 영역
    st.markdown("<h3 style='text-align: center; margin-top: 30px;'>✅ 필수 입력 사항</h3>", unsafe_allow_html=True)
    
    st.markdown("<p style='text-align: center; margin-bottom: 5px;'>출발지 (한국)</p>", unsafe_allow_html=True)
    dep_airport = st.selectbox("출발지_hidden", options=korea_airports, label_visibility="collapsed", key="sel_dep")
    
    st.markdown("<p style='text-align: center; margin-top: 15px; margin-bottom: 5px;'>목적지 (미국)</p>", unsafe_allow_html=True)
    arr_airport = st.selectbox("목적지_hidden", options=usa_airports, label_visibility="collapsed", key="sel_arr")

    # 4. 추가 입력 사항 영역 (총 5개 항목)
    st.markdown("<h3 style='text-align: center; margin-top: 50px;'>➕ 추가 입력 사항 (선택)</h3>", unsafe_allow_html=True)
    
    # (1) 선호 항공사
    st.markdown("<p style='text-align: center; margin-bottom: 5px;'>1. 선호 항공사</p>", unsafe_allow_html=True)
    opt_airline = st.text_input("항공사_hidden", label_visibility="collapsed", placeholder="예: 대한항공, 아시아나, 델타항공", key="opt_1")
    
    # (2) 좌석 등급
    st.markdown("<p style='text-align: center; margin-top: 15px; margin-bottom: 5px;'>2. 좌석 등급</p>", unsafe_allow_html=True)
    opt_seat = st.selectbox("좌석_hidden", ["선택 안 함", "이코노미", "비즈니스", "퍼스트 클래스"], label_visibility="collapsed", key="opt_2")

    # (3) 비행 방식 (직항/경유) - 추가됨
    st.markdown("<p style='text-align: center; margin-top: 15px; margin-bottom: 5px;'>3. 비행 방식</p>", unsafe_allow_html=True)
    opt_flight_type = st.radio("비행방식_hidden", ["상관없음", "직항만", "경유 포함"], label_visibility="collapsed", horizontal=True, key="opt_3")

    # (4) 예산 범위 (1인 기준) - 추가됨
    st.markdown("<p style='text-align: center; margin-top: 15px; margin-bottom: 5px;'>4. 최대 예산 (1인 기준)</p>", unsafe_allow_html=True)
    opt_budget = st.select_slider("예산_hidden", options=["제한 없음", "100만원 이하", "150만원 이하", "200만원 이하", "250만원 이하", "300만원 이상"], label_visibility="collapsed", key="opt_4")

    # (5) 위탁 수하물 여부 - 추가됨
    st.markdown("<p style='text-align: center; margin-top: 15px; margin-bottom: 5px;'>5. 위탁 수하물 포함 여부</p>", unsafe_allow_html=True)
    opt_luggage = st.checkbox("수하물 포함 노선만 보기", key="opt_5")

    st.write("\n" * 3)

    # 5. 분석 시작 버튼
    # type="primary"를 추가하여 Streamlit 대표 색상을 적용합니다.
    if st.button("🚀 최적의 노선 분석 시작하기", use_container_width=True, type="primary"):
        if dep_airport != "선택해주세요" and arr_airport != "선택해주세요":
            st.session_state.page = "routeload"
            st.rerun()
        else:
            st.error("출발지와 목적지를 목록에서 선택해 주세요!")

    st.write("\n" * 5)