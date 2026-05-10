import streamlit as st
import requests
from bs4 import BeautifulSoup
import urllib.parse

# 페이지 설정 (모바일 최적화)
st.set_page_config(page_title="음식 백과사전", page_icon="🍴")

st.title("🍴 음식 정보 검색")
st.write("음식 이름을 입력하면 사진, 레시피, 유래, 맛집 정보를 찾아줍니다.")

food_name = st.text_input("어떤 음식이 궁금하신가요?", placeholder="예: 비빔밥, 똠양꿍")

if food_name:
    with st.spinner('정보를 가져오는 중입니다...'):
        # 1. 사진 검색 (구글 이미지 검색 결과 페이지 링크)
        encoded_food = urllib.parse.quote(food_name)
        img_url = f"https://www.google.com/search?q={encoded_food}+음식+사진&tbm=isch"
        
        # 2. 레시피 및 유래 (네이버 검색 활용)
        # 실제 앱에서는 API를 쓰는 것이 좋으나, 여기서는 결과 페이지 연결 방식으로 구현
        recipe_url = f"https://search.naver.com/search.naver?query={encoded_food}+레시피"
        history_url = f"https://search.naver.com/search.naver?query={encoded_food}+유래"
        
        # 3. 맛집 정보 (네이버 지도)
        map_url = f"https://map.naver.com/v5/search/{encoded_food} 맛집"

        # 결과 화면 출력
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.link_button("📸 대표 사진 보기", img_url, use_container_width=True)
        with col2:
            st.link_button("📍 주변 맛집 찾기", map_url, use_container_width=True)

        with st.expander("👨‍🍳 레시피(만드는 법) 보기", expanded=True):
            st.write(f"'{food_name}'의 상세 레시피는 아래 링크에서 확인할 수 있습니다.")
            st.markdown(f"[네이버 레시피 검색 결과 바로가기]({recipe_url})")

        with st.expander("📜 음식의 유래 보기"):
            st.write(f"'{food_name}'이(가) 어디서 시작되었는지 궁금하신가요?")
            st.markdown(f"[네이버 유래/백과사전 검색 결과 바로가기]({history_url})")

st.caption("공공 데이터 및 포털 검색 결과를 활용합니다.")
