"""
天气查询 Agent（LangChain 1.x 最新版）
"""
import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from tools.weather_tool import query_weather


class WeatherAgent02:
    """天气查询智能助手（LangChain 1.x）"""

    def __init__(self, model_name: str = "gpt-4o-mini"):
        # 初始化 LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,  # 创造性程度 0-1
            max_tokens=1000
        )

        # 定义工具
        self.tools = [query_weather]

        # 创建 Agent（LangChain 1.x 新 API）
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt="""你是一个专业的天气查询助手。

你的职责：
1. 理解用户想查询哪个城市的天气
2. 使用 query_weather 工具获取天气信息
3. 用友好、清晰的方式回复用户

注意事项：
- 如果用户没有指定城市，请询问具体城市
- 如果查询失败，请友好地告知用户
- 可以适当给出穿衣、出行建议"""
        )

    def chat(self, user_input: str) -> str:
        """
        与 Agent 对话（LangChain 1.x 调用方式）

        Args:
            user_input: 用户输入

        Returns:
            Agent 回复
        """
        try:
            # LangChain 1.x: 使用 messages 格式
            result = self.agent.invoke({"messages": [HumanMessage(content=user_input)]})
            # 获取最后一条消息的内容
            return result["messages"][-1].content
        except Exception as e:
            return f"❌ 发生错误：{str(e)}"


# 测试
if __name__ == "__main__":
    agent = WeatherAgent()

    # 测试对话
    test_questions = [
        "北京今天天气怎么样？",
        "上海和广州哪个更热？",
        "我想去杭州旅游，那边天气如何？"
    ]

    for question in test_questions:
        print(f"\n👤 用户：{question}")
        print(f"🤖 助手：{agent.chat(question)}")
        print("-" * 50)