# Run Streamlit main
import streamlit as st
import folium
from streamlit_folium import st_folium
from api_modules import get_location_info, get_current_weather, get_air_pollution, API_KEY

# 1. Cấu hình trang
st.set_page_config(page_title="MyWeather App", layout="wide", page_icon="🌤️")

st.title("🌤️ Ứng dụng MyWeather")
st.markdown("Tra cứu thông tin thời tiết và chất lượng không khí dựa trên tọa độ.")

# 2. Tạo Sidebar để nhập liệu (Theo đúng yêu cầu: Lấy từ tọa độ)
st.sidebar.header("📍 Nhập tọa độ")
# Set mặc định là tọa độ TP.HCM cho dễ test
lat = st.sidebar.number_input("Vĩ độ (Latitude):", value=10.7769, format="%.4f")
lon = st.sidebar.number_input("Kinh độ (Longitude):", value=106.7009, format="%.4f")

if st.sidebar.button("Tra cứu thời tiết"):
    # Chia giao diện làm 2 cột
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏙️ Thông tin Khu vực")
        # Gọi API 1
        loc_data = get_location_info(lat, lon)
        if loc_data['status'] == 'success':
            st.success(f"**Thành phố:** {loc_data['city']} | **Quốc gia:** {loc_data['country']}")
        else:
            st.error(loc_data['message'])

        st.subheader("🌡️ Thời tiết hiện tại")
        # Gọi API 2
        weather_data = get_current_weather(lat, lon)
        if weather_data['status'] == 'success':
            st.info(f"**Nhiệt độ:** {weather_data['temp']}°C")
            st.info(f"**Độ ẩm:** {weather_data['humidity']}%")
            st.info(f"**Sức gió:** {weather_data['wind_speed']} m/s")
            st.info(f"**Mô tả:** {weather_data['description']}")
            # Hiển thị icon thời tiết
            icon_url = f"http://openweathermap.org/img/wn/{weather_data['icon']}@2x.png"
            st.image(icon_url, width=100)
        else:
            st.error(weather_data['message'])
            
        st.subheader("😷 Chất lượng không khí (AQI)")
        # Gọi API 3
        aqi_data = get_air_pollution(lat, lon)
        if aqi_data['status'] == 'success':
            # AQI scale: 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor
            aqi_val = aqi_data['aqi']
            st.warning(f"**Chỉ số AQI:** {aqi_val} / 5")
        else:
            st.error(aqi_data['message'])

    with col2:
        st.subheader("🗺️ Bản đồ thời tiết (Lớp Nhiệt độ)")
        # Sử dụng Folium để vẽ bản đồ
        m = folium.Map(location=[lat, lon], zoom_start=10)
        
        # Đánh dấu vị trí người dùng nhập
        folium.Marker([lat, lon], tooltip="Vị trí tra cứu").add_to(m)
        
        # Thêm layer bản đồ nhiệt độ từ OpenWeather Map 1.0 API
        if API_KEY:
            tile_url = f"https://tile.openweathermap.org/map/temp_new/{{z}}/{{x}}/{{y}}.png?appid={API_KEY}"
            folium.TileLayer(
                tiles=tile_url,
                attr="OpenWeatherMap",
                name="Lớp Nhiệt độ",
                overlay=True,
                control=True
            ).add_to(m)
        
        # Render bản đồ lên Streamlit
        st_folium(m, width=500, height=500)