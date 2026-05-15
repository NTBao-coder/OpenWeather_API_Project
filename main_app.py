# Run Streamlit main
import streamlit as st
import folium
from folium import raster_layers
from streamlit_folium import st_folium
from api_modules import (
    get_air_pollution,
    get_coordinates_by_city,
    get_current_weather,
    get_location_info,
    API_KEY,
)


WEATHER_LAYERS = {
    "Nhiệt độ": "temp_new",
    "Gió": "wind_new",
    "Mây": "clouds_new",
    "Lượng mưa": "precipitation_new",
}

MAP_HEIGHT = 360


def create_weather_map(lat, lon):
    """Tạo bản đồ Folium với base map ổn định và các layer OpenWeather."""
    weather_map = folium.Map(
        location=[lat, lon],
        zoom_start=10,
        tiles=None,
        control_scale=True,
        zoom_control=True,
        prefer_canvas=True,
    )

    raster_layers.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        name="OpenStreetMap",
        control=False,
    ).add_to(weather_map)

    folium.CircleMarker(
        location=[lat, lon],
        radius=8,
        color="#1f77b4",
        fill=True,
        fill_color="#1f77b4",
        fill_opacity=0.85,
        tooltip="Vị trí tra cứu",
    ).add_to(weather_map)

    if API_KEY:
        for layer_name, layer_code in WEATHER_LAYERS.items():
            tile_url = (
                f"https://tile.openweathermap.org/map/{layer_code}/"
                f"{{z}}/{{x}}/{{y}}.png?appid={API_KEY}"
            )
            raster_layers.TileLayer(
                tiles=tile_url,
                attr="Map data &copy; OpenWeatherMap",
                name=layer_name,
                overlay=True,
                control=True,
                opacity=0.65,
                show=layer_code == "temp_new",
            ).add_to(weather_map)

        folium.LayerControl(collapsed=True).add_to(weather_map)

    return weather_map


# 1. Cấu hình trang
st.set_page_config(page_title="MyWeather App", layout="wide", page_icon="🌤️")

st.title("🌤️ Ứng dụng MyWeather")
st.markdown("Tra cứu thông tin thời tiết và chất lượng không khí dựa trên tọa độ.")
st.markdown(
    """
    <style>
    div[data-testid="stImage"] img {
        display: block;
        margin: 0 auto;
    }

    iframe[title="streamlit_folium.st_folium"] {
        border: 1px solid #d9dee8;
        border-radius: 8px;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 2. Tạo Sidebar để nhập liệu
st.sidebar.header("📍 Tra cứu")
search_mode = st.sidebar.radio(
    "Chọn chế độ đầu vào",
    ["Tọa độ", "Tên thành phố"],
    horizontal=True,
)

if search_mode == "Tọa độ":
    # Set mặc định là tọa độ TP.HCM cho dễ test
    input_lat = st.sidebar.number_input(
        "Vĩ độ (Latitude):",
        min_value=-90.0,
        max_value=90.0,
        value=10.7769,
        format="%.4f",
    )
    input_lon = st.sidebar.number_input(
        "Kinh độ (Longitude):",
        min_value=-180.0,
        max_value=180.0,
        value=106.7009,
        format="%.4f",
    )
else:
    input_city = st.sidebar.text_input(
        "Tên thành phố:",
        value="Ho Chi Minh City",
        placeholder="Ví dụ: Hanoi, Da Nang, Tokyo",
    )

if st.sidebar.button("Tra cứu thời tiết"):
    if search_mode == "Tên thành phố":
        city_lookup = get_coordinates_by_city(input_city)
        if city_lookup["status"] != "success":
            st.error(city_lookup["message"])
            st.stop()

        lat = city_lookup["lat"]
        lon = city_lookup["lon"]
        resolved_city = city_lookup["city"]
        resolved_country = city_lookup["country"]
        resolved_state = city_lookup["state"]
        location_label = f"{resolved_city}, {resolved_country}"
        if resolved_state:
            location_label = f"{resolved_city}, {resolved_state}, {resolved_country}"

        st.sidebar.success(f"Đã tìm thấy: {location_label}")
        st.sidebar.caption(f"Tọa độ: {lat:.4f}, {lon:.4f}")
    else:
        lat = input_lat
        lon = input_lon
        location_label = None

    # Chia giao diện làm 2 cột
    col1, col2 = st.columns([1, 1.25], gap="large")
    
    with col1:
        st.subheader("🏙️ Thông tin Khu vực")
        # Gọi API 1
        loc_data = get_location_info(lat, lon)
        if loc_data['status'] == 'success':
            display_city = location_label or f"{loc_data['city']}, {loc_data['country']}"
            st.success(f"**Khu vực:** {display_city}")
            st.caption(f"Vĩ độ: {lat:.4f} | Kinh độ: {lon:.4f}")
        else:
            st.error(loc_data['message'])

        st.subheader("🌡️ Thời tiết hiện tại")
        # Gọi API 2
        weather_data = get_current_weather(lat, lon)
        if weather_data['status'] == 'success':
            temp_col, humidity_col, wind_col = st.columns(3)
            temp_col.metric("Nhiệt độ", f"{weather_data['temp']}°C")
            humidity_col.metric("Độ ẩm", f"{weather_data['humidity']}%")
            wind_col.metric("Sức gió", f"{weather_data['wind_speed']} m/s")
            st.info(f"**Mô tả:** {weather_data['description']}")
            # Hiển thị icon thời tiết
            icon_url = f"https://openweathermap.org/img/wn/{weather_data['icon']}@2x.png"
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
        st.subheader("🗺️ Bản đồ thời tiết")

        if not API_KEY:
            st.warning("Chưa cấu hình API Key nên chỉ hiển thị bản đồ nền.")

        m = create_weather_map(lat, lon)
        st_folium(
            m,
            use_container_width=True,
            height=MAP_HEIGHT,
            returned_objects=[],
            key=f"weather_map_{lat}_{lon}",
        )
