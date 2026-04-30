import streamlit as st
import time

def show_routeload_page():
    # 상단 여백
    st.write("\n" * 5)
    
    # 중앙 정렬을 위한 컨테이너
    st.markdown(
        """
        <div style="text-align: center;">
            <h1 style="font-size: 30px; color: #555;">데이터를 기반으로 분석하고 있습니다.</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    # 로딩 애니메이션 및 메시지
    with st.status("🚀 최적의 노선을 분석 중입니다...", expanded=True) as status:
        st.write("기상 데이터를 수집하는 중...")
        time.sleep(1)
        st.write("항공편 일정을 확인하는 중...")
        time.sleep(1)
        st.write("최적의 추천 경로를 계산하는 중...")
        time.sleep(1)
        status.update(label="분석 완료!", state="complete", expanded=False)
    
    # 분석 완료 후 잠시 대기했다가 결과 페이지(4p)로 이동
    time.sleep(1)
    st.session_state.page = "routeresult" # 4페이지 결과 화면으로 이동
    time.sleep(0.1)
    st.rerun()