import requests
import os
import datetime 
from pathlib import Path
from dotenv import load_dotenv

# Load các biến môi trường từ file .env
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")
API_KEY = os.getenv("OPENWEATHER_API_KEY")


# Hàm 0: Direct Geocoding (Tên thành phố -> Tọa độ)
# Sử dụng: Direct Geocoding API của OpenWeather.
def get_coordinates_by_city(city_name):
    """
    Lấy tọa độ từ tên thành phố.
    Endpoint: Direct Geocoding API
    """
    if not API_KEY:
        return {"status": "error", "message": "Chưa cấu hình API Key."}

    city_name = city_name.strip()
    if not city_name:
        return {"status": "error", "message": "Vui lòng nhập tên thành phố."}

    url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {
        "q": city_name,
        "limit": 1,
        "appid": API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                location = data[0]
                return {
                    "status": "success",
                    "city": location.get("name", city_name),
                    "country": location.get("country", "Unknown"),
                    "state": location.get("state", ""),
                    "lat": location["lat"],
                    "lon": location["lon"],
                }
            return {"status": "error", "message": "Không tìm thấy thành phố này."}
        elif response.status_code == 401:
            return {"status": "error", "message": "Lỗi 401: API Key không hợp lệ."}
        else:
            return {"status": "error", "message": f"Lỗi tìm tọa độ: {response.status_code}"}

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Lỗi kết nối mạng: {str(e)}"}


# Hàm 1: Geocoding (Tọa độ -> Tên thành phố & Country Code)
# Sử dụng: Reverse Geocoding API của OpenWeather.
def get_location_info(lat, lon):
    """
    Lấy tên thành phố và mã quốc gia (ISO 3166-1 alpha-2) từ tọa độ.
    Endpoint: Reverse Geocoding API
    """
    if not API_KEY:
        return {"status": "error", "message": "Chưa cấu hình API Key."}

    # limit=1 để chỉ lấy kết quả chính xác nhất đầu tiên
    url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                city = data[0].get('name', 'Unknown')
                country = data[0].get('country', 'Unknown')
                return {
                    "status": "success", 
                    "city": city, 
                    "country": country
                }
            else:
                return {"status": "error", "message": "Không tìm thấy thông tin cho tọa độ này."}
        elif response.status_code == 401:
            return {"status": "error", "message": "Lỗi 401: API Key không hợp lệ."}
        else:
            return {"status": "error", "message": f"Lỗi hệ thống HTTP: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Lỗi kết nối mạng: {str(e)}"}
    
# Hàm 2: Current Weather (Thời tiết hiện tại)
def get_current_weather(lat, lon):
    """
    Lấy thông tin thời tiết hiện tại dựa trên tọa độ.
    Endpoint: Current Weather API
    """
    if not API_KEY:
        return {"status": "error", "message": "Chưa cấu hình API Key."}

    # Thêm units=metric để lấy độ C, lang=vi để lấy mô tả tiếng Việt
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=vi"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # --- PHẦN XỬ LÝ MỞ RỘNG ---
            # Chuyển đổi timestamp Unix sang định dạng giờ phút địa phương
            sunrise_time = datetime.datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')
            sunset_time = datetime.datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')
            
            return {
                "status": "success",
                "temp": data['main']['temp'],
                "humidity": data['main']['humidity'],
                "wind_speed": data['wind']['speed'],
                "description": data['weather'][0]['description'].capitalize(),
                "icon": data['weather'][0]['icon'],
                # Trích xuất thêm dữ liệu cho Widgets:
                "feels_like": data['main']['feels_like'],
                "pressure": data['main']['pressure'],
                "visibility": data.get('visibility', 0) / 1000, # Đổi từ mét sang km
                "sunrise": sunrise_time,
                "sunset": sunset_time
            }
        else:
            return {"status": "error", "message": f"Lỗi lấy thời tiết: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Lỗi kết nối mạng: {str(e)}"}


# Hàm 3: Air Pollution (Chất lượng không khí)
# Sử dụng: Air Pollution API.
def get_air_pollution(lat, lon):
    """
    Lấy chỉ số chất lượng không khí (AQI).
    Endpoint: Air Pollution API
    """
    if not API_KEY:
        return {"status": "error", "message": "Chưa cấu hình API Key."}

    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # AQI có giá trị từ 1 (Tốt) đến 5 (Rất kém)
            aqi = data['list'][0]['main']['aqi']
            components = data['list'][0]['components'] # Chứa các chất như CO, NO2, O3...
            return {
                "status": "success",
                "aqi": aqi,
                "components": components
            }
        else:
            return {"status": "error", "message": f"Lỗi lấy thông tin AQI: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Lỗi kết nối mạng: {str(e)}"}

# Hàm 4: Forecast (Dự báo 5 ngày / 3 giờ cho phần nâng cao)
# Sử dụng: 5 Day / 3 Hour Forecast API. 
def get_weather_forecast(lat, lon):
    """
    Lấy dự báo thời tiết 5 ngày (mỗi 3 giờ).
    Endpoint: 5 Day / 3 Hour Forecast API
    """
    if not API_KEY:
        return {"status": "error", "message": "Chưa cấu hình API Key."}

    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=vi"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            forecast_list = data['list'] # Chứa 40 phần tử (5 ngày x 8 mốc/ngày)
            
            # Trích xuất dữ liệu thành các danh sách (lists)
            times = [item['dt_txt'] for item in forecast_list]
            temps = [item['main']['temp'] for item in forecast_list]
            humidities = [item['main']['humidity'] for item in forecast_list]
            winds = [item['wind']['speed'] for item in forecast_list]
            
            return {
                "status": "success",
                "times": times,
                "temps": temps,
                "humidities": humidities,
                "winds": winds
            }
        else:
            return {"status": "error", "message": f"Lỗi lấy dự báo: {response.status_code}"}
            
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Lỗi kết nối mạng: {str(e)}"}

# === TEST LOGIC ===
# Chạy thử file này độc lập để kiểm tra hàm hoạt động chưa
if __name__ == "__main__":
    test_lat = 10.7769
    test_lon = 106.7009
    
    print("--- 1. Kiểm tra Vị trí ---")
    print(get_location_info(test_lat, test_lon))

    print("\n--- 1b. Kiểm tra Tọa độ theo Thành phố ---")
    print(get_coordinates_by_city("Ho Chi Minh City"))
    
    print("\n--- 2. Kiểm tra Thời tiết hiện tại ---")
    print(get_current_weather(test_lat, test_lon))
    
    print("\n--- 3. Kiểm tra Chất lượng không khí ---")
    print(get_air_pollution(test_lat, test_lon))

