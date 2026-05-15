# MyWeather Application

## 1. Mô tả dự án
Dự án xây dựng ứng dụng thời tiết (MyWeather) sử dụng **Streamlit** cho giao diện người dùng và tích hợp dữ liệu từ hệ thống OpenWeather API. Toàn bộ quy trình xây dựng, thiết kế kiến trúc và triển khai được tài liệu hóa chi tiết trong báo cáo Notebook.

## 2. Các tính năng cốt lõi (Core Features)
Ứng dụng đáp ứng các yêu cầu kỹ thuật tối thiểu sau:
* **Định vị không gian:** Trích xuất tên thành phố và mã quốc gia (chuẩn ISO 3166-1 alpha-2) từ tọa độ thu thập qua Google Maps.
* **Thời tiết thời gian thực:** Truy xuất và hiển thị thông tin thời tiết hiện tại cho dữ liệu đầu vào.
* **Bản đồ thời tiết (Weather Maps):** Render bản đồ không gian có phủ tối thiểu một lớp dữ liệu (Layer) chuyên dụng như: Nhiệt độ (Temperature), Gió (Wind), Mây (Clouds), hoặc Lượng mưa (Precipitation).
* **Chỉ số không khí:** Tra cứu và hiển thị chất lượng không khí (AQI).

## 3. Các tính năng nâng cao (Advanced Features)
* **Weather Widgets:** Tích hợp các module giao diện thời tiết nhúng (widgets).
* **Phân tích Dự báo:** Biểu diễn trực quan (Biểu đồ) các thông số nhiệt độ, độ ẩm, và sức gió dựa trên dữ liệu dự báo 5 ngày / 3 giờ (5 Day / 3 Hour Forecast).
* **Quản lý người dùng:** Xây dựng luồng quản lý tài khoản và lưu trữ danh sách các thành phố quan tâm.

## 4. Cấu trúc bài nộp (Submission Structure)
Hệ thống mã nguồn và tài liệu được tổ chức theo chuẩn bao gồm:

* **Báo cáo kỹ thuật (`.ipynb`):** Notebook chứa đầy đủ các khía cạnh:
    * Mô tả mục tiêu và phân tích yêu cầu.
    * Kiến trúc tổng quát (Sơ đồ Pipeline).
    * Quá trình thiết lập và cấu hình API.
    * Thiết kế server và thực thi ứng dụng.
    * Kiểm thử cơ bản hoạt động (Unit/Integration Test).
    * Tài liệu hóa các chức năng mở rộng.
* **Mã nguồn thực thi (`.py`):** Chứa file khởi chạy ứng dụng chính và các module logic được tách riêng.
* **Môi trường (`requirements.txt`):** Danh sách toàn bộ thư viện phụ thuộc để tái tạo môi trường.

## 5. Hướng dẫn thiết lập môi trường (Apple Silicon / Unix)
Hệ thống yêu cầu môi trường Python cô lập (khuyến nghị Python 3.10) nhằm đảm bảo tính tương thích của các thư viện lõi (như `protobuf`, `folium`).

```bash
# 1. Khởi tạo và kích hoạt môi trường bằng micromamba
micromamba create -n weather_env python=3.10 -c conda-forge
micromamba activate weather_env

# 2. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt

# 3. Thiết lập biến môi trường
# Tạo file .env tại thư mục gốc và cung cấp khóa API:
# OPENWEATHER_API_KEY=your_api_key_here

# 4. Khởi chạy ứng dụng
python -m streamlit run main_app.py
```
