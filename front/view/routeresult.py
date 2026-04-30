import streamlit as st
import pandas as pd

def show_routeresult_page():
    # 1. 상단 영역: 메인으로 돌아가기 버튼
    if st.button("🏠 메인으로"):
        st.session_state.page = "main"
        st.rerun()

    # 2. 타이틀 영역 (중앙 정렬)
    st.markdown(
        """
        <div style="text-align: center; padding-top: 20px; padding-bottom: 30px;">
            <h1 style="font-size: 40px;">📊 맞춤형 노선 추천</h1>
            <p style="color: #666; font-size: 18px;">입력하신 정보를 바탕으로 분석한 최적의 항공 노선입니다.</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # 3. 데이터 테이블 영역 (구성안에 있는 컬럼 반영)
    # 실제 데이터가 연결되기 전까지 보여줄 샘플 데이터입니다.
    # ==================================================
    # /api/reservation-rank 활용
    # ==================================================
    data = {
        "항공사명": ["대한항공", "델타항공", "아시아나", "유나이티드", "아메리칸항공"],
        "출발지": ["인천(ICN)", "인천(ICN)", "인천(ICN)", "인천(ICN)", "인천(ICN)"],
        "출발시간": ["10:30", "14:20", "17:40", "09:15", "11:50"],
        "도착지": ["LAX", "LAX", "LAX", "LAX", "LAX"],
        "도착시간": ["05:10", "09:00", "12:20", "04:00", "06:40"],
        "소요시간": ["10h 40m", "10h 40m", "10h 40m", "10h 45m", "10h 50m"]
    }

    df = pd.DataFrame(data)

    # 테이블을 화면에 출력 (중앙 배치를 위해 컬럼 활용)
    # 테이블은 전체 너비를 사용하게 하거나, 가독성을 위해 살짝 조절할 수 있습니다.
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("\n" * 2)

    # 4. 하단 안내 문구
    st.info("💡 위 노선은 기상 데이터와 과거 지연 데이터를 분석하여 추천된 순서입니다.")

    # 다시 검색하기 버튼
    if st.button("🔄 다시 검색하기", use_container_width=True):
        st.session_state.page = "route"
        st.rerun()

    st.write("\n" * 5)