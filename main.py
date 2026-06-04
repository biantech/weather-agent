"""
天气查询助手 - 入口文件
"""
import logging

from agent.weather_agent import WeatherAgent

# Module-level logger; basicConfig is applied in __main__ so this module
# can also be safely imported without side-effecting the root logger.
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    # User-facing interactive text — kept as print intentionally
    print("🌤️  欢迎使用天气查询助手！")
    print("输入城市名称查询天气，输入 'quit' 退出")
    print("=" * 50)

    # 创建 Agent
    logger.info("Initializing WeatherAgent model=qwen-plus")
    agent = WeatherAgent(model_name="qwen-plus")
    logger.info("WeatherAgent ready")

    # 交互循环
    while True:
        try:
            user_input = input("\n👤 你：").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "退出"]:
                print("👋 再见！祝你有美好的一天！")
                logger.info("User exited normally")
                break

            # 获取 Agent 回复
            logger.debug("Invoking agent: input=%r", user_input)
            response = agent.chat(user_input)
            logger.debug("Agent responded: length=%d", len(response))

            # Core interaction text — kept as print for clean UX
            print(f"\n🤖 助手：{response}")

        except KeyboardInterrupt:
            print("\n👋 再见！")
            logger.info("Session terminated by KeyboardInterrupt")
            break
        except Exception as e:
            logger.error("Unexpected error in main loop: %s", e, exc_info=True)


if __name__ == "__main__":
    # Configure root logger here so weather_tool.py loggers share the same
    # handler and format without duplicating basicConfig calls.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()