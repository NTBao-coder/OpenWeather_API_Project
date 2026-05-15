# Run Streamlit main
from pathlib import Path
import json

import folium
import pandas as pd
import plotly.express as px
import streamlit as st
from folium import raster_layers
from streamlit_folium import st_folium

from api_modules import (
    API_KEY,
    get_air_pollution,
    get_coordinates_by_city,
    get_current_weather,
    get_location_info,
    get_weather_forecast,
)


BASE_DIR = Path(__file__).resolve().parent
USER_FILE = BASE_DIR / "users.json"
MAP_HEIGHT = 360

WEATHER_LAYERS = {
    "Nhiệt độ": "temp_new",
    "Gió": "wind_new",
    "Mây": "clouds_new",
    "Lượng mưa": "precipitation_new",
}

AQI_LABELS = {
    1: "Tốt",
    2: "Khá",
    3: "Trung bình",
    4: "Kém",
    5: "Rất kém",
}


st.set_page_config(page_title="MyWeather App", layout="wide", page_icon="🌤️")


def load_users():
    if not USER_FILE.exists():
        return {}

    try:
        with USER_FILE.open("r", encoding="utf-8") as f:
            users = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

    for user_data in users.values():
        user_data.setdefault("password", "")
        user_data.setdefault("favorites", [])

    return users


