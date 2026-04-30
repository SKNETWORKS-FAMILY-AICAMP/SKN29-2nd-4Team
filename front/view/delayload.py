import streamlit as st
import time

def show_delayload_page():
    # 1. 상단 여백 (중앙 배치를 위해)
    st.write("\n" * 5)
    
    # 2. 메인 메시지 영역 (중앙 정렬)
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="font-size: 32px; color: #333;">선택하신 항공편의 <br>지연 가능성을 분석 중입니다.</h1>
            <p style="font-size: 18px; color: #777; margin-top: 10px;">
                실시간 기상 데이터와 과거 운항 기록을 대조하고 있습니다.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # 3. 분석 진행 상태 (st.status 활용)
    with st.status("🔍 지연 요인 정밀 분석 중...", expanded=True) as status:
        st.write("📡 실시간 현지 기상 상황 수집 중...")
        time.sleep(1.2)
        st.write("✈️ 해당 항공기 경로의 정체 여부 확인 중...")
        time.sleep(1.2)
        st.write("📊 머신러닝 알고리즘 기반 지연 확률 계산 중...")
        time.sleep(1.5)
        status.update(label="분석이 완료되었습니다!", state="complete", expanded=False)
    
    # 4. 분석 완료 후 결과 페이지(7p)로 이동
    time.sleep(1)
    st.session_state.page = "delayresult" # 7페이지 지연 결과 화면으로 이동
    st.rerun()