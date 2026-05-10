import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# ----------------- 데이터 수집 함수 ----------------- #

def get_wiki_info(food_name):
    """위키백과 API를 사용하여 정확한 음식 유래와 고화질 이미지를 즉시 가져옵니다."""
    url = f"https://ko.wikipedia.org/api/rest_v1/page/summary/{food_name}"
    try:
        res = requests.get(url).json()
        description = res.get("extract", f"'{food_name}'에 대한 백과사전 설명이 없습니다.")
        # 이미지가 없을 경우 대체 이미지 제공
        image_url = res.get("thumbnail", {}).get("source", "https://via.placeholder.com/500x300?text=No+Image+Found")
        return description, image_url
    except Exception:
        return "정보를 불러오는데 실패했습니다.", "https://via.placeholder.com/500x300?text=Error"

def get_recipe(food_name):
    """네이버 검색을 통해 상위 레시피 요약 텍스트를 바로 가져옵니다."""
    url = f"https://search.naver.com/search.naver?query={food_name}+황금레시피+만드는법"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 블로그 검색 결과의 본문 요약 발췌
        snippets = soup.select('.api_txt_lines.dsc_txt')
        if snippets:
            return snippets[0].text
        return "자세한 레시피 정보를 화면에 바로 띄울 수 없습니다. 검색어를 바꿔보세요."
    except Exception:
        return "레시피 정보를 불러오는 중 오류가 발생했습니다."

def get_best_restaurants(food_name):
    """
    네이버 검색을 활용하여 사람들이 가장 많이 추천하는 상위 3개 맛집의 
    이름이나 리뷰 제목을 긁어와 바로 보여줍니다.
    """
    url = f"https://search.naver.com/search.naver?query={food_name}+전국+3대+맛집+추천"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
        # 상위 노출되는 포스팅의 제목들 추출
        titles = soup.select('.api_txt_lines.total_tit')
        
        if titles:
            places = []
            for i, title in enumerate(titles[:3]):
                places.append(f"{i+1}. {title.text}")
            return places
        return ["추천 맛집 데이터를 찾을 수 없습니다."]
    except Exception:
        return ["맛집 검색 중 오류가 발생했습니다."]

# ----------------- 화면 UI 구성 ----------------- #

st.set_page_config(page_title="즉시 보는 음식 백과", page_icon="🍔", layout="centered")

st.title("🍔 음식 정보 즉시 검색기")
st.write("음식 이름을 입력하면 클릭 없이 **사진, 유래, 레시피, 1위 맛집**이 한 번에 나옵니다.")

# 검색창
food_name = st.text_input("궁금한 음식 이름을 입력하세요 (예: 떡볶이, 평양냉면)")

if food_name:
    # 로딩 애니메이션
    with st.spinner(f"인터넷에서 '{food_name}'의 최고 데이터를 모으는 중입니다..."):
        
        # 정보 긁어오기
        origin_text, img_url = get_wiki_info(food_name)
        recipe_text = get_recipe(food_name)
        best_places = get_best_restaurants(food_name)
        
        st.divider()

        # 1. 사진 표시 (링크 이동 없이 화면에 바로 출력)
        st.image(img_url, caption=f"{food_name} 대표 사진", use_container_width=True)
        
        # 2. 음식의 유래 표시
        st.subheader("📜 음식의 유래 및 설명")
        st.info(origin_text)
        
        # 3. 레시피 요약 표시
        st.subheader("👨‍🍳 핵심 레시피 요약")
        st.success(recipe_text)
        
        # 4. 평가가 좋은 맛집 리스트 직접 표시
        st.subheader("🏆 네이버 추천 상위 맛집 리스트")
        st.write("검색 결과 가장 평가가 좋고 많이 언급된 식당 정보입니다.")
        for place in best_places:
            st.warning(place)

st.caption("※ 데이터는 위키백과 및 네이버 실시간 검색 결과를 즉시 추출하여 제공합니다.")
