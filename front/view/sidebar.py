import streamlit as st
import os

# 1. 현재 app.py 파일이 있는 폴더 경로를 구합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
# 2. 해당 폴더를 기준으로 resource/logo.png의 전체 경로를 만듭니다.
logo_path = os.path.join(current_dir, "../resource", "logo.png")

def show_sidebar():
    with st.sidebar:
        if os.path.exists(logo_path):
            # 양옆에 빈 공간을 만들어 로고를 가운데로 몹니다.
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.image(logo_path, width=100)
        else:
            st.error("로고 파일을 찾을 수 없습니다.")
        
        if st.button("🏠 Sky Cast 홈", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()
            
        st.write("---")
        
        st.markdown("### 🛫 항공 예약 전")
        if st.button("최적의 노선 확인", key="side_route", use_container_width=True):
            st.session_state.page = "route"
            st.rerun()

        st.markdown("### 🛬 항공 예약 완료")
        if st.button("내 비행기 예상 지연 시간 확인", key="side_delay", use_container_width=True):
            st.session_state.page = "delay"
            st.rerun()

        st.markdown("### Online Leaning 시뮬레이션")
        if st.button("🖥️모델 업데이트 과정 보기", key="side_model", use_container_width=True):
            st.session_state.page = "model"
            st.rerun()