import streamlit as st
st.set_page_config(layout="wide")
import os
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def show_main_page():
    # 1. 이미지 경로 설정 (기존 동일)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(current_dir, "../resource", "airport.jpg")

    if os.path.exists(img_path):
        img_base64 = get_base64_of_bin_file(img_path)
        
        # 2. 와이드 모드에서 여백을 완전히 제거하기 위한 CSS
        st.markdown(
            """
            <style>
                /* 메인 컨테이너 최대 너비 제한 해제 및 패딩 제거 */
                .block-container {
                    max-width: 100% !important;
                    padding-top: 0rem !important;
                    padding-bottom: 0rem !important;
                    padding-left: 0rem !important;
                    padding-right: 0rem !important;
                }
                
                /* 앱 전체 배경과 상단 여백 조절 */
                .stApp {
                    margin-top: -65px;
                }

                header { visibility: hidden; }
            </style>
            """,
            unsafe_allow_html=True
        )

        # 3. 배너 구성 (높이를 키우고 텍스트 크기를 조절하여 웅장하게 변경)
        st.markdown(
            f"""
            <div style="
                width: 100%;
                height: 500px;
                background-image: linear-gradient(rgba(0, 0, 0, 0.4), rgba(0, 0, 0, 0.4)), url('data:image/jpg;base64,{img_base64}');
                background-size: cover;
                background-position: center;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                color: white;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.7);
                margin: 0;
            ">
                <h1 style="font-size: 80px; margin: 0; font-weight: 900; letter-spacing: -2px;">Sky Cast</h1>
                <p style="font-size: 26px; line-height: 1.6; margin-top: 20px; font-weight: 400; opacity: 0.9;">
                    Sky Cast는 사용자의 기분 좋은 여행을 위해<br>
                    기상데이터를 바탕으로 최적의 항공 서비스를 제공합니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("이미지 파일을 찾을 수 없습니다.")

    # 4. 하단 영역 (내용물은 중앙에 적절히 모이도록 패딩 부여)
    # 가로로 너무 퍼지면 읽기 힘들기 때문에 하단만 max-width를 줍니다.
    st.markdown(
        """
        <div style="max-width: 1000px; margin: 0 auto; padding: 0 2rem;">
            <hr style="border: 0.5px solid #eee; margin-top: 50px;">
            <div style="text-align: center; margin-top: 40px;">
                <!-- 제목 부분에 파란색 밑줄 추가 -->
                <h2 style="margin-bottom: 20px; color: #333;">
                    <span style="border-bottom: 5px solid #007bff; padding-bottom: 5px;">
                        🔍 나에게 필요한 서비스 확인하기
                    </span>
                </h2>
                <p style="font-size: 60px; margin: 0; color: #ccc;">▼</p> 
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # 버튼 영역도 하단 컨테이너 안으로 배치
    container = st.container()
    with container:
        _, col_mid, _ = st.columns([1, 8, 1]) # 양 옆에 여백을 주어 버튼이 너무 커지지 않게 조절
        with col_mid:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🛫 항공 예약하기 전이에요.", use_container_width=True):
                    st.session_state.page = "route"
                    st.rerun()
            with c2:
                if st.button("🛬 항공 예약 완료했어요!", use_container_width=True):
                    st.session_state.page = "delay"
                    st.rerun()