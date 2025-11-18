import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import os

warning_icon1 = folium.Icon(
    color='darkred',     
    icon='exclamation-triangle',
    prefix='fa'        
)

warning_icon2 = folium.Icon(
    color='orange',     
    icon='exclamation-triangle',
    prefix='fa'        
)

DATA_FILE = 'clicked_locations_data.csv'
st.title("안전 지도")
st.markdown("지도를 클릭하면 위험 지역을 체크할 수 있습니다.")

default_lat=37.514575
default_lng=127.0495556

if 'map_center_lat' not in st.session_state:
    st.session_state.map_center_lat = default_lat
if 'map_center_lng' not in st.session_state:
    st.session_state.map_center_lng = default_lng

input_lat_str = st.sidebar.text_input('위도 (Latitude)', value=st.session_state.map_center_lat)
input_lng_str = st.sidebar.text_input('경도 (Longitude)', value=st.session_state.map_center_lng)

def create_folium_map(lat_str, lng_str):
    try:

        initial_lat = float(lat_str)
        initial_lng = float(lng_str)
    except ValueError:
        st.warning("위도/경도 입력값이 올바른 숫자 형식이 아닙니다. 기본 위치를 사용합니다.")
        initial_lat = default_lat
        initial_lng = default_lng
    
    m = folium.Map(location=[initial_lat,initial_lng], zoom_start=15, tiles='OpenStreetMap')
    
    if st.session_state.clicked_locations:
        
        for idx, loc in enumerate(st.session_state.clicked_locations):
            if(loc['c']==1):
                folium.Marker(
                    location=[loc['a'], loc['b']],
                    popup=f"사고지역 #{idx+1}: ({loc['a']:.4f}, {loc['b']:.4f})",
                    icon=warning_icon1
                ).add_to(m)
            else:
                folium.Marker(
                    location=[loc['a'], loc['b']],
                    popup=f"클릭 #{idx+1}: ({loc['a']:.4f}, {loc['b']:.4f})",
                    icon=warning_icon2
                ).add_to(m)
    return m

def load_locations():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_csv(DATA_FILE)
            return df.to_dict('records')
        except pd.errors.EmptyDataError:
            return []
        except Exception as e:
            st.error(f"데이터 로딩 중 오류 발생: {e}")
            return []
    else:
        return []

def save_locations(locations_list):
    df = pd.DataFrame(locations_list)
    df.to_csv(DATA_FILE, index=False)


if 'clicked_locations' not in st.session_state:
    st.session_state.clicked_locations = load_locations()

m = create_folium_map(input_lat_str,input_lng_str)
map_data = st_folium(m,width=800,height=600,key="map_main")
    
if map_data and map_data.get("last_clicked"):
    latest_click = map_data["last_clicked"]
    
    lat = latest_click['lat']
    lng = latest_click['lng']
    st.sidebar.markdown(f"**마지막 클릭 위치:**")
    st.sidebar.markdown(f"위도: **{lat:.6f}**")
    st.sidebar.markdown(f"경도: **{lng:.6f}**")
    new_location = {'a': lat, 'b': lng, 'c': 2}

    if new_location not in st.session_state.clicked_locations:
        st.session_state.clicked_locations.append(new_location)
        save_locations(st.session_state.clicked_locations)
        st.session_state.map_center_lat = lat
        st.session_state.map_center_lng = lng
        st.rerun() 