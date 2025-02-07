from wxauto import *
import time
import requests
import json
import re

# 初始化微信客户端
wx = WeChat()

# 获取最近的会话列表
# sessions = wx.GetSessionList()
# print("最近的会话列表：")
# for session in sessions:
#     print(session)

# 定义 API 请求的 URL 和请求头
url = "http://127.0.0.1:1234/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}

firstLoad = False

# 初始化对话历史
messages = [
    # {"role": "system", "content": "你要一直扮演一名老师的角色，回答家长们的问题，并且向家长夸赞他们的孩子，说出鼓励的话。"}
]

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

def get_api_reply(user_input):
    """
    调用 API 获取回复
    """
    # 将用户输入添加到对话历史
    messages.append({"role": "user", "content": user_input})

    # 定义请求体
    data = {
        "model": "deepseek-r1-distill-qwen-1.5b",
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
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)
        return "抱歉，我暂时无法回复。"

def auto_reply():
    """
    微信自动回复逻辑
    """
    # 获取初始消息记录
    initial_msg = ""
    while True:
        # 获取当前最新消息
        allMessages = wx.GetAllMessage()
        if allMessages:
            # 排除自己发送的消息，找到最后一条他人发送的消息
            last_msg = None
            for msg in reversed(allMessages):
                # 排除已经上一次已经回答的内容
                # 排除自己发送的消息
                # 检查消息内容是否包含 "@乌龟向上爬"
                if msg[0] != "Self" and "@乌龟向上爬" in msg[1]:  # 替换为你的微信昵称
                    last_msg = msg
                    break
            if last_msg and msg[1] != initial_msg:
                # 如果找到符合条件的消息
                sender = last_msg[0]
                content = last_msg[1]
                
                print(f"收到来自 [{sender}] 的触发消息：{content}，对比上一次的数据 >>{initial_msg}=={content}{initial_msg==content}")
                
                # 去掉 "@乌龟向上爬" 触发词
                user_input = content.replace("@乌龟向上爬", "").strip()
                
                # 调用 API 获取回复
                reply = get_api_reply(user_input)
                # print(f"生成回复：{reply}")
                
                # 更新初始消息
                initial_msg = content
                # 发送回复
                # wx.ChatWith(sender)
                reply = f"{reply}@{sender}"
                wx.SendMsg(reply)
                # print(f"已回复 [{sender}]：{reply}")

        # 设置休眠时间，避免占用过多资源
        time.sleep(1)

if __name__ == "__main__":
    print("自动回复机器人正在运行...")
    auto_reply()