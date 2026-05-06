import streamlit as st
import os
import base64

from front.data import get_check_my_reservation

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def show_delayresult_page():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(current_dir, "../resource", "airport.jpg")

    st.markdown(
        """
        <style>
            /* === 컨테이너 === */
            [data-testid="stAppViewBlockContainer"] {
                max-width: 900px !important;
                padding: 0 2rem 4rem !important;
                margin: 0 auto !important;
            }

            /* === 뒤로가기 버튼 (secondary) === */
            [data-testid="stMainBlockContainer"] div.stButton > button[kind="secondary"] {
                background-color: white !important;
                color: #001f3f !important;
                border: 1.5px solid #D1D9E6 !important;
                border-radius: 10px !important;
                font-weight: 600 !important;
                font-size: 13px !important;
                transition: all 0.2s ease !important;
            }
            [data-testid="stMainBlockContainer"] div.stButton > button[kind="secondary"]:hover {
                border-color: #001f3f !important;
                background-color: #f8f9fb !important;
            }

            /* === 다시 검색 버튼 (primary) === */
            div.stButton > button[kind="primary"] {
                background-color: #001f3f !important;
                color: white !important;
                border: none !important;
                border-radius: 10px !important;
                font-weight: 600 !important;
                font-size: 15px !important;
                padding: 0.75rem 1rem !important;
                transition: background-color 0.2s ease !important;
            }
            div.stButton > button[kind="primary"]:hover {
                background-color: #003366 !important;
            }

            /* === info 박스 === */
            [data-testid="stAlert"] {
                border-radius: 12px !important;
                border: 1px solid #DBEAFE !important;
                background-color: #EFF6FF !important;
                color: #1E40AF !important;
                font-size: 14px !important;
            }

            /* === 배너 full-width === */
            .result-banner-outer {
                width: 100vw;
                position: relative;
                left: 50%;
                right: 50%;
                margin-left: -50vw;
                margin-right: -50vw;
                margin-bottom: 20px;
            }

            /* 배너 텍스트 애니메이션 */
            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .banner-text { animation: fadeInUp 1s ease-out; }

            /* === 섹션 헤딩 === */
            .section-heading {
                font-size: 15px;
                font-weight: 700;
                color: #001f3f;
                margin: 28px 0 16px;
                padding-bottom: 10px;
                border-bottom: 1px solid #EAECF0;
            }

            /* === 상단 네비 === */
            .top-nav {
                padding: 20px 0 0;
            }

            /* === 커스텀 metric 카드 === */
            .metric-card {
                background: white;
                border: 1px solid #E8ECF2;
                border-radius: 16px;
                padding: 28px 28px 24px;
                box-shadow: 0 4px 20px rgba(0, 31, 63, 0.07);
                position: relative;
                overflow: hidden;
            }
            .metric-card::before {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0;
                height: 4px;
                background: linear-gradient(90deg, #001f3f, #0057b8);
                border-radius: 16px 16px 0 0;
            }
            .metric-card-label {
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                color: #9CA3AF;
                margin-bottom: 14px;
            }
            .metric-card-value {
                font-size: 42px;
                font-weight: 900;
                color: #001f3f;
                letter-spacing: -1.5px;
                line-height: 1;
                margin-bottom: 14px;
            }
            .metric-badge {
                display: inline-flex;
                align-items: center;
                gap: 5px;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
            }
            .metric-badge.warn {
                background: #FEF3C7;
                color: #B45309;
            }
            .metric-badge.good {
                background: #D1FAE5;
                color: #065F46;
            }

            /* === 현지 정보 통합 카드 === */
            .local-info-card {
                display: flex;
                background: white;
                border: 1px solid #E8ECF2;
                border-radius: 16px;
                box-shadow: 0 4px 20px rgba(0, 31, 63, 0.07);
                overflow: hidden;
            }
            .local-info-weather {
                background: linear-gradient(160deg, #EFF6FF 0%, #DBEAFE 100%);
                padding: 36px 28px;
                text-align: center;
                min-width: 180px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                border-right: 1px solid #DBEAFE;
            }
            .wi-emoji {
                font-size: 72px;
                line-height: 1;
                display: block;
                margin-bottom: 14px;
                filter: drop-shadow(0 4px 8px rgba(0,0,0,0.1));
            }
            .wi-label {
                font-size: 16px;
                font-weight: 800;
                color: #001f3f;
                letter-spacing: -0.3px;
            }
            .wi-sublabel {
                font-size: 11px;
                color: #6B7280;
                margin-top: 5px;
                font-weight: 500;
            }
            .local-info-rows {
                padding: 8px 28px;
                flex: 1;
                display: flex;
                flex-direction: column;
                justify-content: center;
            }
            .info-row {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 13px 0;
                border-bottom: 1px solid #F3F4F6;
                font-size: 14px;
                color: #374151;
            }
            .info-row:last-child { border-bottom: none; }
            .info-row-label {
                font-weight: 700;
                color: #001f3f;
                min-width: 110px;
                flex-shrink: 0;
                font-size: 13px;
            }
            .info-row-value { color: #374151; font-size: 14px; }
            .info-row-value.highlight {
                color: #065F46;
                font-weight: 600;
                background: #D1FAE5;
                padding: 3px 10px;
                border-radius: 20px;
                font-size: 13px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    # === 상단 뒤로가기 버튼 ===
    st.markdown("<div class='top-nav'>", unsafe_allow_html=True)
    if st.button("← 메인으로"):
        st.session_state.page = "main"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # === 히어로 배너 ===
    if os.path.exists(img_path):
        img_base64 = get_base64_of_bin_file(img_path)
        bg = f"linear-gradient(rgba(0, 31, 63, 0.5), rgba(0, 31, 63, 0.5)), url('data:image/jpg;base64,{img_base64}')"
    else:
        bg = "linear-gradient(rgba(0, 31, 63, 0.8), rgba(0, 31, 63, 0.8))"

    st.markdown(
        f"""
        <div class="result-banner-outer">
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
                    <h1 style="font-size: 40px; margin: 0; font-weight: 900; letter-spacing: -1.5px; color: white;">지연 분석 결과</h1>
                    <div style="width: 40px; height: 2px; background: rgba(255,255,255,0.7); margin: 18px auto;"></div>
                    <p style="font-size: 16px; line-height: 1.7; font-weight: 300; opacity: 0.9; margin: 0;">
                        입력하신 항공편의 분석된 지연 정보와 현지 상황입니다.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # === 핵심 요약 ===
    st.markdown("<div class='section-heading'>✅ 지연 예측 요약</div>", unsafe_allow_html=True)
    
    data = get_check_my_reservation()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-label">⏳ &nbsp;예상 지연 시간</div>
                <div class="metric-card-value">{data.get("delay")}</div>
            </div>
            """,
            # <span class="metric-badge warn">▲ 평균 대비 +5분</span>
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-card-label">📊 &nbsp;지연 발생 확률</div>
                <div class="metric-card-value">{data.get("proba")*100:.2f}%</div>
            </div>
            """,
            # <span class="metric-badge good">✔ 지연 가능성 낮음</span>
            unsafe_allow_html=True
        )

    # === 현지 도착지 정보 ===
    st.markdown("<div class='section-heading'>🇺🇸 도착지 현지 정보</div>", unsafe_allow_html=True)

    wdata = weather_data(data)
    st.markdown(
        f"""
        <div class="local-info-card">
            <div class="local-info-weather">
                <span class="wi-emoji">{wdata.get("w_emoji")}</span>
                <div class="wi-label">{wdata.get("weather_ko")}</div>
                <div class="wi-sublabel">현지 기상 상태</div>
            </div>
            <div class="local-info-rows">
                <div class="info-row">
                    <span class="info-row-label">📍 목적지</span>
                    <span class="info-row-value">{wdata.get("airport_name")}</span>
                </div>
                <div class="info-row">
                    <span class="info-row-label">🌡️ 현재 기온</span>
                    <span class="info-row-value">{wdata.get("temperature")}°C</span>
                </div>
                <div class="info-row">
                    <span class="info-row-label">💨 풍속</span>
                    <span class="info-row-value">{wdata.get("wind")}m/s</span>
                </div>
            </div>
        </div>
        """,
        # <div class="info-row">
        #     <span class="info-row-label">📢 현지 알림</span>
        #     <span class="info-row-value highlight">기상 상태 양호 · 운항 원활 예상</span>
        # </div>
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

    # === 안내 문구 ===
    st.info("💡 위 결과는 실시간 기상 데이터와 과거 운항 기록을 바탕으로 예측된 정보입니다.")

    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

    # === 다시 검색 버튼 ===
    if st.button("🔄 다른 항공편 확인하기", use_container_width=True, type="primary"):
        st.session_state.page = "delay"
        st.rerun()

    st.markdown("<div style='height: 60px'></div>", unsafe_allow_html=True)

def weather_data(data):
    wdata = data.get("weather")
    if wdata.get("weather") == 'sunny':
        w_emoji = '☀️'
        weather_ko = '맑음'
    elif wdata.get("weather") == 'cloudy':
        w_emoji = "☁️"
        weather_ko = '흐림'
    elif wdata.get("weather") == 'rainy':
        w_emoji = '🌧️'
        weather_ko = '비'
    elif wdata.get("weather") == 'snowy':
        w_emoji = '❄️'
        weather_ko = '눈'
    return {
        "w_emoji": w_emoji,
        "weather_ko": weather_ko,
        "airport_name": wdata.get("airport"),
        "temperature": float(wdata.get("temperature")),
        "wind": float(wdata.get("wind")),
    }