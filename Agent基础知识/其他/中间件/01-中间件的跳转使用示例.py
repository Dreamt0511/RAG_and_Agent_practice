"""
有些中间件确实不能跳转。关键在于中间件的类型——wrap_model_call 和 wrap_tool_call 属于包裹式钩子（Wrap-style hooks），它们不支持跳转
API参考链接
https://reference.langchain.com/python/langchain/agents/middleware/types/after_model
"""


from langchain.agents.middleware import after_model

@after_model(can_jump_to=["model"])  # 允许跳回模型
def response_format_validator(state, runtime):
    """
    响应格式验证器：如果模型返回空内容，强制重试
    """
    last_message = state["messages"][-1]

    # 检查模型返回是否有效
    if hasattr(last_message, "content") and not last_message.content.strip():
        print("⚠️ 模型返回空内容，请求重试")

        # 返回空状态更新，但指定跳回模型节点
        return {
            "jump_to": "model",  # 关键：跳回模型节点重新生成
            # 可以添加提示消息
            "messages": state["messages"]  # 保持对话历史不变
        }

    return None  # 格式正确，继续执行