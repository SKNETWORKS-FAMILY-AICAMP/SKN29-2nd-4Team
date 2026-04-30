import streamlit as st

from front.view.route import show_route_page
from front.view.main import show_main_page
from front.view.sidebar import show_sidebar
from front.view.routeload import show_routeload_page
from front.view.routeresult import show_routeresult_page
from front.view.delay import show_delay_page
from front.view.delayload import show_delayload_page
from front.view.delayresult import show_delayresult_page
from front.view.model import show_model_page

# 세션 상태 초기화
if "page" not in st.session_state:
    st.session_state.page = "main"

# 1. 사이드바 설정
show_sidebar()

# 2. 메인 화면 영역
if st.session_state.page == "main":
    # 상단 영역: 서비스 소개 (중앙 정렬)
    show_main_page()
 
elif st.session_state.page == "route":
    show_route_page() # 불러온 함수 실행

elif st.session_state.page == "delay":
    show_delay_page()
    
elif st.session_state.page == "routeload":
    show_routeload_page()

elif st.session_state.page == "routeresult":
    show_routeresult_page()

elif st.session_state.page == "delayload":
    show_delayload_page()

elif st.session_state.page == "delayresult":
    show_delayresult_page()

elif st.session_state.page == "model":
    show_model_page()