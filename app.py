import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 실제 크롬 브라우저인 것처럼 속이는 강력한 헤더 (봇 차단 방지)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
}

def get_wiki_info(food_name):
    """위키백과 API (가장 안정적)"""
    url = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(food_name)}"
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        description = data.get("extract", f"'{food_name}'에 대한 위키백과 설명이 없습니다.")
        image_url = data.get("thumbnail", {}).get("source", "https://via.placeholder.com/500x300?text=No+Image")
        return description, image_url
    except Exception as e:
        return f"유래 정보를 불러오지 못했습니다. (검색어: {food_name})", "https://via.placeholder.com/500x300?text=Error"

def get_recipe(food_name):
    """네이버 레시피 검색 크롤링 (방어 코드 적용)"""
    query = urllib.parse.quote(f"{food_name} 레시피 만드는 법")
    url = f"https://search.naver.com/search.naver?query={query}"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 네이버 블로그/뷰 텍스트 추출 (클래스명이 유동적이므로 여러 클래스 시도)
        descriptions = soup.find_all('div', class_=['api_txt_lines', 'dsc_txt'])
        
        for desc in descriptions:
            text = desc.get_text(strip=True)
            # 너무 짧은 텍스트 제외하고 의미 있는 레시피 정보 추출
            if len(text) > 30: 
                return text
                
        return f"'{food_name}'에 대한 레시피 텍스트를 화면에 직접 표시할 수 없습니다."
    except Exception as e:
        return "네이버 서버에서 레시피 정보를 차단했거나 가져올 수 없습니다."

def get_best_restaurants(food_name):
    """네이버 맛집 검색 크롤링 (방어 코드 적용)"""
    query = urllib.parse.quote(f"{food_name} 맛집 후기")
    url = f"https://search.naver.com/search.naver?query={query}"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 블로그/카페 글 제목 추출
        titles = soup.find_all('a', class_=['api_txt_lines', 'total_tit', 'title_link'])
        
        places = []
        for title in titles:
            text = title.get_text(strip=True)
            if food_name in text or "맛집" in text or "후기" in text:
                if text not in places: # 중복 제거
                    places.append(text)
            if len(places) >= 3:
                break
                
        if places:
            return places
        return ["추천 맛집 포스팅을 찾을 수 없습니다. 검색어를 변경해보세요."]
    except Exception as e:
        return ["맛집 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."]

# ----------------- UI 구성 ----------------- #
st.set_page_config(page_title="음식 백과사전", page_icon="🍔", layout="centered")

st.title("🍔 즉시 확인! 음식 정보")

food_name = st.text_input("궁금한 음식 이름을 입력하세요 (예: 푸아그라, 팟타이)", placeholder="음식 이름 입력 후 엔터")

if food_name:
    with st.spinner(f"'{food_name}' 데이터를 실시간으로 수집 중입니다..."):
        
        origin_text, img_url = get_wiki_info(food_name)
        recipe_text = get_recipe(food_name)
        best_places = get_best_restaurants(food_name)
        
        st.divider()

        st.image(img_url, caption=f"{food_name} 사진", use_container_width=True)
        
        st.subheader("📜 설명 및 유래")
        st.info(origin_text)
        
        st.subheader("👨‍🍳 레시피 및 만드는 법 요약")
        st.success(recipe_text)
        
        st.subheader("🏆 네이버 맛집 및 추천 후기")
        st.write("관련된 상위 식당 추천/리뷰 포스팅 제목입니다.")
        for idx, place in enumerate(best_places):
            st.warning(f"{idx+1}. {place}")

st.caption("공공 데이터 및 포털 검색 결과를 실시간으로 추출하여 제공합니다.")
