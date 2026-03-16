import pytest
import json
import sys
from unittest.mock import MagicMock
from types import ModuleType

# 1. Create mock for var_file
var_mock = ModuleType("var_file")
var_mock.TOKEN = "test_token"
var_mock.API_NINJA = "test_ninja"
var_mock.API_WEATHER = "test_weather"
var_mock.API_AIRVISUAL = "test_air"
var_mock.link_quote = "http://quote.test"
var_mock.link_fact = "http://fact.test"
var_mock.link_shorten = "http://short.test"
var_mock.link_xsmb = "http://xsmb.test"
var_mock.meme_shiba = ["sticker1"]
var_mock.modau = "Hello"
var_mock.l_antrua = ["Com"]
var_mock.link_vnexpress_new = "http://rss.test"
var_mock.link_aws_new = "http://rss.test"
var_mock.link_country = "http://country.test"
var_mock.degree_sign = "°"
var_mock.starFace = "⭐"
var_mock.neutralFace = "😐"
var_mock.confuseFace = "😕"
var_mock.fearfulFace = "😨"
var_mock.medicalMask = ""
var_mock.nauseatedFace = "🤢"
var_mock.thunderstorm = "⚡"
var_mock.drizzle = "🌧️"
var_mock.rain = "☔"
var_mock.snowflake = "❄️"
var_mock.snowman = "☃️"
var_mock.atmosphere = "🌫️"
var_mock.clearSky = "☀️"
var_mock.fewClouds = "🌤️"
var_mock.clouds = "☁️"
var_mock.hot = "🔥"
var_mock.defaultEmoji = "🌈"
sys.modules["var_file"] = var_mock

# 2. Add path to sys.path so we can import real modules
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 3. Import functions to test
from weather import getEmoji, temp_K_to_C, data_openweather, data_air
from linhtinh_aws_lambda import get_day_name, validate_ip_address, translate_vn, lambda_handler

# --- Test Weather Bot Functions ---

def test_temp_K_to_C():
    assert temp_K_to_C(273.15) == 0
    assert temp_K_to_C(373.15) == 100

@pytest.mark.parametrize("weather_id, expected_emoji", [
    (800, "☀️"), # clearSky
    (200, "⚡"), # thunderstorm
    (500, "☔"), # rain
    (999, "🌈"), # default
])
def test_get_emoji(weather_id, expected_emoji):
    assert getEmoji(weather_id) == expected_emoji

def test_data_openweather_success(mocker):
    mock_content = MagicMock()
    mock_content.json.return_value = {
        "weather": [{"id": 800, "main": "Clear", "description": "trời quang"}],
        "main": {"temp": 300, "feels_like": 301, "temp_min": 299, "temp_max": 302, "humidity": 50},
        "wind": {"speed": 5},
        "sys": {"sunrise": 1600000000, "sunset": 1600050000}
    }
    result = data_openweather(mock_content)
    assert "☀️" in result
    assert "trời quang" in result
    assert "26°" in result

def test_data_openweather_none():
    assert "❌ Không thể lấy dữ liệu" in data_openweather(None)

@pytest.mark.parametrize("aqi, expected_status", [
    (10, "Tốt"),
    (50, "Tốt"),
    (75, "Trung bình"),
    (100, "Trung bình"),
    (125, "Không tốt cho nhóm nhạy cảm"),
    (150, "Không tốt cho nhóm nhạy cảm"),
    (175, "Có hại cho sức khỏe"),
    (250, "Rất có hại cho sức khỏe"),
    (400, "Nguy hại"),
])
def test_data_air_ranges(aqi, expected_status):
    content = {"data": {"current": {"pollution": {"aqius": aqi}}}}
    assert expected_status in data_air(content)

def test_data_air_none():
    assert "❌ Không thể lấy dữ liệu" in data_air(None)

# --- Test Lambda Bot Functions ---

def test_get_day_name():
    assert get_day_name("12-03-2026") == "Thursday"

@pytest.mark.parametrize("ip, expected", [
    ("192.168.1.1", True),
    ("10.0.0.0/24", True),
    ("255.255.255.255", True),
    ("300.1.1.1", False),
    ("not.an.ip", False),
])
def test_validate_ip_address(ip, expected):
    assert validate_ip_address(ip) == expected

def test_translate_vn_success(mocker):
    mock_trans = mocker.patch('linhtinh_aws_lambda.Translator')
    mock_trans.return_value.translate.return_value.text = "Xin chào"
    assert translate_vn("Hello") == "Xin chào"

def test_translate_vn_failure(mocker):
    mocker.patch('linhtinh_aws_lambda.Translator', side_effect=Exception("Fail"))
    assert translate_vn("Hello") == "Hello"

def test_lambda_handler_quote(mocker):
    mocker.patch('linhtinh_aws_lambda.get_n_send_quote')
    event = {
        "body": json.dumps({
            "message": {"chat": {"id": 123}, "text": "/quote"}
        })
    }
    response = lambda_handler(event, None)
    assert response["statusCode"] == 200

def test_lambda_handler_edited(mocker):
    mock_send = mocker.patch('linhtinh_aws_lambda.send_text')
    event = {
        "body": json.dumps({
            "edited_message": {"chat": {"id": 123}, "text": "hey"}
        })
    }
    lambda_handler(event, None)
    mock_send.assert_called_once_with("edited_mess", 123)
