import streamlit as st

def show_delayresult_page():
    # 1. 상단 내비게이션
    if st.button("🏠 메인으로"):
        st.session_state.page = "main"
        st.rerun()

    # 2. 타이틀 영역
    st.markdown(
        """
        <div style="text-align: center; padding-top: 20px; padding-bottom: 30px;">
            <h1 style="font-size: 38px;">⏰ 지연 분석 결과</h1>
            <p style="color: #666; font-size: 18px;">입력하신 항공편의 분석된 지연 정보와 현지 상황입니다.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # 3. 핵심 요약 영역 (지연 시간 & 확률)
    # 중앙 정렬을 위해 컬럼 활용
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(label="⏳ 예상 지연 시간", value="약 25분", delta="평균 대비 +5분", delta_color="inverse")
    
    with col2:
        st.metric(label="📊 지연 발생 확률", value="15%", delta="낮음", delta_color="normal")

    st.markdown("<hr style='border: 0.5px solid #ddd; margin: 30px 0;'>", unsafe_allow_html=True)

    # 4. 현지 도착지 정보 (날씨 및 상태)
    st.markdown("### 🇺🇸 도착지 현지 정보")
    
    # 카드 스타일 구현
    inner_col1, inner_col2 = st.columns([1, 2])
    
    with inner_col1:
        # 날씨 아이콘을 크게 표시 (이모지 활용)
        st.markdown(
            """
            <div style="text-align: center; background-color: #f0f2f6; padding: 20px; border-radius: 10px;">
                <span style="font-size: 70px;">☀️</span>
                <p style="margin-top: 10px; font-weight: bold;">맑음</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with inner_col2:
        st.write("**📍 목적지:** 로스앤젤레스(LAX)")
        st.write("**🌡️ 현재 기온:** 22°C")
        st.write("**💨 풍속/습도:** 3m/s / 45%")
        st.write("**📢 현지 알림:** 기상 상태 양호. 항공기 운항이 원활할 것으로 예상됩니다.")

    st.write("\n" * 3)

    # 5. 하단 버튼
    if st.button("🔄 다른 항공편 확인하기", use_container_width=True):
        st.session_state.page = "delay"
        st.rerun()

    st.write("\n" * 5)