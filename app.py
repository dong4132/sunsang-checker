import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta

# 1. 웹 페이지 기본 설정
st.set_page_config(
    page_title="선상24 빈자리 조회기", 
    page_icon="🎣", 
    layout="wide"
)

# 모바일 최적화 스타일
st.markdown("""
    <style>
        .stButton button {
            width: 100%;
            font-size: 16px;
            font-weight: bold;
            height: 46px;
        }
        .stDataFrame {
            font-size: 14px;
        }
        div.stForm {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎣 선상24 맞춤형 빈자리 조회기")
st.markdown("원하는 날짜를 터치하고 **[실시간 빈자리 검색하기]**를 눌러주세요.")

# 세션 상태에 날짜 초기화 (기본값: 오늘)
if 'target_date' not in st.session_state:
    st.session_state.target_date = datetime.now().date()

# 2. 메인 화면 상단 검색 폼
with st.form("search_form"):
    
    st.markdown("📅 **출조 날짜 선택 (키보드 없음, 터치로 즉시 변경)**")
    
    # 날짜를 빠르게 이동할 수 있는 전용 버튼들 (오늘, 내일, 모레, +3일, +7일)
    d_btn1, d_btn2, d_btn3, d_btn4, d_btn5 = st.columns(5)
    with d_btn1:
        p_today = st.form_submit_button("오늘")
    with d_btn2:
        p_tom = st.form_submit_button("내일")
    with d_btn3:
        p_plus2 = st.form_submit_button("+2일뒤")
    with d_btn4:
        p_plus3 = st.form_submit_button("+3일뒤")
    with d_btn5:
        p_plus7 = st.form_submit_button("+1주일")

    # 버튼 클릭에 따른 날짜 계산
    if p_today:
        st.session_state.target_date = datetime.now().date()
    elif p_tom:
        st.session_state.target_date = datetime.now().date() + timedelta(days=1)
    elif p_plus2:
        st.session_state.target_date = datetime.now().date() + timedelta(days=2)
    elif p_plus3:
        st.session_state.target_date = datetime.now().date() + timedelta(days=3)
    elif p_plus7:
        st.session_state.target_date = datetime.now().date() + timedelta(days=7)

    # 현재 선택된 날짜 큼직하게 표시
    st.success(f"🎯 선택된 출조일: **{st.session_state.target_date}**")

    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        region_options = {
            "충남전체": {
                "area": "497,498,499,500,501", 
                "area_text": "충남", 
                "area_type": "area",
                "display_name": "충남"
            },
            "당진": {
                "area": "501", 
                "area_text": "당진", 
                "area_type": "area",
                "display_name": "충남 당진"
            },
            "보령": {
                "area": "497", 
                "area_text": "보령", 
                "area_type": "area",
                "display_name": "충남 보령"
            },
            "서산": {
                "area": "499", 
                "area_text": "서산", 
                "area_type": "area",
                "display_name": "충남 서산"
            },
            "태안": {
                "area": "500", 
                "area_text": "태안", 
                "area_type": "area",
                "display_name": "충남 태안"
            },
            "홍성": {
                "area": "498", 
                "area_text": "홍성", 
                "area_type": "area",
                "display_name": "충남 홍성"
            },
            "군산": {
                "area": "493", 
                "area_text": "군산", 
                "area_type": "area",
                "display_name": "전북 군산"
            }
        }
        selected_region_label = st.selectbox("📍 지역 선택", list(region_options.keys()))
        region_info = region_options[selected_region_label]

    with col2:
        fish_options = {
            "전체": "", 
            "갑오징어": "갑오징어", 
            "주꾸미": "주꾸미", 
            "문어": "문어"
        }
        selected_fish_label = st.selectbox("🐟 대상 어종 선택", list(fish_options.keys()))
        selected_fish = fish_options[selected_fish_label]

    # 최종 검색 버튼
    search_button = st.form_submit_button("🔍 실시간 빈자리 검색하기", type="primary")

# 3. 검색 버튼을 눌렀을 때 실행되는 API 연동 로직
if search_button:
    current_date = st.session_state.target_date
    date_str = f"{current_date},{current_date}"
    
    st.markdown("---")
    st.subheader(f"📌 검색 결과 ({current_date} / {selected_region_label})")
    
    with st.spinner("선상24 실시간 빈자리를 확인하는 중입니다..."):
        try:
            api_url = "https://api.sunsang24.com/ship/list"
            
            params = {
                "page": 1,
                "type": "general",
                "sdate": date_str,
                "fish": selected_fish,
                "keyword": "",
                "area": region_info["area"],
                "area_text": region_info["area_text"],
                "area_type": region_info["area_type"]
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Referer": "https://www.sunsang24.com/"
            }
            
            response = requests.get(api_url, params=params, headers=headers)
            
            if response.status_code == 200:
                json_data = response.json()
                
                items = json_data.get("data", []) or json_data.get("list", []) or json_data.get(0, [])
                if not items and isinstance(json_data, list):
                    items = json_data
                
                parsed_list = []
                for item in items:
                    ship_info = item.get("ship", {})
                    
                    ship_name = ship_info.get("name", "정보없음")
                    ship_no = ship_info.get("no", "")
                    
                    area_main = ship_info.get("area_main", "")
                    area_sub = ship_info.get("area_sub", "")
                    
                    if selected_region_label == "충남전체":
                        region_str = region_info["display_name"]
                    else:
                        region_str = f"{area_main} {area_sub}".strict if hasattr(str, 'strict') else f"{area_main} {area_sub}".strip()
                        if not region_str:
                            region_str = region_info["display_name"]
                    
                    fish_type = item.get("fish_type", "정보없음")
                    port_name = item.get("port_name", "정보없음")
                    price = item.get("price", 0)
                    remain_seats = item.get("remain_embarkation_num", 0)
                    status_name = item.get("schedule_status_name", "확인필요")
                    sdate = item.get("sdate", str(current_date))
                    
                    # 출항/입항 시간 가공
                    raw_stime = item.get("stime", "")
                    raw_etime = item.get("etime", "")
                    stime = raw_stime[:5] if len(raw_stime) >= 5 else raw_stime
                    etime = raw_etime[:5] if len(raw_etime) >= 5 else raw_etime
                    
                    time_str = f"{stime}~{etime}" if (stime and etime) else "시간문의"
                    
                    # 잔여석이 없고 예약 불가인 경우 제외
                    if remain_seats <= 0 or status_name != "예약가능":
                        continue

                    # 선박 예약 링크 생성
                    if ship_no:
                        sdate_clean = str(sdate).replace("-", "")
                        booking_link = f"https://www.sunsang24.com/ship/list/?ship_no={ship_no}&sdate={sdate_clean}"
                    else:
                        booking_link = "https://www.sunsang24.com"

                    parsed_list.append({
                        "날짜": sdate,
                        "선박명": ship_name,
                        "지역": region_str,
                        "출항지": port_name,
                        "시간": time_str,
                        "어종": fish_type,
                        "가격": f"{price:,}원" if isinstance(price, int) else price,
                        "잔여석": f"{remain_seats}석",
                        "예약": booking_link
                    })
                
                df = pd.DataFrame(parsed_list)
                
                if not df.empty:
                    st.dataframe(
                        df, 
                        use_container_width=True,
                        column_config={
                            "예약": st.column_config.LinkColumn("예약 바로가기", display_text="🔗 예약하기")
                        }
                    )
                    st.success(f"총 {len(df)}개의 예약 가능한 빈자리를 찾았습니다!")
                else:
                    st.warning("조건에 맞는 예약 가능한 빈자리가 없습니다.")
            else:
                st.error(f"API 서버 연결 실패 (상태 코드: {response.status_code})")
                
        except Exception as e:
            st.error(f"오류가 발생했습니다: {e}")
