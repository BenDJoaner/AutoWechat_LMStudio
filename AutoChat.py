from wxauto import *
import time
from api_utils import get_api_reply, get_api_selections
import threading

# 初始化微信客户端
wx = WeChat()

firstLoad = True
nickname = wx.nickname  # 获取微信昵称

# 定义过滤条件
filter_conditions = ["Recall", "SYS", "Time", "Self"]

def should_filter_message(msg_type, msg_content):
    """
    判断消息类型是否应该被过滤
    """
    return msg_type in filter_conditions or msg_content.strip() == ""

def select_model():
    """
    列出所有可选择的模型，并让用户选择一个
    """
    models = get_api_selections()
    if models:
        print("可选择的模型:")
        for idx, model in enumerate(models):
            print(f"{idx + 1}. {model['id']}")
        
        while True:
            try:
                choice = int(input("请输入选择的模型编号: ")) - 1
                if 0 <= choice < len(models):
                    return models[choice]['id']
                else:
                    print("无效的选择，请输入有效的模型编号")
            except ValueError:
                print("输入无效，请输入数字")
    else:
        print("未能获取模型列表")
        return None

def check_new_message(data):
    # 获取第一个键
    keys = list(data.keys())
    for key in keys:
        value_list = data[key]
        for data in value_list:
            sender = data.info[0]
            print(f"条目：{sender} >> {data.info[1]}")
            # print(f"第一个子列表的第一个元素是：{sender} >>> {sender in filter_conditions}")
            if sender in filter_conditions:
                print(f"排除自己和系统消息 >>>> {sender}")
                continue
            else:
                print(f"检测到符合条件的消息 >>>> {sender}")
                return True

    print(f"未找到符合条件的消息 >>>> {data}")
    return False

def auto_reply(model_id, filter_nickname):
    """
    微信自动回复逻辑
    """
    print(f"已选择模型：{model_id}\n\t过滤昵称：{filter_nickname}\n\t开始监听并自动回复消息...")
    global firstLoad
    # 获取初始消息记录
    # initial_msg = ""
    while True:
        # 检查是否有新消息
        newMessagesCheck = wx.CheckNewMessage()
        if newMessagesCheck == False:
            continue
        # 获取下一条最新消息的来源
        nextMessage = wx.GetNextNewMessage()
        if nextMessage and check_new_message(nextMessage) == False:
            print("排除自己和系统消息 >>>> ", nextMessage)
            continue
        # 获取当前聊天框所有消息
        allMessages = wx.GetAllMessage()
        if allMessages:
            # 排除自己发送的消息，找到最后一条他人发送的消息
            last_msg = None
            # print(f"该聊天框所有消息：\n\t{allMessages}")
            for msg in reversed(allMessages):
                # 排除已经上一次已经回答的内容
                # 排除自己发送的消息
                # 检查消息内容是否包含 "@nickname"
                if not should_filter_message(msg[0], msg[1]) and (not filter_nickname or f"@{nickname}" in msg[1]):
                    last_msg = msg
                    break

            # if last_msg != None and last_msg[1] != initial_msg:
            if last_msg != None:
                # 如果找到符合条件的消息
                sender = last_msg[0]
                content = last_msg[1]
                
                print(f"收到来自 [{sender}] 的触发消息：{content}")
                
                # 去掉 "@nickname" 触发词
                user_input = content.replace(f"@{nickname}", "").strip() if filter_nickname else content.strip()
                
                if filter_nickname:
                    user_input = f"{sender}说：{user_input}"
                try:
                    # 调用 API 获取回复
                    reply = get_api_reply(user_input, model_id)
                    # print(f"生成回复：{reply}")
                except Exception as e:
                    print("Failed to get reply from API:", e)
                    reply = "抱歉，我暂时无法回复。"
                    break
                
                # 更新初始消息
                # initial_msg = content
                # 发送回复
                # wx.ChatWith(sender)
                if filter_nickname:
                    reply = f"{reply}@{sender}"
                wx.SendMsg(reply)
                # print(f"已回复 [{sender}]：{reply}")
            # else:
            #     print("未找到符合条件的消息", last_msg[1], initial_msg, last_msg[1] == initial_msg)

        # 设置休眠时间，避免占用过多资源
        time.sleep(3)

def select_filter_option():
    """
    选择是否过滤 @nickname
    """
    print(f"是否需要@{nickname}时候才触发自动回复？")
    print("1. 过滤")
    print("2. 不过滤")
    choice = None

    def auto_select():
        nonlocal choice
        time.sleep(5)
        if choice is None:
            choice = 1
            print("\n5秒未选择，自动选择: 1. 过滤")

    threading.Thread(target=auto_select).start()
    while True:
        choice = input("请输入选择的编号 (5秒后自动选择1): ")
        if choice.isdigit() and int(choice) in [1, 2]:
            return int(choice)
        else:
            print("无效的选择，请输入 1 或 2")

if __name__ == "__main__":
    print(f"自动回复机器启动...")
    model_id = select_model()
    if model_id:
        filter_option = select_filter_option()
        filter_nickname = (filter_option == 1)
        auto_reply(model_id, filter_nickname)