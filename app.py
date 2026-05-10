
import streamlit as st
import requests
import urllib.parse

# ----------------- 데이터 엔진 ----------------- #

def get_wiki_data(food_name):
    """위키백과 공식 REST API 사용 (차단 위험 없음)"""
    encoded_name = urllib.parse.quote(food_name)
    url = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{encoded_name}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return {
                "desc": data.get("extract", "설명이 없습니다."),
                "img": data.get("thumbnail", {}).get("source", "https://via.placeholder.com/500x300?text=No+Image")
            }
    except:
        pass
    return {"desc": "정보를 불러올 수 없습니다.", "img": "https://via.placeholder.com/500x300?text=Error"}

# ----------------- UI 구성 ----------------- #

st.set_page_config(page_title="푸아그라 검색 성공 앱", page_icon="🍲")

# 모바일 가독성을 위한 스타일 설정
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🍲 실시간 음식 백과사전")
st.write("가장 안정적인 데이터를 실시간으로 가져옵니다.")

food_name = st.text_input("음식 이름을 입력하세요", placeholder="예: 푸아그라, 에스카르고")

if food_name:
    with st.spinner('최신 정보를 분석 중...'):
        # 1. 위키백과 정보 가져오기 (가장 안정적)
        wiki = get_wiki_data(food_name)
        
        # 2. 검색 쿼리 생성
        encoded_food = urllib.parse.quote(food_name)
        recipe_link = f"https://www.google.com/search?q={encoded_food}+레시피+만드는법"
        restaurant_link = f"https://www.google.com/search?q={encoded_food}+전국+맛집+추천+순위"

        # 화면 출력
        st.divider()
        
        # 이미지 출력
        st.image(wiki['img'], caption=f"<{food_name}>", use_container_width=True)
        
        # 설명 (유래)
        st.subheader("📜 음식의 유래 및 설명")
        st.info(wiki['desc'])
        
        # 레시피와 맛집 (텍스트 기반 요약 및 링크)
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👨‍🍳 레시피 요약")
            st.success(f"'{food_name}' 조리법의 핵심은 신선한 재료와 적절한 온도 조절입니다.")
            st.link_button("상세 레시피 보기", recipe_link, use_container_width=True)
            
        with col2:
            st.subheader("🏆 추천 맛집")
            st.warning(f"현재 위치 주변 및 전국에서 가장 평점이 높은 '{food_name}' 전문점을 찾아보세요.")
            st.link_button("맛집 리스트 확인", restaurant_link, use_container_width=True)

st.caption("공식 API와 실시간 검색 엔진을 결합하여 정보를 제공합니다.")
