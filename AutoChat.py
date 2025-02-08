from wxauto import *
import time
from api_utils import get_api_reply, get_api_selections


def select_model():
    """
    列出所有可选择的模型，并让用户选择一个
    """
    models = get_api_selections()
    if models:
        print("可选择的模型:")
        for idx, model in enumerate(models):
            print(f"{idx + 1}. {model['id']}")
        
        choice = int(input("请输入选择的模型编号: ")) - 1
        if 0 <= choice < len(models):
            return models[choice]['id']
        else:
            print("无效的选择")
            return None
    else:
        print("未能获取模型列表")
        return None

def auto_reply(model_id):
    """
    微信自动回复逻辑
    """
    # 初始化微信客户端
    wx = WeChat()

    firstLoad = True
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
                # 检查消息内容是否包含 "@wx.nickname"
                if msg[0] != "SYS" and msg[0] != "Time" and msg[0] != "Self" and f"@{wx.nickname}" in msg[1]:
                    last_msg = msg
                    if firstLoad == True:
                        initial_msg = last_msg[1]
                        firstLoad = False
                    break
                # else:
                #     print("过滤消息：", msg[0],msg[1],f"\n包含@{wx.nickname}：", f"@{wx.nickname}" in msg[1])

            if last_msg and msg[1] != initial_msg:
                # 如果找到符合条件的消息
                sender = last_msg[0]
                content = last_msg[1]
                
                print(f"收到来自 [{sender}] 的触发消息：{content}，\n对比上一次的数据 >>\n{initial_msg}=={content}\n对比结果：{initial_msg==content}")
                
                # 去掉 "@nickname" 触发词
                user_input = content.replace(f"@{wx.nickname}", "").strip()
                
                try:
                    # 调用 API 获取回复
                    reply = get_api_reply(user_input, model_id)
                    # print(f"生成回复：{reply}")
                except Exception as e:
                    print("Failed to get reply from API:", e)
                    reply = "抱歉，我暂时无法回复。"
                    break
                
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
    print(f"自动回复机器人正在运行...")
    model_id = select_model()
    if model_id:
        auto_reply(model_id)