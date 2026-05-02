import streamlit as st
import os
import base64
st.set_page_config(
    page_title="Sky Caster",
    layout="wide",  # 화면 꽉 채우기
    initial_sidebar_state="expanded"
)

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
        
        # 2. 사이드바와 메인 영역의 평화로운 공존을 위한 CSS
        st.markdown(
        """
        <style>
            /* 사이드바와 겹치지 않도록 너비와 패딩 조정 */
            [data-testid="stAppViewBlockContainer"] {
                max-width: 100%; 
                padding-top: 0rem !important;
                padding-right: 0rem !important;
                padding-left: 0rem !important;
                /* 하단 패딩은 조금 남겨두는 것이 좋습니다 */
                padding-bottom: 2rem !important; 
            }

            /* 배너가 헤더 영역까지 올라가도록 조정 */
            [data-testid="stHeader"] {
                background-color: rgba(0,0,0,0); /* 헤더 투명화 */
            }
        </style>
        """,
        unsafe_allow_html=True
    )

        # 3. 배너 구성 (class="full-width-banner" 추가)
        st.markdown(
            f"""
            <div class="full-width-banner" style="
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

    # 4. 하단 영역
    st.markdown(
        """
        <div style="max-width: 1000px; margin: 0 auto; padding: 0 2rem;">
            <hr style="border: 0.5px solid #ddd; margin-top: 50px;">
            <div style="text-align: center; margin-top: 40px; margin-bottom: 30px;">
                <h2 style="margin-bottom: 20px;">
                    <span style="
                        /* 그라데이션 효과 적용: 왼쪽(남색)에서 오른쪽(약간 밝은 남색)으로 */
                        background-image: linear-gradient(135deg, #001f3f 0%, #003366 100%);
                        color: white;              /* 배경이 어두우니 글자는 흰색으로 */
                        padding: 12px 45px;        /* 여백 살짝 조정 */
                        border-radius: 50px;       /* 캡슐 모양 */
                        display: inline-block;
                        font-weight: bold;
                        font-size: 26px;
                        box-shadow: 0 4px 15px rgba(0,0,0,0.1); /* 은은한 그림자 추가 */
                    ">
                        나에게 필요한 서비스 확인하기
                    </span>
                </h2>
            </div>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # ... (상단 배너 및 "서비스 확인하기" 영역은 유지) ...

   # 5. 버튼 영역 커스텀 스타일 및 배치
    st.markdown(
        """
        <style>
            /* 버튼 기본 스타일: 크기 1.2배 확대, 검은색 테두리, 연남색 배경 */
            div.stButton > button {
                width: 100%;
                height: auto !important;
                padding-top: 20px !important;    /* 상하 패딩 확대로 크기 키움 */
                padding-bottom: 20px !important;
                font-size: 24px !important;      /* 글자 크기 확대 */
                font-weight: bold !important;
                border: 3px solid #000000 !important; /* 선명한 검은색 테두리 */
                border-radius: 12px !important;
                
                /* 요청하신 연한 남색 배경색 */
                background-color: #b0c4de !important; 
                color: #000000 !important;           /* 검정색 글자 */
                
                transition: all 0.3s ease;
                box-shadow: 0 4px 10px rgba(0,0,0,0.15); /* 입체감을 위한 그림자 */
            }

            /* 버튼 마우스 호버 효과 */
            div.stButton > button:hover {
                /* 호버 시 배경색을 살짝 더 진하게 변경 */
                background-color: #a2b9d6 !important; 
                border-color: #000000 !important;
                transform: translateY(-3px); /* 위로 살짝 들리는 효과 */
                box-shadow: 0 6px 15px rgba(0,0,0,0.2);
            }

            /* 버튼 클릭 시 효과 */
            div.stButton > button:active {
                transform: translateY(-1px);
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 버튼 배치 (화면 중앙 정렬을 위해 컬럼 사용)
    container = st.container()
    with container:
        # 좌우 여백을 주어 버튼이 너무 퍼지지 않게 조절
        _, col_mid, _ = st.columns([1, 8, 1]) 
        with col_mid:
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🛫 항공 예약하기 전이에요.", use_container_width=True, key="main_btn_route"):
                    st.session_state.page = "route"
                    st.rerun()
            with c2:
                # 두 버튼 모두 동일한 스타일이 적용됩니다.
                if st.button("🛬 항공 예약 완료했어요!", use_container_width=True, key="main_btn_delay"):
                    st.session_state.page = "delay"
                    st.rerun()
    
    # 하단 여백 추가
    st.write("\n" * 5)