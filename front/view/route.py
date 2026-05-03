import streamlit as st
import os
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def show_route_page():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(current_dir, "../resource", "airport.jpg")

    st.markdown(
        """
        <style>
            /* === 전체 배경 및 컨테이너 === */
            [data-testid="stAppViewBlockContainer"] {
                max-width: 860px !important;
                padding: 0 2rem 4rem !important;
                margin: 0 auto !important;
            }

            /* 배너는 컨테이너 밖으로 full-width 처리 */
            .route-banner-outer {
                width: 100vw;
                position: relative;
                left: 50%;
                right: 50%;
                margin-left: -50vw;
                margin-right: -50vw;
                margin-bottom: 36px;
            }

            /* === 버튼 === */
            div.stButton > button[kind="primary"] {
                background-color: #001f3f !important;
                color: white !important;
                border: none !important;
                border-radius: 10px !important;
                font-weight: 600 !important;
                font-size: 15px !important;
                padding: 0.75rem 1rem !important;
                letter-spacing: 0.02em !important;
                transition: background-color 0.2s ease !important;
            }
            div.stButton > button[kind="primary"]:hover {
                background-color: #003366 !important;
            }

            /* === 멀티셀렉트 태그 === */
            span[data-baseweb="tag"] {
                background-color: #001f3f !important;
                color: white !important;
                border-radius: 6px !important;
            }

            /* === selectbox / multiselect 테두리 === */
            [data-baseweb="select"] > div {
                border-radius: 10px !important;
                border-color: #D1D9E6 !important;
                transition: border-color 0.2s ease;
            }
            [data-baseweb="select"] > div:focus-within {
                border-color: #001f3f !important;
                box-shadow: 0 0 0 2px rgba(0, 31, 63, 0.1) !important;
            }

            /* === 섹션 헤딩 === */
            .section-heading {
                font-size: 15px;
                font-weight: 700;
                color: #001f3f;
                margin: 32px 0 16px;
                padding-bottom: 10px;
                border-bottom: 1px solid #EAECF0;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .card-title-badge {
                background: linear-gradient(90deg, #001f3f, #0057b8);
                color: white;
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 1px;
            }

            .field-label {
                font-size: 12px;
                font-weight: 700;
                color: #6B7280;
                letter-spacing: 0.8px;
                text-transform: uppercase;
                margin-bottom: 8px;
            }

            /* 화살표 구분자 */
            .route-arrow {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100%;
                padding-top: 28px;
            }
            .route-arrow-inner {
                width: 36px;
                height: 36px;
                background: linear-gradient(135deg, #001f3f, #0057b8);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 16px;
                box-shadow: 0 4px 12px rgba(0, 31, 63, 0.25);
            }

            /* 출발/도착 라벨 칩 */
            .airport-chip {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: #F0F4FF;
                border: 1px solid #DBEAFE;
                border-radius: 20px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: 700;
                color: #1E40AF;
                margin-bottom: 10px;
                letter-spacing: 0.5px;
            }

            /* 옵션 번호 뱃지 */
            .opt-badge {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 20px;
                height: 20px;
                background: #001f3f;
                color: white;
                border-radius: 50%;
                font-size: 10px;
                font-weight: 800;
                margin-right: 6px;
                flex-shrink: 0;
            }
            .opt-label {
                font-size: 12px;
                font-weight: 700;
                color: #374151;
                display: flex;
                align-items: center;
                margin-bottom: 8px;
            }
            .opt-sub {
                font-size: 11px;
                color: #9CA3AF;
                font-weight: 400;
                margin-left: 4px;
            }

            /* 배너 텍스트 애니메이션 */
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .banner-text { animation: fadeInUp 1s ease-out; }
        </style>
        """,
        unsafe_allow_html=True
    )

    # === 히어로 배너 ===
    if os.path.exists(img_path):
        img_base64 = get_base64_of_bin_file(img_path)
        bg = f"linear-gradient(rgba(0, 31, 63, 0.5), rgba(0, 31, 63, 0.5)), url('data:image/jpg;base64,{img_base64}')"
    else:
        bg = "linear-gradient(rgba(0, 31, 63, 0.8), rgba(0, 31, 63, 0.8))"

    st.markdown(
        f"""
        <div class="route-banner-outer">
            <div style="
                height: 280px;
                background-image: {bg};
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
                    <h1 style="font-size: 40px; margin: 0; font-weight: 900; letter-spacing: -1.5px; color: white;">행복한 여행을 위한<br>최적의 노선 확인하기</h1>
                    <div style="width: 40px; height: 2px; background: rgba(255,255,255,0.7); margin: 18px auto;"></div>
                    <p style="font-size: 16px; line-height: 1.7; font-weight: 300; opacity: 0.9; margin: 0;">
                        기상 데이터를 기반으로 지연 가능성이 가장 낮은 항로를 분석합니다.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 데이터 리스트
    korea_airports = ["선택해주세요", "인천(ICN)", "김포(GMP)", "김해(PUS)", "제주(CJU)", "대구(TAE)", "청주(CJJ)"]
    usa_airports = ["선택해주세요", "로스앤젤레스(LAX)", "뉴욕(JFK)", "샌프란시스코(SFO)", "시카고(ORD)", "시애틀(SEA)", "호놀룰루(HNL)"]
    airline_list = [
        "대한항공 (Korean Air)", "아시아나항공 (Asiana Airlines)",
        "델타항공 (Delta Air Lines)", "유나이티드항공 (United Airlines)",
        "아메리칸항공 (American Airlines)", "에어프레미아 (Air Premia)",
        "하와이안항공 (Hawaiian Airlines)", "일본항공 (JAL)",
        "전일본공수 (ANA)", "에어캐나다 (Air Canada)", "캐세이퍼시픽 (Cathay Pacific)"
    ]
    dep_time_options = ["출발 시각"] + [f"{i:02d}:00 이후" for i in range(24)]
    arr_time_options = ["도착 시각"] + [f"{i:02d}:00 이후" for i in range(24)]

    # === 섹션 1: 필수 입력 ===
    st.markdown(
        """
        <div class="section-heading">
            ✅ &nbsp;필수 입력 사항
        </div>
        """,
        unsafe_allow_html=True
    )

    col_dep, col_arrow, col_arr = st.columns([5, 1, 5])
    with col_dep:
        st.markdown("<div class='airport-chip'>🛫 &nbsp;출발지 · 한국</div>", unsafe_allow_html=True)
        dep_airport = st.selectbox("출발지_hidden", options=korea_airports, label_visibility="collapsed", key="sel_dep")
    with col_arrow:
        st.markdown(
            """
            <div class="route-arrow">
                <div class="route-arrow-inner">→</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col_arr:
        st.markdown("<div class='airport-chip'>🛬 &nbsp;목적지 · 미국</div>", unsafe_allow_html=True)
        arr_airport = st.selectbox("목적지_hidden", options=usa_airports, label_visibility="collapsed", key="sel_arr")

    st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

    # === 섹션 2: 추가 입력 ===
    st.markdown(
        """
        <div class="section-heading">
            ➕ &nbsp;추가 입력 사항
        </div>
        """,
        unsafe_allow_html=True
    )

    opt_col1, opt_col2 = st.columns(2)

    with opt_col1:
        st.markdown(
            "<div class='opt-label'><span class='opt-badge'>1</span>선호 항공사<span class='opt-sub'>중복 선택 가능</span></div>",
            unsafe_allow_html=True
        )
        selected_airlines = st.multiselect(
            "항공사_hidden",
            options=airline_list,
            placeholder="항공사를 검색하거나 선택하세요",
            label_visibility="collapsed",
            key="opt_1_multi"
        )

    with opt_col2:
        st.markdown(
            "<div class='opt-label'><span class='opt-badge'>2</span>선호 시간대</div>",
            unsafe_allow_html=True
        )
        time_col1, time_col2 = st.columns(2)
        with time_col1:
            pref_dep_time = st.selectbox("출발시간_hidden", options=dep_time_options, label_visibility="collapsed", key="opt_time_dep")
        with time_col2:
            pref_arr_time = st.selectbox("도착시간_hidden", options=arr_time_options, label_visibility="collapsed", key="opt_time_arr")

    st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)

    # === 분석 버튼 ===
    if st.button("🚀 최적의 노선 분석 시작하기", use_container_width=True, type="primary"):
        if dep_airport != "선택해주세요" and arr_airport != "선택해주세요":
            st.session_state.page = "routeload"
            st.rerun()
        else:
            st.error("출발지와 목적지를 목록에서 선택해 주세요!")
