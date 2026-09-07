import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 웹 페이지 기본 설정
st.set_page_config(
    page_title="통합 낚시 빈자리 조회기", 
    page_icon="🎣", 
    layout="wide"
)

# 모바일 최적화 및 카드형 UI 스타일링 CSS
st.markdown("""
    <style>
        .stButton button {
            width: 100%;
            font-size: 16px;
            font-weight: bold;
            height: 48px;
        }
        div.stForm {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
        .fish-card {
            background-color: #ffffff;
            padding: 16px;
            border-radius: 12px;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 12px;
        }
        .ship-title {
            font-size: 18px;
            font-weight: bold;
            color: #1e293b;
            margin-bottom: 6px;
        }
        .ship-info {
            font-size: 14px;
            color: #475569;
            margin-bottom: 4px;
        }
        .badge-seat {
            background-color: #dbeafe;
            color: #1d4ed8;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 13px;
        }
        .badge-price {
            background-color: #f1f5f9;
            color: #334155;
            padding: 4px 8px;
            border-radius: 6px;
            font-weight: bold;
            font-size: 13px;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🎣 통합 낚시 빈자리 조회기")
st.markdown("원하는 플랫폼을 선택하고 날짜와 지역을 골라 실시간 빈자리를 확인하세요!")

# 상단 탭 나누기 (선상24 / 더피싱)
tab_sunsang, tab_thefishing = st.tabs(["🚀 선상24 조회기", "🌊 더피싱 조회기"])

# ==========================================
# [탭 1] 선상24 조회기 로직
# ==========================================
with tab_sunsang:
    st.subheader("선상24 실시간 빈자리 찾기")
    
    with st.form("sunsang_form"):
        sunsang_date = st.date_input("📅 출조 날짜 선택", value=datetime.now().date(), key="sunsang_date")
        
        col1, col2 = st.columns(2)
        with col1:
            sunsang_regions = {
                "충남전체": {"area": "497,498,499,500,501", "area_text": "충남", "area_type": "area", "display_name": "충남"},
                "당진": {"area": "501", "area_text": "당진", "area_type": "area", "display_name": "충남 당진"},
                "보령": {"area": "497", "area_text": "보령", "area_type": "area", "display_name": "충남 보령"},
                "서산": {"area": "499", "area_text": "서산", "area_type": "area", "display_name": "충남 서산"},
                "태안": {"area": "500", "area_text": "태안", "area_type": "area", "display_name": "충남 태안"},
                "홍성": {"area": "498", "area_text": "홍성", "area_type": "area", "display_name": "충남 홍성"},
                "군산": {"area": "493", "area_text": "군산", "area_type": "area", "display_name": "전북 군산"}
            }
            s_region_label = st.selectbox("📍 지역 선택", list(sunsang_regions.keys()), key="s_reg")
            s_region_info = sunsang_regions[s_region_label]

        with col2:
            sunsang_fishes = {"전체": "", "갑오징어": "갑오징어", "주꾸미": "주꾸미", "문어": "문어"}
            s_fish_label = st.selectbox("🐟 대상 어종 선택", list(sunsang_fishes.keys()), key="s_fish")
            s_fish = sunsang_fishes[s_fish_label]

        sunsang_btn = st.form_submit_button("🔍 선상24 빈자리 검색하기", type="primary")

    if sunsang_btn:
        date_str = f"{sunsang_date},{sunsang_date}"
        st.markdown("---")
        st.subheader(f"📌 선상24 검색 결과 ({sunsang_date} / {s_region_label})")
        
        with st.spinner("선상24 실시간 정보를 가져오는 중입니다..."):
            try:
                api_url = "https://api.sunsang24.com/ship/list"
                params = {
                    "page": 1, "type": "general", "sdate": date_str, "fish": s_fish,
                    "keyword": "", "area": s_region_info["area"], "area_text": s_region_info["area_text"], "area_type": s_region_info["area_type"]
                }
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://www.sunsang24.com/"
                }
                res = requests.get(api_url, params=params, headers=headers)
                
                parsed_list = []
                if res.status_code == 200:
                    json_data = res.json()
                    items = json_data.get("data", []) or json_data.get("list", []) or json_data.get(0, [])
                    if not items and isinstance(json_data, list):
                        items = json_data
                    
                    for item in items:
                        ship_info = item.get("ship", {})
                        ship_name = ship_info.get("name", "정보없음")
                        ship_no = ship_info.get("no", "")
                        
                        area_main = ship_info.get("area_main", "")
                        area_sub = ship_info.get("area_sub", "")
                        if s_region_label == "충남전체":
                            region_str = s_region_info["display_name"]
                        else:
                            region_str = f"{area_main} {area_sub}".strip() or s_region_info["display_name"]
                        
                        fish_type = item.get("fish_type", "정보없음")
                        port_name = item.get("port_name", "정보없음")
                        price = item.get("price", 0)
                        remain_seats = item.get("remain_embarkation_num", 0)
                        status_name = item.get("schedule_status_name", "확인필요")
                        
                        raw_stime = item.get("stime", "")
                        raw_etime = item.get("etime", "")
                        stime = raw_stime[:5] if len(raw_stime) >= 5 else raw_stime
                        etime = raw_etime[:5] if len(raw_etime) >= 5 else raw_etime
                        time_str = f"{stime}~{etime}" if (stime and etime) else "시간문의"
                        
                        if remain_seats <= 0 or status_name != "예약가능":
                            continue

                        booking_link = f"https://www.sunsang24.com/ship/list/?ship_no={ship_no}&sdate={str(sunsang_date).replace('-', '')}" if ship_no else "https://www.sunsang24.com"

                        parsed_list.append({
                            "선박명": ship_name, "지역": region_str, "출항지": port_name,
                            "시간": time_str, "어종": fish_type,
                            "가격": f"{price:,}원" if isinstance(price, int) else f"{price}원",
                            "잔여석": remain_seats, "예약링크": booking_link
                        })
                
                if parsed_list:
                    st.success(f"총 {len(parsed_list)}개의 빈자리를 찾았습니다!")
                    st.markdown("<br>", unsafe_allow_html=True)
                    for item in parsed_list:
                        st.markdown(f"""
                            <div class="fish-card">
                                <div class="ship-title">🚢 {item["선박명"]}</div>
                                <div class="ship-info">📍 <b>지역:</b> {item["지역"]} ({item["출항지"]})</div>
                                <div class="ship-info">⏰ <b>시간:</b> {item["시간"]}</div>
                                <div class="ship-info">🐟 <b>어종:</b> {item["어종"]}</div>
                                <div style="margin-top: 10px; display: flex; gap: 8px; align-items: center;">
                                    <span class="badge-seat">🔥 잔여석: {item["잔여석"]}석</span>
                                    <span class="badge-price">💰 {item["가격"]}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        st.link_button(f"🔗 {item['선박명']} 예약하러 가기", item["예약링크"])
                        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
                else:
                    st.warning("조건에 맞는 예약 가능한 빈자리가 없습니다.")
            except Exception as e:
                st.error(f"오류 발생: {e}")

# ==========================================
# [탭 2] 더피싱 조회기 로직
# ==========================================
with tab_thefishing:
    st.subheader("더피싱 실시간 빈자리 찾기")
    
    with st.form("thefishing_form"):
        tf_date = st.date_input("📅 출조 날짜 선택", value=datetime.now().date(), key="tf_date")
        
        col1, col2 = st.columns(2)
        with col1:
            tf_regions = {"전체지역": "", "충남/군산권": "49"}
            tf_region_label = st.selectbox("📍 지역 선택", list(tf_regions.keys()), key="tf_reg")
            tf_region_code = tf_regions[tf_region_label]

        with col2:
            tf_fishes = {"전체": "", "갑오징어": "갑오징어", "주꾸미": "주꾸미", "문어": "문어"}
            tf_fish_label = st.selectbox("🐟 대상 어종 선택", list(tf_fishes.keys()), key="tf_fish")
            tf_fish = tf_fishes[tf_fish_label]

        tf_btn = st.form_submit_button("🔍 더피싱 빈자리 검색하기", type="primary")

    if tf_btn:
        date_str = tf_date.strftime("%Y-%m-%d")
        st.markdown("---")
        st.subheader(f"📌 더피싱 검색 결과 ({tf_date} / {tf_region_label})")
        
        with st.spinner("더피싱 정보를 불러오는 중입니다..."):
            try:
                target_url = "https://thefishing.kr/reservation/list.php"
                params = {"search_date": date_str, "search_2": tf_fish}
                if tf_region_code:
                    params["sa[]"] = tf_region_code
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Referer": "https://thefishing.kr/"
                }
                res = requests.get(target_url, params=params, headers=headers)
                
                if res.status_code == 200:
                    st.success("더피싱 검색 페이지 연결 완료!")
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown("""
                        <div class="fish-card">
                            <div class="ship-title">🌊 더피싱 맞춤 검색 링크</div>
                            <div class="ship-info">선택하신 조건으로 더피싱 검색 페이지가 생성되었습니다. 아래 버튼을 눌러 원본 사이트에서 바로 확인하실 수 있습니다.</div>
                        </div>
                    """, unsafe_allow_html=True)
                    st.link_button("🔗 더피싱 검색 결과 페이지 열기", res.url)
                else:
                    st.warning("더피싱 연결에 실패했습니다.")
            except Exception as e:
                st.error(f"오류 발생: {e}")
