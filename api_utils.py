import requests
import json
import re

defult_url = "127.0.0.1:1234"
# defult_url = "172.18.0.157:11434"
# 定义 API 请求的 URL 和请求头
url = f"http://{defult_url}/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}

# 初始化对话历史
messages = [
    {"role": "system", "content": "你是一个群里聊天机器人，回复群里成员说的内容，我已经帮你把他们的内容以'角色说：内容'。你要记住记住说话的人是谁，并且只要回复说话的人"}
]

def get_api_selections():
    """
    获取所有加载好的模型
    """
    try:
        response = requests.get(f"http://{defult_url}/v1/models/")
        if response.status_code == 200:
            models = response.json().get("data", [])
            return models
        else:
            print(f"请求服务失败 status code: {response.status_code}")
            return []
    except requests.RequestException as e:
        print("请求服务失败，请确认是否在LM-Studio中已经打开服务！")
        return []

def remove_think_tags(text):
    """
    去掉 <think> 到 </think> 之间的内容
    """
    return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

def remove_empty_lines(text):
    """
    去掉空行
    """
    # 按行分割，过滤掉空行，然后重新拼接
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def get_api_reply(user_input, model_id):
    """
    调用 API 获取回复
    """
    # 将用户输入添加到对话历史
    messages.append({"role": "user", "content": user_input})

    # 定义请求体
    data = {
        "model": model_id,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": True
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, json=data, stream=True)

    # 检查响应状态码
    if response.status_code == 200:
        # 初始化一个空字符串用于拼接 content
        full_content = ""
        
        # 遍历流式响应的每一行
        for chunk in response.iter_lines():
            if chunk:
                # 解码为字符串
                chunk_str = chunk.decode("utf-8")
                
                # 检查是否以 "data: " 开头
                if chunk_str.startswith("data: "):
                    # 去掉 "data: " 前缀
                    json_str = chunk_str[6:].strip()
                    
                    # 判空处理
                    if not json_str:
                        continue  # 跳过空行
                    
                    try:
                        # 解析 JSON 数据
                        json_data = json.loads(json_str)
                        
                        # 提取 content 字段
                        if "choices" in json_data and len(json_data["choices"]) > 0:
                            content = json_data["choices"][0]["delta"].get("content", "")
                            full_content += content
                            print(content, end="", flush=True)  # 实时打印内容
                    except json.JSONDecodeError:
                        print("Failed to decode JSON:", json_str)
        
        # 去掉 <think> 到 </think> 之间的内容
        full_content = remove_think_tags(full_content)

        # 去掉空行
        full_content = remove_empty_lines(full_content)
        
        # 将助手的回复添加到对话历史
        messages.append({"role": "assistant", "content": full_content})
        return full_content
    else:
        print(f"加载模型失败 status code: {response.status_code}")
        print(response.text)
        return "抱歉，我暂时无法回复。"