import streamlit as st
import os
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def show_main_page():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(current_dir, "../resource", "airport.jpg")

    # --- 카드 클릭 최적화 및 레이아웃 CSS ---
    st.markdown(
        """
        <style>
            /* 1. 전체 컨테이너 패딩 완전 제거 */
            [data-testid="stAppViewBlockContainer"] {
                max-width: 100% !important;
                padding: 0rem !important;
                margin: 0rem !important;
            }

            /* 2. 상단 헤더 투명화 */
            [data-testid="stHeader"] {
                background-color: rgba(0,0,0,0);
            }

            /* 3. 배너 설정 */
            .full-width-banner {
                width: 100% !important;
                margin: 0 !important;
                padding: 0 !important;
            }

            /* 4. 카드 섹션 전용 여백 */
            .main-content-wrapper {
                padding: 0 10% 50px 10%;
                margin-top: 50px;
            }

            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .banner-text { animation: fadeInUp 1s ease-out; }

            /* 5. 서비스 카드 디자인 (클릭 가능 피드백 추가) */
            .service-card {
                background-color: white;
                border-radius: 20px;
                padding: 35px 25px;
                text-align: center;
                box-shadow: 0 10px 30px rgba(0,0,0,0.05);
                transition: all 0.3s ease;
                border: 1px solid #eee;
                height: 300px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                cursor: pointer; /* 마우스 포인터 변경 */
            }
            
            .service-card:hover {
                transform: translateY(-10px);
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                border-color: #001f3f;
            }

            /* 버튼 스타일링 (카드와 조화롭게) */
            .stButton > button {
                width: 100%;
                border-radius: 12px;
                border: 1px solid #eee;
                background-color: white;
                color: #001f3f;
                font-weight: 600;
            }
            
            .stButton > button:hover {
                border-color: #001f3f;
                color: #001f3f;
                background-color: #f8f9fa;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # --- 카드 클릭 시 페이지 이동을 위한 JavaScript 추가 ---
    st.markdown(
        """
        <script>
            // 카드 클릭 시 해당 링크로 이동하는 함수
            function navigateTo(page) {
                // Streamlit의 멀티페이지 구조에서 파일명을 직접 호출
                window.parent.location.assign(window.parent.location.origin + '/' + page);
            }
        </script>
        """,
        unsafe_allow_html=True
    )

    # 히어로 배너 영역
    if os.path.exists(img_path):
        img_base64 = get_base64_of_bin_file(img_path)
        st.markdown(
            f"""
            <div class="full-width-banner" style="
                height: 410px;
                background-image: linear-gradient(rgba(0, 31, 63, 0.5), rgba(0, 31, 63, 0.5)), url('data:image/jpg;base64,{img_base64}');
                background-size: cover;
                background-position: center;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                color: white;
            ">
                <div class="banner-text">
                    <h1 style="font-size: 65px; margin: 0; font-weight: 900; letter-spacing: -2px;">SKY CASTER</h1>
                    <div style="width: 60px; height: 3px; background: #ffffff; margin: 20px auto;"></div>
                    <p style="font-size: 20px; line-height: 1.6; font-weight: 300; opacity: 0.95;">
                        실시간 기상 데이터를 분석하여<br>
                        당신의 여정에 가장 안전하고 정확한 항로를 제안합니다.
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 서비스 선택 섹션
    st.markdown('<div class="main-content-wrapper">', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 40px;">
            <p style="color: #007bff; font-weight: 700; font-size: 13px; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px;">Select Service</p>
            <h2 style="font-size: 32px; color: #001f3f; font-weight: 800;">어떤 도움이 필요하신가요?</h2>
        </div>
        """, 
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5 = st.columns([0.5, 4, 1, 4, 0.5])

    # 1. 최적 노선 분석 카드 (onclick 이벤트 추가)
    with col2:
        st.markdown("""
            <div class="service-card" onclick="window.parent.location.assign(window.parent.location.href + 'route')">
                <div style="font-size: 45px; margin-bottom: 15px;">🛫</div>
                <div style="font-size: 22px; font-weight: 700; color: #001f3f; margin-bottom: 12px;">최적 노선 분석</div>
                <div style="font-size: 15px; color: #666; line-height: 1.5;">
                    출발 전, 기상 상황을 고려하여<br>지연 가능성이 가장 낮은 노선을 추천합니다.
                </div>
            </div>
        """, unsafe_allow_html=True)
        # 버튼 클릭 시 페이지 이동
        if st.button("노선 확인하기", key="main_btn_route", use_container_width=True):
            st.session_state.page = "route"
            st.rerun()

    # 2. 지연 시간 예측 카드 (onclick 이벤트 추가)
    with col4:
        st.markdown("""
            <div class="service-card" onclick="window.parent.location.assign(window.parent.location.href + 'delay')">
                <div style="font-size: 45px; margin-bottom: 15px;">🛬</div>
                <div style="font-size: 22px; font-weight: 700; color: #001f3f; margin-bottom: 12px;">지연 여부 예측</div>
                <div style="font-size: 15px; color: #666; line-height: 1.5;">
                    이미 예약한 항공편이 있다면,<br>현재 기상 조건에 따른 도착 시간을 예측합니다.
                </div>
            </div>
        """, unsafe_allow_html=True)
        # 버튼 클릭 시 페이지 이동
        if st.button("지연 예측하기", key="main_btn_delay", use_container_width=True):
            st.session_state.page = "delay"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # 푸터 영역
    st.markdown(
        """
        <div style="text-align: center; margin-top: 30px; padding-bottom: 40px; color: #aaa; font-size: 13px;">
            © 2026 SKY CASTER. All Rights Reserved.
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    show_main_page()