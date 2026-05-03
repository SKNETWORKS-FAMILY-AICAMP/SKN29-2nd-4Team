import streamlit as st
import pandas as pd
import os
import base64

def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def show_routeresult_page():
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

            /* === 커스텀 테이블 === */
            .custom-table {
                width: 100%;
                border-collapse: collapse;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0, 31, 63, 0.07);
                border: 1px solid #E8ECF2;
                font-size: 14px;
            }
            .custom-table thead tr {
                background: linear-gradient(90deg, #001f3f, #0057b8);
                color: white;
            }
            .custom-table thead th {
                padding: 16px 18px;
                text-align: center;
                font-weight: 700;
                font-size: 11px;
                letter-spacing: 1.5px;
                text-transform: uppercase;
            }
            .custom-table thead th:first-child {
                text-align: left;
            }
            .custom-table tbody tr {
                border-bottom: 1px solid #F0F2F6;
                transition: background-color 0.15s ease;
            }
            .custom-table tbody tr:last-child {
                border-bottom: none;
            }
            .custom-table tbody tr:hover {
                background-color: #EFF6FF;
            }
            .custom-table tbody tr:nth-child(even) {
                background-color: #FAFBFD;
            }
            .custom-table tbody tr:nth-child(even):hover {
                background-color: #EFF6FF;
            }
            .custom-table td {
                padding: 16px 18px;
                text-align: center;
                color: #374151;
            }
            .custom-table td:first-child {
                font-weight: 700;
                color: #001f3f;
                text-align: left;
            }

            /* 순위 뱃지 */
            .rank-badge {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                font-size: 11px;
                font-weight: 800;
                margin-right: 10px;
                flex-shrink: 0;
            }
            .rank-badge.rank-1 {
                background: linear-gradient(135deg, #F59E0B, #FBBF24);
                color: white;
                box-shadow: 0 2px 6px rgba(245, 158, 11, 0.4);
            }
            .rank-badge.rank-2 {
                background: linear-gradient(135deg, #6B7280, #9CA3AF);
                color: white;
                box-shadow: 0 2px 6px rgba(107, 114, 128, 0.3);
            }
            .rank-badge.rank-3 {
                background: linear-gradient(135deg, #B45309, #D97706);
                color: white;
                box-shadow: 0 2px 6px rgba(180, 83, 9, 0.3);
            }
            .rank-badge.rank-other {
                background: #E8ECF2;
                color: #6B7280;
            }

            /* 1등 행 강조 */
            .custom-table tbody tr.top-row {
                background-color: #FFFBEB !important;
            }
            .custom-table tbody tr.top-row:hover {
                background-color: #FEF3C7 !important;
            }

            /* 시간 뱃지 */
            .time-badge {
                display: inline-block;
                background: #F0F4FF;
                color: #001f3f;
                border-radius: 8px;
                padding: 3px 10px;
                font-size: 13px;
                font-weight: 700;
                letter-spacing: 0.3px;
            }

            /* 소요시간 pill */
            .duration-pill {
                display: inline-block;
                background: #D1FAE5;
                color: #065F46;
                border-radius: 20px;
                padding: 3px 12px;
                font-size: 12px;
                font-weight: 700;
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
                    <h1 style="font-size: 40px; margin: 0; font-weight: 900; letter-spacing: -1.5px; color: white;">맞춤형 노선 추천</h1>
                    <div style="width: 40px; height: 2px; background: rgba(255,255,255,0.7); margin: 18px auto;"></div>
                    <p style="font-size: 16px; line-height: 1.7; font-weight: 300; opacity: 0.9; margin: 0;">
                        입력하신 정보를 바탕으로 분석한 최적의 항공 노선입니다.
                    </p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # === 결과 테이블 ===
    st.markdown("<div class='section-heading'>✅ 추천 노선 목록</div>", unsafe_allow_html=True)

    data = {
        "항공사명": ["대한항공", "델타항공", "아시아나", "유나이티드", "아메리칸항공"],
        "출발지": ["인천(ICN)", "인천(ICN)", "인천(ICN)", "인천(ICN)", "인천(ICN)"],
        "출발시간": ["10:30", "14:20", "17:40", "09:15", "11:50"],
        "도착지": ["LAX", "LAX", "LAX", "LAX", "LAX"],
        "도착시간": ["05:10", "09:00", "12:20", "04:00", "06:40"],
        "소요시간": ["10h 40m", "10h 40m", "10h 40m", "10h 45m", "10h 50m"]
    }
    df = pd.DataFrame(data)

    rank_classes = ["rank-1", "rank-2", "rank-3", "rank-other", "rank-other"]

    rows_html = ""
    for i, row in df.iterrows():
        row_class = "top-row" if i == 0 else ""
        badge_class = rank_classes[i] if i < len(rank_classes) else "rank-other"
        rows_html += (
            f"<tr class='{row_class}'>"
            f"<td><span class='rank-badge {badge_class}'>{i+1}</span>{row['항공사명']}</td>"
            f"<td>{row['출발지']}</td>"
            f"<td><span class='time-badge'>{row['출발시간']}</span></td>"
            f"<td>{row['도착지']}</td>"
            f"<td><span class='time-badge'>{row['도착시간']}</span></td>"
            f"<td><span class='duration-pill'>{row['소요시간']}</span></td>"
            "</tr>"
        )

    table_html = (
        "<table class='custom-table'>"
        "<thead><tr>"
        "<th>항공사명</th><th>출발지</th><th>출발시간</th>"
        "<th>도착지</th><th>도착시간</th><th>소요시간</th>"
        "</tr></thead>"
        "<tbody>" + rows_html + "</tbody>"
        "</table>"
    )
    st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("<div style='height: 20px'></div>", unsafe_allow_html=True)

    # === 안내 문구 ===
    st.info("💡 위 노선은 기상 데이터와 과거 지연 데이터를 분석하여 추천된 순서입니다.")

    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

    # === 다시 검색 버튼 ===
    if st.button("🔄 다시 검색하기", use_container_width=True, type="primary"):
        st.session_state.page = "route"
        st.rerun()

    st.markdown("<div style='height: 60px'></div>", unsafe_allow_html=True)
