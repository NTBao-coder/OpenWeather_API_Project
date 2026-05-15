import unittest
from api_modules import (
    get_location_info, 
    get_current_weather, 
    get_air_pollution, 
    get_coordinates_by_city
)

class TestWeatherAPI(unittest.TestCase):

    # --- TEST CASES CHO TỌA ĐỘ HỢP LỆ (Happy Path) ---
    def test_valid_coordinates_location(self):
        """Kiểm tra dịch vụ giải mã địa lý ngược với tọa độ TP.HCM."""
        result = get_location_info(10.7769, 106.7009)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["country"], "VN")
        self.assertIn("Ho Chi Minh", result["city"]) # Có thể trả về 'Ho Chi Minh City' hoặc 'Ho Chi Minh'

    def test_valid_coordinates_weather(self):
        """Kiểm tra dịch vụ thời tiết với tọa độ hợp lệ."""
        result = get_current_weather(10.7769, 106.7009)
        self.assertEqual(result["status"], "success")
        self.assertIn("temp", result)
        self.assertIn("humidity", result)

    def test_valid_coordinates_aqi(self):
        """Kiểm tra dịch vụ chất lượng không khí với tọa độ hợp lệ."""
        result = get_air_pollution(10.7769, 106.7009)
        self.assertEqual(result["status"], "success")
        self.assertIn("aqi", result)

    # --- TEST CASES CHO CHUỖI ĐẦU VÀO THÀNH PHỐ (Edge Cases) ---
    def test_valid_city_name(self):
        """Kiểm tra tìm tọa độ bằng tên thành phố đúng."""
        result = get_coordinates_by_city("Hanoi")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["country"], "VN")
        self.assertIsInstance(result["lat"], float)

    def test_invalid_city_name(self):
        """Kiểm tra tìm tọa độ với tên thành phố không tồn tại (Edge Case)."""
        result = get_coordinates_by_city("ThanhPhoKhongTonTai123")
        self.assertEqual(result["status"], "error")
        self.assertIn("Không tìm thấy", result["message"])

    def test_empty_city_name(self):
        """Kiểm tra tìm tọa độ với chuỗi rỗng hoặc chỉ chứa khoảng trắng (Edge Case)."""
        result = get_coordinates_by_city("   ")
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Vui lòng nhập tên thành phố.")

if __name__ == "__main__":
    unittest.main()