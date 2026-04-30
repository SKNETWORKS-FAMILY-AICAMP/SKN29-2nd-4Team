import streamlit as st
import pandas as pd
import numpy as np

def update_days():
    # 슬라이더 값이 변경되면 즉시 세션 상태를 업데이트하는 콜백 함수
    st.session_state.sim_days = st.session_state.temp_slider

def show_model_page():
    # 세션 상태 초기화
    if 'sim_days' not in st.session_state:
        st.session_state.sim_days = 10

    # 1. 상단 내비게이션
    if st.button("🏠 메인으로"):
        st.session_state.page = "main"
        st.rerun()

    # --- 1. 제목 영역 ---
    st.markdown(
        """
        <div style="text-align: left; padding-top: 10px; padding-bottom: 20px;">
            <h1 style="font-size: 36px;">Online Learning 시뮬레이션</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )

    # 현재 설정된 누적 일수 가져오기[cite: 1]
    accumulated_days = st.session_state.sim_days

    # --- 데이터 계산 로직 (멘트에 노출될 수치 계산) ---
    # 학습 데이터가 늘어남에 따라 줄어드는 평균 오차율 시뮬레이션
    base_avg_error = max(15, 45 - (accumulated_days // 10) * 3) # 기존 오차율
    updated_avg_error = base_avg_error * 0.45 # 업데이트 후 오차율

    # --- 2. 데이터 오차 및 모델 업데이트 후 표(그래프) ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 샘플 데이터 오차")
        base_error = [45, 38, 52, 41]
        improvement = (accumulated_days // 10) * 3
        current_error = [max(10, x - improvement + np.random.randint(-1, 2)) for x in base_error]
        
        error_df = pd.DataFrame({
            '지표': ['기온 오차', '습도 오차', '풍속 오차', '지연 오차'],
            '오차율(%)': current_error
        })
        st.bar_chart(error_df.set_index('지표'), color="#ff4b4b")
        st.caption(f"{accumulated_days}일 누적 데이터 기반 오차")

    with col2:
        st.subheader("📈 업데이트 후")
        after_error = [x * 0.45 for x in current_error]
        
        updated_df = pd.DataFrame({
            '지표': ['기온 오차', '습도 오차', '풍속 오차', '지연 오차'],
            '오차율(%)': after_error
        })
        st.bar_chart(updated_df.set_index('지표'), color="#29b5e8")
        st.caption("실시간 업데이트(Online Learning) 결과")

    # --- 3. 분석 결과 멘트 (요청하신 포맷으로 수정) ---
    st.write("\n")
    st.success(f"💡 **분석 결과:** 학습 데이터가 **{accumulated_days}**일로 확장됨에 따라 오차율이 **{base_avg_error}**%에서 **{updated_avg_error:.1f}**%로 변경되었습니다.")
    
    st.write("\n" * 2)

    # --- 4. 학습 데이터 기간 확장 및 현재 학습 범위 ---
    st.markdown("### 📅 학습 데이터 기간 확장")
    
    # 조절바 (10일 단위)[cite: 1]
    st.slider(
        "슬라이더를 움직여 학습 데이터의 범위를 조절하세요.", 
        min_value=10, 
        max_value=100, 
        value=st.session_state.sim_days, 
        step=10,
        key="temp_slider",
        on_change=update_days
    )

    # 날짜 범위 계산 및 표시
    start_date = "2026-05-01"
    if accumulated_days <= 31:
        end_date = f"2026-05-{accumulated_days:02d}"
    else:
        end_date = f"2026-06-{accumulated_days-31:02d}"

    st.markdown(
        f"""
        <div style="background-color: #f0f2f6; padding: 15px;">
            <strong>📍 현재 학습 범위:</strong> {start_date} ~ {end_date} (총 {accumulated_days}일간의 데이터 학습 중)
        </div>
        """, 
        unsafe_allow_html=True
    )

    st.write("\n" * 5)