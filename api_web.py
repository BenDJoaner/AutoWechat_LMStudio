import requests
from bs4 import BeautifulSoup

def search_baidu(query):
    # 百度搜索的URL
    url = f"https://www.baidu.com/s?wd={query}"
    
    # 发送HTTP请求
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    # 检查请求是否成功
    if response.status_code != 200:
        print("请求失败，状态码:", response.status_code)
        return
    
    # 解析网页内容
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 提取搜索结果
    results = soup.find_all('div', class_='result c-container new-pmd')
    
    # 打印搜索结果
    for i, result in enumerate(results, 1):
        title = result.find('h3').get_text()
        link = result.find('a')['href']
        print(f"{i}. {title}\n   {link}\n")

if __name__ == "__main__":
    query = input("请输入要搜索的问题: ")
    search_baidu(query)