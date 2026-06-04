"""
天气查询工具
基于和风天气 API（API Host 私有域名）
"""
import logging
import os
from typing import Optional

import requests
from dotenv import load_dotenv
from langchain.tools import tool

# Load .env at module import so this file also works when run standalone
load_dotenv()

logger = logging.getLogger(__name__)


class WeatherAPI:
    """和风天气 API 封装（API Host 私有域名）"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("WEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("缺少 WEATHER_API_KEY，请在 .env 中配置或显式传入")
        # 私有 API Host：/geo/v2/* 走 GeoAPI，/v7/* 走 Weather API
        self.base_url = "https://nh2tuqha4m.re.qweatherapi.com"

    def get_city_id(self, city_name: str) -> Optional[str]:
        """获取城市 ID"""
        url = f"{self.base_url}/geo/v2/city/lookup"
        params = {"location": city_name, "key": self.api_key, "number": 1}
        logger.debug("GeoAPI request url=%s location=%s", url, city_name)

        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.Timeout:
            logger.error("GeoAPI timeout, city=%s", city_name)
            return None
        except requests.ConnectionError as e:
            logger.error("GeoAPI connection error: %s", e)
            return None
        except requests.HTTPError as e:
            body = e.response.text[:200] if e.response is not None else ""
            status = e.response.status_code if e.response is not None else "N/A"
            logger.error("GeoAPI HTTP error: status=%s body=%s", status, body)
            return None
        except ValueError as e:
            logger.error("GeoAPI JSON decode error: %s", e)
            return None

        code = data.get("code")
        if code == "200" and data.get("location"):
            city_id = data["location"][0]["id"]
            logger.debug("GeoAPI matched city=%s -> id=%s", city_name, city_id)
            return city_id
        logger.warning("GeoAPI non-success: code=%s city=%s", code, city_name)
        return None

    def get_weather(self, city_name: str) -> dict:
        """获取天气信息"""
        city_id = self.get_city_id(city_name)
        if not city_id:
            return {"error": f"未找到城市：{city_name}"}

        # Note: under API Host, Weather API path requires the /v7 version prefix
        weather_url = f"{self.base_url}/v7/weather/now"
        params = {"location": city_id, "key": self.api_key}
        logger.debug("Weather request url=%s location=%s", weather_url, city_id)

        try:
            response = requests.get(weather_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
        except requests.Timeout:
            logger.error("Weather API timeout, city=%s", city_name)
            return {"error": "查询超时，请稍后重试"}
        except requests.ConnectionError as e:
            logger.error("Weather API connection error: %s", e)
            return {"error": "网络连接失败"}
        except requests.HTTPError as e:
            body = e.response.text[:200] if e.response is not None else ""
            status = e.response.status_code if e.response is not None else "N/A"
            logger.error("Weather API HTTP error: status=%s body=%s", status, body)
            return {"error": f"HTTP {status}"}
        except ValueError as e:
            logger.error("Weather API JSON decode error: %s", e)
            return {"error": "响应解析失败"}

        code = data.get("code")
        if code == "200":
            now = data.get("now", {})
            return {
                "city": city_name,
                "temperature": now.get("temp", "N/A"),
                "feels_like": now.get("feelsLike", "N/A"),
                "condition": now.get("text", "N/A"),
                "wind_direction": now.get("windDir", "N/A"),
                "wind_scale": now.get("windScale", "N/A"),
                "humidity": now.get("humidity", "N/A"),
                "update_time": data.get("updateTime", "N/A")
            }
        logger.warning("Weather API non-success: code=%s city=%s", code, city_name)
        return {"error": f"API 错误：{code}"}


@tool
def query_weather(city_name: str) -> str:
    """
    查询指定城市的实时天气

    Args:
        city_name: 城市名称，如"北京"、"上海"

    Returns:
        格式化的天气信息字符串
    """
    api = WeatherAPI()
    result = api.get_weather(city_name)

    if "error" in result:
        return f"❌ {result['error']}"

    # 格式化输出
    output = f"""
🌤️  {result['city']} 实时天气

🌡️  温度：{result['temperature']}°C（体感：{result['feels_like']}°C）
☁️  天气：{result['condition']}
💨  风向：{result['wind_direction']} {result['wind_scale']}级
💧  湿度：{result['humidity']}%
🕐  更新时间：{result['update_time']}
"""
    return output.strip()


# 测试
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    weather = query_weather.invoke("北京")
    print(weather)