import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 앱 설정 ---
st.set_page_config(page_title="식후 혈당 모니터링", page_icon="🩸")

st.title("🩸 식후 혈당 변화 그래프 (30분 단위)")
st.markdown("식사 시작 후 30분 간격으로 측정한 혈당 수치를 입력하세요.")

# --- 사이드바: 데이터 입력 ---
st.sidebar.header("수치 입력 (mg/dL)")

def user_input_features():
    fasting = st.sidebar.number_input("식전 (공복)", min_value=0, max_value=600, value=95)
    min_30 = st.sidebar.number_input("식후 30분", min_value=0, max_value=600, value=140)
    min_60 = st.sidebar.number_input("식후 1시간 (60분)", min_value=0, max_value=600, value=160)
    min_90 = st.sidebar.number_input("식후 1시간 30분 (90분)", min_value=0, max_value=600, value=130)
    min_120 = st.sidebar.number_input("식후 2시간 (120분)", min_value=0, max_value=600, value=110)
    min_150 = st.sidebar.number_input("식후 2시간 30분 (150분)", min_value=0, max_value=600, value=100)
    min_180 = st.sidebar.number_input("식후 3시간 (180분)", min_value=0, max_value=600, value=95)
    
    data = {
        '시간(분)': [0, 30, 60, 90, 120, 150, 180],
        '혈당(mg/dL)': [fasting, min_30, min_60, min_90, min_120, min_150, min_180]
    }
    return pd.DataFrame(data)

df = user_input_features()

# --- 메인 화면: 데이터 표시 ---
st.subheader("📊 입력된 데이터")
st.dataframe(df.set_index('시간(분)').T)

# --- 그래프 그리기 (Plotly 사용) ---
st.subheader("📈 혈당 변화 추이")

fig = go.Figure()

# 1. 사용자 혈당 라인
fig.add_trace(go.Scatter(
    x=df['시간(분)'], 
    y=df['혈당(mg/dL)'],
    mode='lines+markers+text',
    name='내 혈당',
    text=df['혈당(mg/dL)'],
    textposition="top center",
    line=dict(color='#FF4B4B', width=3),
    marker=dict(size=8)
))

# 2. 정상 혈당 참고선 (식후 2시간 140 미만 권장)
fig.add_shape(
    type="line",
    x0=0, y0=140, x1=180, y1=140,
    line=dict(color="Green", width=2, dash="dash"),
)
fig.add_annotation(
    x=10, y=145, text="관리 목표 (140 mg/dL)", showarrow=False, font=dict(color="green")
)

# 그래프 레이아웃 설정
fig.update_layout(
    xaxis_title="식사 후 경과 시간 (분)",
    yaxis_title="혈당 수치 (mg/dL)",
    yaxis_range=[50, max(df['혈당(mg/dL)']) + 30],
    template="plotly_white"
)

st.plotly_chart(fig, use_container_width=True)

# --- 분석 코멘트 ---
st.divider()
peak_glucose = df['혈당(mg/dL)'].max()
peak_time = df.loc[df['혈당(mg/dL)'].idxmax(), '시간(분)']

st.info(f"💡 **분석 결과:**\n"
        f"- 최고 혈당은 **식후 {peak_time}분**에 **{peak_glucose} mg/dL** 였습니다.\n"
        f"- 일반적으로 혈당 스파이크를 막기 위해서는 완만한 곡선을 유지하는 것이 좋습니다.")