import requests

URL = 'https://www.171k.com/login'  # 定义 URL
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0'  # 定义 headers
}
data = {
    '_token': 'pDXeh7QxYdopndeiEWpUcKHwfFgshIbJ35xwH1Ke',
    'uname': 'njjalfdl',
    'password': 'hejia81304002',
    'usecookie': '315360000',
    'action': 'login'
}

try:
    session = requests.session()    # 保持会话状态,session可以保持cookies
    reps = session.post(URL, data=data, headers=headers)
    reps.raise_for_status()
    print("登录成功")
except requests.exceptions.RequestException as e:
    print(f"{e}请求失败!")
