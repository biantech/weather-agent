import os
from dotenv import load_dotenv

# 导入核心组件
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent

# 导入工具
from tools.weather_tool import query_weather

# 1. 导入不同的模型类
try:
    from langchain_community.chat_models import ChatTongyi  # 通义千问
except ImportError:
    ChatTongyi = None

try:
    from langchain_openai import ChatOpenAI  # OpenAI
except ImportError:
    ChatOpenAI = None


class WeatherAgent:
    """天气查询智能助手（支持 OpenAI 和 通义千问）"""

    def __init__(self, model_name: str = "qwen-plus"):
        """
        Args:
            model_name: 模型名称
                - OpenAI: 'gpt-4o-mini', 'gpt-3.5-turbo'
                - Qwen:   'qwen-plus', 'qwen-max', 'qwen-turbo'
        """
        load_dotenv()

        # 2. 根据模型名称自动选择对应的 LLM 类
        self.llm = self._get_llm(model_name)

        # 定义工具
        self.tools = [query_weather]

        # 系统提示词保持不变
        system_prompt = """你是一个专业的天气查询助手。

你的职责：
1. 理解用户想查询哪个城市的天气
2. 使用 query_weather 工具获取天气信息
3. 用友好、清晰的方式回复用户

注意事项：
- 如果用户没有指定城市，请询问具体城市
- 如果查询失败，请友好地告知用户
- 可以适当给出穿衣、出行建议"""

        # 创建 Agent
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=system_prompt
        )

    def _get_llm(self, model_name: str):
        """内部方法：根据名称返回正确的 LLM 实例"""

        # 判断是否为通义千问模型 (通常以 qwen 开头)
        if "qwen" in model_name.lower():
            if not ChatTongyi:
                raise ImportError("请安装 langchain-community 和 dashscope 以使用通义千问")

            api_key = os.getenv("DASHSCOPE_API_KEY")
            if not api_key:
                raise ValueError("环境变量 DASHSCOPE_API_KEY 未设置")

            print(f"🚀 正在初始化通义千问模型: {model_name}")
            return ChatTongyi(
                model=model_name,
                temperature=0.7,
                max_tokens=1000,
                dashscope_api_key=api_key
            )

        # 否则默认为 OpenAI
        else:
            if not ChatOpenAI:
                raise ImportError("请安装 langchain-openai 以使用 OpenAI 模型")

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("环境变量 OPENAI_API_KEY 未设置")

            print(f"🚀 正在初始化 OpenAI 模型: {model_name}")
            return ChatOpenAI(
                model=model_name,
                temperature=0.7,
                max_tokens=1000,
                openai_api_key=api_key
            )

    def chat(self, user_input: str) -> str:
        """与 Agent 对话"""
        try:
            result = self.agent.invoke({"messages": [HumanMessage(content=user_input)]})
            return result["messages"][-1].content
        except Exception as e:
            return f"❌ 发生错误：{str(e)}"


# 测试入口
if __name__ == "__main__":
    # ✅ 这里直接传入 qwen 的模型名即可
    agent = WeatherAgent(model_name="qwen-plus")

    test_questions = [
        "北京今天天气怎么样？",
        "上海和广州哪个更热？",
    ]

    for question in test_questions:
        print(f"\n👤 用户：{question}")
        print(f"🤖 助手：{agent.chat(question)}")
        print("-" * 50)