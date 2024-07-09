# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring

import json
from time import strftime, localtime
import requests

DAPNET_FILENAME = 'dapnet.json'
OPENWEATHERAPI_FILENAME = 'openweatherapi.json'

def read_json(file):
    with open(file, encoding='UTF-8') as f:
        d = json.load(f)
        return d

def send_dapnet_msg(dapnet, msg):
    url = dapnet['url']
    headers = {'Content-type': 'application/json'}
    pkt = {
        "text": msg,
        "callSignNames": dapnet['callSignNames'],
        "transmitterGroupNames": dapnet['transmitterGroupNames'],
        "emergency": dapnet['emergency']
    }
    data = json.dumps(pkt)
    response = requests.post(   url=url,
                                headers=headers,
                                auth= (
                                    dapnet['loginuser'],
                                    dapnet['loginpass']
                                    ),
                                data=data,
                                timeout=10
                                )
    if response.status_code != 201:
        raise requests.ConnectionError("ERROR: failed to POST to hampager")

def owa_getweather(s_owapi):
    excludes = ','.join(s_owapi['exclude'])
    params = {
        "appid": s_owapi['appid'],
        "lat": s_owapi['lat'],
        "lon": s_owapi['lon'],
        "units": s_owapi['units'],
        "lang": s_owapi['lang'],
        "exclude": excludes}

    response = requests.get(url = s_owapi['url'],
                            params=params,
                            timeout=10)
    #print(response)
    #print(response.text)
    if response.status_code != 200:
        raise requests.ConnectionError("ERROR: failed to GET from openweatherapi")

    results = json.loads(response.text)
    #print(json.dumps(results, indent=2))
    return results

def owa_buildmsg(weather):
    dt = strftime('%m/%d %I:%M%p', localtime(weather['current']['dt'])).replace(' 0', ' ')
    summary = weather['daily'][0]['summary']
    temp = weather['current']['temp']
    #tempfeel = weather['current']['feels_like']
    humidity = weather['current']['humidity']
    #condition = weather['current']['weather'][0]['description']
    forecastHigh = weather['daily'][0]['temp']['max']
    forecastLow = weather['daily'][0]['temp']['min']
    #forecastTemp = weather['daily'][0]['temp']['day']
    forecastCondition = weather['daily'][0]['weather'][0]['description']
    forecastRain = weather['daily'][0]['rain']
    
    
    msg = (
        f'{dt} Curr: {temp:0.1f}°F Hum: {humidity:0.0f}%. '
        f'Hi: {forecastHigh:0.1f}°F Lo: {forecastLow:0.1f}°F '
        f'Forecast: {forecastCondition}'
    )
    return msg


def main():
    try:
        s_owapi = read_json(OPENWEATHERAPI_FILENAME)
        s_dapnet = read_json(DAPNET_FILENAME)
        weather = owa_getweather(s_owapi)
        msg = owa_buildmsg(weather)
        print(msg)
        print(f"Length: {len(msg)}")
        #send_dapnet_msg(s_dapnet, 'test msg 7')
    except Exception as e: #pylint: disable=broad-exception-caught
        print(e)

if __name__ == "__main__":
    main()