def save_users(users):
    with USER_FILE.open("w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)


def init_session_state():
    defaults = {
        "logged_in": False,
        "username": "",
        "last_search": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def current_user(users):
    username = st.session_state["username"]
    if not st.session_state["logged_in"] or username not in users:
        return None

    users[username].setdefault("favorites", [])
    return users[username]


def create_weather_map(lat, lon):
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


def resolve_search(search_mode, input_city=None, input_lat=None, input_lon=None):
    if search_mode == "Tên thành phố":
        city_lookup = get_coordinates_by_city(input_city or "")
        if city_lookup["status"] != "success":
            return city_lookup

        city_parts = [city_lookup["city"]]
        if city_lookup.get("state"):
            city_parts.append(city_lookup["state"])
        city_parts.append(city_lookup["country"])

        return {
            "status": "success",
            "mode": search_mode,
            "lat": city_lookup["lat"],
            "lon": city_lookup["lon"],
            "city": city_lookup["city"],
            "country": city_lookup["country"],
            "label": ", ".join(city_parts),
        }

    return {
        "status": "success",
        "mode": search_mode,
        "lat": input_lat,
        "lon": input_lon,
        "city": None,
        "country": None,
        "label": None,
    }


def add_favorite(users, favorite_name):
    username = st.session_state["username"]
    if not st.session_state["logged_in"] or username not in users:
        st.warning("Bạn cần đăng nhập để lưu địa điểm yêu thích.")
        return

    favorite_name = favorite_name.strip()
    if not favorite_name:
        return

    favorites = users[username].setdefault("favorites", [])
    existing = {item.casefold() for item in favorites}

    if favorite_name.casefold() not in existing:
        favorites.append(favorite_name)
        save_users(users)
        st.toast(f"Đã lưu {favorite_name} vào yêu thích.")
    else:
        st.toast(f"{favorite_name} đã có trong danh sách yêu thích.")


def remove_favorite(users, favorite_name):
    username = st.session_state["username"]
    if not st.session_state["logged_in"] or username not in users:
        return

    users[username]["favorites"] = [
        item for item in users[username].get("favorites", [])
        if item.casefold() != favorite_name.casefold()
    ]
    save_users(users)
    st.toast(f"Đã xóa {favorite_name} khỏi yêu thích.")


def apply_page_styles():
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        div[data-testid="stImage"] img {
            display: block;
            margin: 0 auto;
        }

        iframe[title="streamlit_folium.st_folium"] {
            border: 1px solid #d9dee8;
            border-radius: 8px;
            overflow: hidden;
        }

        .weather-widget-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin: 12px 0 8px;
        }

        .weather-widget {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 14px;
        }

        .weather-widget-title {
            color: #64748b;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        .weather-widget-value {
            color: #0f172a;
            font-size: 20px;
            font-weight: 700;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(users):
    st.sidebar.header("👤 Tài khoản")

    if not st.session_state["logged_in"]:
        tab_login, tab_register = st.sidebar.tabs(["Đăng nhập", "Đăng ký"])

        with tab_login:
            login_user = st.text_input("Tên đăng nhập", key="login_user")
            login_pass = st.text_input("Mật khẩu", type="password", key="login_pass")
            if st.button("Đăng nhập", use_container_width=True):
                if login_user in users and users[login_user]["password"] == login_pass:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = login_user
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu.")

        with tab_register:
            reg_user = st.text_input("Tên đăng nhập mới", key="reg_user")
            reg_pass = st.text_input("Mật khẩu mới", type="password", key="reg_pass")
            if st.button("Tạo tài khoản", use_container_width=True):
                if reg_user in users:
                    st.warning("Tên đăng nhập đã tồn tại.")
                elif reg_user and reg_pass:
                    users[reg_user] = {"password": reg_pass, "favorites": []}
                    save_users(users)
                    st.success("Tạo tài khoản thành công. Hãy đăng nhập.")
                else:
                    st.warning("Vui lòng điền đủ thông tin.")
    else:
        st.sidebar.success(f"Xin chào, {st.session_state['username']}")
        if st.sidebar.button("Đăng xuất", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["last_search"] = None
            st.rerun()

    st.sidebar.divider()

    favorite_request = None
    user_data = current_user(users)
    if user_data is not None:
        favorites = user_data.get("favorites", [])
        st.sidebar.header("⭐ Yêu thích")

        if favorites:
            fav_city = st.sidebar.selectbox("Địa điểm đã lưu", favorites)
            fav_col1, fav_col2 = st.sidebar.columns(2)
            if fav_col1.button("Tra cứu", use_container_width=True, key="search_favorite"):
                favorite_request = fav_city
            if fav_col2.button("Xóa", use_container_width=True, key="remove_favorite"):
                remove_favorite(users, fav_city)
                st.rerun()
        else:
            st.sidebar.caption("Chưa có địa điểm yêu thích.")

        st.sidebar.divider()

    st.sidebar.header("📍 Tra cứu")
    with st.sidebar.form("search_form"):
        search_mode = st.radio(
            "Chọn chế độ đầu vào",
            ["Tọa độ", "Tên thành phố"],
            horizontal=True,
        )

        if search_mode == "Tọa độ":
            input_lat = st.number_input(
                "Vĩ độ (Latitude)",
                min_value=-90.0,
                max_value=90.0,
                value=10.7769,
                format="%.4f",
            )
            input_lon = st.number_input(
                "Kinh độ (Longitude)",
                min_value=-180.0,
                max_value=180.0,
                value=106.7009,
                format="%.4f",
            )
            input_city = None
        else:
            input_city = st.text_input(
                "Tên thành phố",
                value="Ho Chi Minh City",
                placeholder="Ví dụ: Hanoi, Da Nang, Tokyo",
            )
            input_lat = None
            input_lon = None

        submitted = st.form_submit_button("Tra cứu thời tiết", use_container_width=True)

    if favorite_request:
        result = resolve_search("Tên thành phố", input_city=favorite_request)
        if result["status"] == "success":
            st.session_state["last_search"] = result
        else:
            st.sidebar.error(result["message"])

    if submitted:
        result = resolve_search(search_mode, input_city, input_lat, input_lon)
        if result["status"] == "success":
            st.session_state["last_search"] = result
        else:
            st.sidebar.error(result["message"])


def render_location_card(users, search):
    lat = search["lat"]
    lon = search["lon"]

    loc_data = get_location_info(lat, lon)
    if loc_data["status"] != "success":
        st.error(loc_data["message"])
        return None

    display_city = search["label"] or f"{loc_data['city']}, {loc_data['country']}"
    favorite_name = search["city"] or loc_data["city"]

    title_col, action_col = st.columns([1, 0.38])
    with title_col:
        st.subheader("🏙️ Khu vực")
        st.success(f"**{display_city}**")
        st.caption(f"Vĩ độ: {lat:.4f} | Kinh độ: {lon:.4f}")

    with action_col:
        st.write("")
        st.write("")
        if st.session_state["logged_in"]:
            user_favs = current_user(users).get("favorites", [])
            is_saved = favorite_name.casefold() in {item.casefold() for item in user_favs}
            if is_saved:
                st.info("Đã lưu")
            elif st.button("⭐ Lưu", use_container_width=True):
                add_favorite(users, favorite_name)
                st.rerun()
        else:
            st.caption("Đăng nhập để lưu yêu thích.")

    return loc_data


def render_current_weather(lat, lon):
    weather_data = get_current_weather(lat, lon)
    if weather_data["status"] != "success":
        st.error(weather_data["message"])
        return

    st.subheader("🌡️ Thời tiết hiện tại")
    temp_col, humidity_col, wind_col = st.columns(3)
    temp_col.metric("Nhiệt độ", f"{weather_data['temp']}°C")
    humidity_col.metric("Độ ẩm", f"{weather_data['humidity']}%")
    wind_col.metric("Sức gió", f"{weather_data['wind_speed']} m/s")

    desc_col, icon_col = st.columns([1, 0.25])
    with desc_col:
        st.info(f"**Mô tả:** {weather_data['description']}")
    with icon_col:
        icon_url = f"https://openweathermap.org/img/wn/{weather_data['icon']}@2x.png"
        st.image(icon_url, width=82)

    widget_html = f"""
    <div class="weather-widget-grid">
        <div class="weather-widget">
            <div class="weather-widget-title">Cảm giác</div>
            <div class="weather-widget-value">{weather_data['feels_like']}°C</div>
        </div>
        <div class="weather-widget">
            <div class="weather-widget-title">Tầm nhìn</div>
            <div class="weather-widget-value">{weather_data['visibility']} km</div>
        </div>
        <div class="weather-widget">
            <div class="weather-widget-title">Áp suất</div>
            <div class="weather-widget-value">{weather_data['pressure']} hPa</div>
        </div>
        <div class="weather-widget">
            <div class="weather-widget-title">Sáng - Tối</div>
            <div class="weather-widget-value">{weather_data['sunrise']} | {weather_data['sunset']}</div>
        </div>
    </div>
    """
    st.markdown(widget_html, unsafe_allow_html=True)


def render_air_quality(lat, lon):
    aqi_data = get_air_pollution(lat, lon)
    if aqi_data["status"] != "success":
        st.error(aqi_data["message"])
        return

    aqi_val = aqi_data["aqi"]
    st.subheader("😷 Chất lượng không khí")
    st.warning(f"**AQI:** {aqi_val} / 5 - {AQI_LABELS.get(aqi_val, 'Không rõ')}")


def render_map(lat, lon):
    st.subheader("🗺️ Bản đồ thời tiết")
    if not API_KEY:
        st.warning("Chưa cấu hình API Key nên chỉ hiển thị bản đồ nền.")

    weather_map = create_weather_map(lat, lon)
    st_folium(
        weather_map,
        use_container_width=True,
        height=MAP_HEIGHT,
        returned_objects=[],
        key=f"weather_map_{lat:.4f}_{lon:.4f}",
    )


def apply_custom_chart_layout(fig, y_title):
    fig.update_layout(
        xaxis_title="",
        yaxis_title=y_title,
        hovermode="x unified",
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(
        tickformat="%d/%m\n%H:%M",
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(128,128,128,0.2)",
        dtick=43200000,
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="rgba(128,128,128,0.2)")
    return fig


def render_forecast(lat, lon):
    st.divider()
    st.header("📈 Dự báo thời tiết 5 ngày")

    forecast_data = get_weather_forecast(lat, lon)
    if forecast_data["status"] != "success":
        st.error(forecast_data["message"])
        return

    df = pd.DataFrame({
        "Thời gian": pd.to_datetime(forecast_data["times"]),
        "Nhiệt độ (°C)": forecast_data["temps"],
        "Độ ẩm (%)": forecast_data["humidities"],
        "Sức gió (m/s)": forecast_data["winds"],
    })

    plotly_config = {"displayModeBar": False}
    tab1, tab2, tab3 = st.tabs(["🌡️ Nhiệt độ", "💧 Độ ẩm", "💨 Sức gió"])

    with tab1:
        fig_temp = px.line(
            df,
            x="Thời gian",
            y="Nhiệt độ (°C)",
            markers=True,
            line_shape="spline",
            color_discrete_sequence=["#ff4b4b"],
        )
        st.plotly_chart(
            apply_custom_chart_layout(fig_temp, "Nhiệt độ (°C)"),
            use_container_width=True,
            config=plotly_config,
        )

    with tab2:
        fig_humidity = px.area(
            df,
            x="Thời gian",
            y="Độ ẩm (%)",
            color_discrete_sequence=["#00a6d6"],
        )
        st.plotly_chart(
            apply_custom_chart_layout(fig_humidity, "Độ ẩm (%)"),
            use_container_width=True,
            config=plotly_config,
        )

    with tab3:
        fig_wind = px.bar(
            df,
            x="Thời gian",
            y="Sức gió (m/s)",
            color="Sức gió (m/s)",
            color_continuous_scale="Teal",
        )
        st.plotly_chart(
            apply_custom_chart_layout(fig_wind, "Sức gió (m/s)"),
            use_container_width=True,
            config=plotly_config,
        )


def render_results(users):
    search = st.session_state["last_search"]

    if not search:
        st.info("Chọn chế độ tra cứu trong sidebar rồi bấm Tra cứu thời tiết.")
        return

    lat = search["lat"]
    lon = search["lon"]

    left_col, right_col = st.columns([1, 1.15], gap="large")
    with left_col:
        loc_data = render_location_card(users, search)
        if loc_data:
            render_current_weather(lat, lon)
            render_air_quality(lat, lon)

    with right_col:
        render_map(lat, lon)

    render_forecast(lat, lon)


init_session_state()
users_db = load_users()
apply_page_styles()

st.title("🌤️ Ứng dụng MyWeather")
st.markdown("Tra cứu thời tiết, chất lượng không khí và lưu nhanh các địa điểm quan tâm.")

render_sidebar(users_db)
render_results(users_db)
