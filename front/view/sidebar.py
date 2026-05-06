import streamlit as st
import os
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def show_sidebar():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "../resource", "logo2.png") 
    
    with st.sidebar:
        st.markdown(
            """
            <style>
                /* 사이드바 배경 */
                [data-testid="stSidebar"] {
                    background-color: #001f3f !important;
                }

                /* 섹션 타이틀 */
                .sidebar-section-title {
                    color: rgba(255, 255, 255, 0.6) !important;
                    font-size: 11px !important;
                    font-weight: 600 !important;
                    letter-spacing: 1px !important;
                    margin: 20px 0 8px 5px !important;
                }

                /* --- 수정된 버튼 스타일 (흰색 테두리 + 둥근 모서리) --- */
                [data-testid="stSidebar"] .stButton>button {
                    background-color: transparent !important;
                    color: white !important;
                    
                    /* 얇은 흰색 테두리 추가 */
                    border: 1px solid rgba(255, 255, 255, 0.4) !important; 
                    /* 모서리 둥글게 */
                    border-radius: 20px !important; 
                    
                    padding: 8px 20px !important;
                    transition: all 0.3s ease !important;
                    margin-bottom: 8px !important;
                }

                /* 버튼 호버 시 스타일 */
                [data-testid="stSidebar"] .stButton>button:hover {
                    background-color: rgba(255, 255, 255, 0.1) !important;
                    border-color: rgba(255, 255, 255, 1) !important; /* 호버 시 테두리 진하게 */
                    transform: scale(1.02); /* 살짝 커지는 효과 */
                }
                
                /* 버튼 안의 텍스트 정렬 */
                [data-testid="stSidebar"] .stButton>button p {
                    color: white !important;
                    font-size: 14px !important;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        # --- 로고 영역 ---
        if os.path.exists(logo_path):
            img_base64 = get_base64_of_bin_file(logo_path)
            st.markdown(
                f"""
                <div style="text-align: center; padding: 20px 0;">
                    <a href="/" target="_self">
                        <img src="data:image/png;base64,{img_base64}" style="width: 80%;">
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        st.markdown('<hr style="border-color: rgba(255,255,255,0.1);">', unsafe_allow_html=True)

        # --- 메뉴 구성 ---
        st.markdown('<p class="sidebar-section-title">FLIGHT ANALYSIS</p>', unsafe_allow_html=True)
        if st.button("✈️  최적의 노선 확인", key="side_route", use_container_width=True):
            st.session_state.page = "route"
            st.rerun()

        if st.button("⏱️  예상 지연 여부 확인", key="side_delay", use_container_width=True):
            st.session_state.page = "delay"
            st.rerun()

        st.markdown('<p class="sidebar-section-title">SYSTEM</p>', unsafe_allow_html=True)
        if st.button("📊  Online Learnung 시뮬레이션", key="side_model", use_container_width=True):
            st.session_state.page = "model"
            st.rerun()

        # 하단 버전 표시
        st.markdown(
            """
            <div style="position: fixed; bottom: 15px; left: 15px; color: rgba(255,255,255,0.2); font-size: 10px;">
                SKY CASTER v1.0.4
            </div>
            """, 
            unsafe_allow_html=True
        )