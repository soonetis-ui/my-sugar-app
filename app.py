import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------------------------------------
# 1. 앱 기본 설정
# ---------------------------------------------------------
st.set_page_config(page_title="식후 혈당 다이어리", page_icon="📝", layout="wide")

st.title("📝 식후 혈당 & 식단 기록장")
st.markdown("오늘 먹은 음식과 시간대별 혈당 변화를 기록하고 그래프로 확인하세요.")

# ---------------------------------------------------------
# 2. 사이드바: 데이터 입력 (날짜, 음식, 혈당)
# ---------------------------------------------------------
st.sidebar.header("✏️ 기록 입력")

# [날짜 및 음식 입력]
record_date = st.sidebar.date_input("날짜 선택", datetime.now())
food_menu = st.sidebar.text_area(
    "섭취한 음식 (메뉴)", 
    placeholder="예: 현미밥 1/2공기, 닭가슴살 샐러드, 아몬드 5알",
    height=100
)

st.sidebar.markdown("---")
st.sidebar.subheader("🩸 혈당 수치 입력 (mg/dL)")

# [혈당 수치 입력 함수]
def user_input_features():
    # 슬라이더나 숫자 입력칸을 통해 수치를 받습니다.
    fasting = st.sidebar.number_input("식전 (공복)", 0, 600, 95)
    min_30  = st.sidebar.number_input("식후 30분", 0, 600, 140)
    min_60  = st.sidebar.number_input("식후 1시간", 0, 600, 160)
    min_90  = st.sidebar.number_input("식후 1시간 30분", 0, 600, 140)
    min_120 = st.sidebar.number_input("식후 2시간", 0, 600, 120)
    min_150 = st.sidebar.number_input("식후 2시간 30분", 0, 600, 110)
    min_180 = st.sidebar.number_input("식후 3시간", 0, 600, 100)
    
    # 데이터프레임(표) 형태로 만듭니다.
    data = {
        '시간(분)': [0, 30, 60, 90, 120, 150, 180],
        '혈당(mg/dL)': [fasting, min_30, min_60, min_90, min_120, min_150, min_180]
    }
    return pd.DataFrame(data)

# 입력받은 데이터를 변수 df에 저장
df = user_input_features()

# ---------------------------------------------------------
# 3. 메인 화면: 기록 요약 정보 표시
# ---------------------------------------------------------
st.divider()

# 화면을 2단으로 나누어 보여줍니다.
col1, col2 = st.columns([1, 2])

with col1:
    st.info(f"📅 **날짜**\n\n{record_date.strftime('%Y년 %m월 %d일')}")

with col2:
    # 음식이 입력되었는지 확인하고 표시
    if food_menu.strip():
        display_food = food_menu
        style = "success" # 초록색 상자
    else:
        display_food = "(아직 메뉴가 입력되지 않았습니다)"
        style = "warning" # 노란색 상자
        
    if style == "success":
        st.success(f"🍽️ **섭취한 음식**\n\n{display_food}")
    else:
        st.warning(f"🍽️ **섭취한 음식**\n\n{display_food}")

# ---------------------------------------------------------
# 4. 그래프 그리기 (Plotly)
# ---------------------------------------------------------
st.subheader("📈 시간대별 혈당 변화")

fig = go.Figure()

# (1) 내 혈당 그래프 선 그리기
fig.add_trace(go.Scatter(
    x=df['시간(분)'], 
    y=df['혈당(mg/dL)'],
    mode='lines+markers+text', # 선, 점, 텍스트 모두 표시
    name='내 혈당',
    text=df['혈당(mg/dL)'],
    textposition="top center",
    line=dict(color='#FF4B4B', width=3), # 빨간색 선
    marker=dict(size=10, color='#FF4B4B')
))

# (2) 관리 목표선 (140mg/dL) 그리기 - 점선
fig.add_shape(
    type="line",
    x0=0, y0=140, x1=180, y1=140,
    line=dict(color="Green", width=2, dash="dash"),
)
# 목표선 옆에 글씨 추가
fig.add_annotation(
    x=10, y=145, text="관리 목표 (140)", showarrow=False, font=dict(color="green", size=12)
)

# 그래프 디자인 다듬기
fig.update_layout(
    xaxis_title="식사 시작 후 경과 시간 (분)",
    yaxis_title="혈당 수치 (mg/dL)",
    yaxis_range=[50, max(df['혈당(mg/dL)']) + 40], # Y축 범위 자동 조절
    template="plotly_white",
    hovermode="x unified" # 마우스 올렸을 때 보기 편하게
)

st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# 5. 결과 분석 및 피드백
# ---------------------------------------------------------
st.markdown("### 💡 분석 결과")

# 최고 혈당 찾기
peak_value = df['혈당(mg/dL)'].max()
peak_time = df.loc[df['혈당(mg/dL)'].idxmax(), '시간(분)']
start_value = df.iloc[0]['혈당(mg/dL)']

# 혈당 스파이크 계산 (식전 대비 50 이상 상승 시 경고)
spike_gap = peak_value - start_value

if spike_gap >= 50:
    st.error(f"⚠️ **주의 필요:** 식전 대비 혈당이 **{spike_gap} mg/dL**나 급격히 올랐습니다.\n\n"
             f"오늘 드신 **'{food_menu if food_menu else '음식'}'** 메뉴에 탄수화물이나 당류가 많은지 확인해보세요.")
elif peak_value > 180:
    st.warning(f"⚠️ 최고 혈당이 **{peak_value}**로 다소 높습니다. 운동을 조금 더 병행하면 좋습니다.")
else:
    st.success(f"✅ **아주 좋습니다!** 혈당 변동폭이 **{spike_gap} mg/dL**로 안정적입니다.\n\n"
               "지금 같은 식단을 유지하시면 건강 관리에 큰 도움이 됩니다.")

st.write(f"- 최고 혈당 시점: 식후 **{peak_time}분**")
