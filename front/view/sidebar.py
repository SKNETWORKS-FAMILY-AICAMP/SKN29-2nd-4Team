import streamlit as st
import os
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def show_sidebar():
    # 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_dir, "../resource", "logo2.png") 
    
    with st.sidebar:
        # --- 사이드바 및 버튼 커스텀 스타일 ---
        st.markdown(
            """
            <style>
                /* 1. 사이드바 전체 배경색 설정 */
                [data-testid="stSidebar"] {
                    background-color: #001f3f !important; /* 남색(Navy) */
                }

                /* 2. 사이드바 내 일반 텍스트 색상 (흰색) */
                [data-testid="stSidebar"] h3, 
                [data-testid="stSidebar"] .stMarkdown {
                    color: white !important;
                }

                /* 3. 로고 이미지 스타일 및 마우스 효과 */
                .logo-container {
                    text-align: center;
                    margin-bottom: 20px;
                }
                .logo-img {
                    max-width: 85%;
                    height: auto;
                    transition: transform 0.2s;
                    cursor: pointer;
                }
                .logo-img:hover {
                    transform: scale(1.05); /* 마우스 올리면 살짝 커짐 */
                }

                /* 4. 버튼 스타일: 평소에는 흰색 배경 + 검정 글씨 */
                [data-testid="stSidebar"] .stButton>button {
                    background-color: #ffffff !important;
                    color: #000000 !important;
                    border: 1px solid #ffffff !important;
                    border-radius: 8px;
                    padding: 0.5rem 1rem;
                    transition: all 0.3s ease;
                }

                /* 5. 버튼 호버 상태: 반투명 배경 + 흰색 글씨 */
                [data-testid="stSidebar"] .stButton>button:hover {
                    background-color: rgba(255, 255, 255, 0.2) !important;
                    color: #ffffff !important;
                    border-color: rgba(255, 255, 255, 0.5) !important;
                }

                /* 6. 버튼 안의 글자색 강제 제어 (p 태그 등 대응) */
                [data-testid="stSidebar"] .stButton>button p {
                    color: inherit !important; /* 부모(button)의 색상을 따라감 */
                }
                
                /* 7. 구분선 색상 조정 */
                [data-testid="stSidebar"] hr {
                    border-color: rgba(255, 255, 255, 0.3) !important;
                }
                
            </style>
            """,
            unsafe_allow_html=True
        )

        # --- 로고 표시 (수정된 부분: href="/" 로 변경하여 주소창 초기화) ---
        if os.path.exists(logo_path):
            img_base64 = get_base64_of_bin_file(logo_path)
            st.markdown(
                f"""
                <div class="logo-container">
                    <a href="/" target="_self">
                        <img src="data:image/png;base64,{img_base64}" class="logo-img" style="width: 100%; display: block;">
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
            # 기존의 query_params 감지 로직은 삭제했습니다. 
            # href="/"가 페이지를 완전히 새로고침하여 메인으로 보내주기 때문에 필요 없습니다.

        else:
            st.markdown("<h2 style='text-align: center; color: white;'>✈️ SKY CASTER</h2>", unsafe_allow_html=True)
        
        st.write("---")
        
        # --- 메뉴 버튼들 ---
        st.write("### 🛫 항공 예약 전")
        if st.button("최적의 노선 확인", key="side_route", use_container_width=True):
            st.session_state.page = "route"
            st.rerun()

        st.write("\n")

        st.write("### 🛬 항공 예약 완료")
        if st.button("내 비행기 예상 지연 시간 확인", key="side_delay", use_container_width=True):
            st.session_state.page = "delay"
            st.rerun()

        st.write("\n")

        st.write("### 🖥️ Online Learning 시뮬레이션")
        if st.button("모델 업데이트 과정 보기", key="side_model", use_container_width=True):
            st.session_state.page = "model"
            st.rerun()