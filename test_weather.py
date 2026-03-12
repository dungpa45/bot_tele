import unittest
from unittest.mock import MagicMock, patch
import json

# Giả lập các biến từ var_file để không bị lỗi import
import sys
from types import ModuleType
m = ModuleType("var_file")
m.API_WEATHER = "test_key"
m.API_AIRVISUAL = "test_key"
m.TOKEN = "test_token"
m.degree_sign = "°"
m.starFace = "⭐"
m.neutralFace = "😐"
m.confuseFace = "😕"
m.fearfulFace = "😨"
m.medicalMask = "😷"
m.nauseatedFace = "🤢"
m.thunderstorm = "⚡"
m.drizzle = "🌧️"
m.rain = "☔"
m.snowflake = "❄️"
m.snowman = "☃️"
m.atmosphere = "🌫️"
m.clearSky = "☀️"
m.fewClouds = "🌤️"
m.clouds = "☁️"
m.hot = "🔥"
m.defaultEmoji = "🌈"
sys.modules["var_file"] = m

# Import các hàm cần test sau khi đã giả lập var_file
from weather import getEmoji, temp_K_to_C, data_air, process_message

class TestWeatherBot(unittest.TestCase):

    def test_temp_K_to_C(self):
        self.assertEqual(temp_K_to_C(273.15), 0)
        self.assertEqual(temp_K_to_C(373.15), 100)

    def test_getEmoji(self):
        self.assertEqual(getEmoji(800), "☀️") # clearSky
        self.assertEqual(getEmoji(200), "⚡") # thunderstorm
        self.assertEqual(getEmoji(999), "🌈") # default

    def test_process_message_valid_json(self):
        input_json = '{"key": "value"}'
        expected_output = json.dumps({"key": "value"}, indent=4)
        self.assertEqual(process_message(input_json), expected_output)

    def test_process_message_invalid_json(self):
        input_text = "Not a JSON"
        self.assertEqual(process_message(input_text), input_text)

    def test_data_air_ranges(self):
        # Giả lập các mức AQI khác nhau
        def get_mock_content(aqi):
            return {"data": {"current": {"pollution": {"aqius": aqi}}}}

        # Test mốc 50 (Tốt)
        self.assertIn("Tốt", data_air(get_mock_content(50)))
        
        # Test mốc 51 (Trung bình)
        self.assertIn("Trung bình", data_air(get_mock_content(51)))
        
        # Test mốc 101 (Không tốt cho nhóm nhạy cảm)
        self.assertIn("Không tốt cho nhóm nhạy cảm", data_air(get_mock_content(101)))

        # Test trường hợp content là None (Lỗi fetch API)
        self.assertIn("Không thể lấy dữ liệu", data_air(None))

if __name__ == '__main__':
    unittest.main()
