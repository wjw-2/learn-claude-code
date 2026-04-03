import requests
import json
import sys

# 设置标准输出编码为UTF-8（Windows兼容）
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

def get_beijing_weather():
    """
    获取北京天气信息
    使用 wttr.in 免费天气服务
    """
    try:
        # wttr.in 是一个免费的天气服务，支持城市名称查询
        url = "https://wttr.in/Beijing?format=j1"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # 解析天气数据
            if 'current_condition' in data and len(data['current_condition']) > 0:
                current = data['current_condition'][0]
                location = data['request'][0] if 'request' in data and len(data['request']) > 0 else {'query': 'Beijing'}
                
                print(f"[Location] {location.get('query', 'Beijing')}")
                print(f"[Date] {current.get('localObsDateTime', 'N/A')}")
                print(f"[Temperature] {current.get('temp_C', 'N/A')}°C (Feels like: {current.get('FeelsLikeC', 'N/A')}°C)")
                print(f"[Weather] {current.get('weatherDesc', [{'value': 'N/A'}])[0].get('value', 'N/A')}")
                print(f"[Humidity] {current.get('humidity', 'N/A')}%")
                print(f"[Wind Speed] {current.get('windspeedKmph', 'N/A')} km/h")
                print(f"[Wind Direction] {current.get('winddir16Point', 'N/A')}")
                
                # 今日预报
                if 'weather' in data and len(data['weather']) > 0:
                    today = data['weather'][0]
                    print(f"\n[Today's Forecast]:")
                    print(f"   Max Temperature: {today.get('maxtempC', 'N/A')}°C")
                    print(f"   Min Temperature: {today.get('mintempC', 'N/A')}°C")
                    if 'astronomy' in today and len(today['astronomy']) > 0:
                        print(f"   Sunrise: {today['astronomy'][0].get('sunrise', 'N/A')}")
                        print(f"   Sunset: {today['astronomy'][0].get('sunset', 'N/A')}")
                    else:
                        print(f"   Sunrise: N/A")
                        print(f"   Sunset: N/A")
                else:
                    print(f"\n[Today's Forecast]: N/A")
            else:
                print("[ERROR] No current weather data available")
                print("[INFO] Try using alternative weather service")
            
        else:
            print(f"[ERROR] Request failed with status code: {response.status_code}")
            print("[INFO] Try checking your internet connection or use alternative API")
            
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network request error: {e}")
        print("[INFO] Please check your internet connection")
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON parsing error: {e}")
        print("[INFO] API response format may have changed")
    except KeyError as e:
        print(f"[ERROR] Data parsing error: Key {e} not found")
        print("[INFO] API response structure may have been updated")
    except Exception as e:
        print(f"[ERROR] Unknown error: {e}")

if __name__ == "__main__":
    print("[Weather Tool] Beijing Weather Query")
    print("=" * 50)
    get_beijing_weather()
    print("=" * 50)
    print("[SUCCESS] Query completed!")
