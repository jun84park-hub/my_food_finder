
import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 타겟 사이트의 봇 차단을 피하기 위한 헤더 세트
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

def get_food_data_google(food_name, search_type="recipe"):
    """네이버 대신 구글 검색 결과의 스니펫(요약문)을 가져오는 안정적인 로직"""
    queries = {
        "recipe": f"{food_name} 만드는법 레시피 요약",
        "restaurant": f"{food_name} 맛집 추천 리스트 후기",
        "history": f"{food_name} 유래 역사"
    }
    
    query = urllib.parse.quote(queries.get(search_type, food_name))
    url = f"https://www.google.com/search?q={query}&hl=ko"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=8)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 구글 검색 결과의 요약 텍스트(스니펫) 클래스 추출
        snippets = soup.select('.VwiC3b, .MUwY9c, .yY7snc')
        
        results = []
        for s in snippets:
            text = s.get_text(strip=True)
            if len(text) > 40: # 너무 짧은 글은 제외
                results.append(text)
            if len(results) >= 2:
                break
                
        return "\n\n".join(results) if results else "상세 정보를 찾을 수 없습니다."
    except Exception:
        return f"{search_type} 정보를 수집하는 중 네트워크 오류가 발생했습니다."

def get_wiki_reliable(food_name):
    """위키백과 API - 가장 높은 신뢰도"""
    url = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(food_name)}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = res.json()
            return data.get("extract", ""), data.get("thumbnail", {}).get("source", "")
    except:
        pass
    return "설명을 가져올 수 없습니다.", "https://via.placeholder.com/500x300?text=No+Image"

# ----------------- UI ----------------- #
st.set_page_config(page_title="푸아그라 검색 성공 버전", page_icon="🥘")

st.title("🥘 AI 기반 음식 정보 통합 검색")
st.markdown("---")

food_name = st.text_input("검색할 음식 이름을 입력하세요", placeholder="예: 푸아그라")

if food_name:
    with st.spinner(f"'{food_name}'의 데이터를 3가지 경로로 수집 중입니다..."):
        # 1. 유래 및 사진 (Wikipedia)
        history_wiki, img_url = get_wiki_reliable(food_name)
        
        # 2. 레시피 (Google Recipe Snippet)
        recipe_data = get_food_data_google(food_name, "recipe")
        
        # 3. 맛집 (Google Restaurant Snippet)
        restaurant_data = get_food_data_google(food_name, "restaurant")
        
        # 결과 렌더링
        st.image(img_url, caption=f"[{food_name}] 대표 이미지", use_container_width=True)
        
        with st.container():
            st.subheader("📜 음식의 유래 및 역사")
            st.info(history_wiki)
            
        with st.container():
            st.subheader("👨‍🍳 추천 레시피 및 조리법")
            st.success(recipe_data)
            
        with st.container():
            st.subheader("🏆 전문가 및 유저 추천 맛집 정보")
            st.warning(restaurant_data)

st.markdown("---")
st.caption("본 앱은 Google 검색 엔진의 실시간 데이터를 분석하여 최적의 정보를 제공합니다.")
