import os
import sys
from dotenv import load_dotenv

# 1. 【非常重要】必须在导入本地模块之前，先加载 .env 文件！
# 否则 loop.py 等文件在初始化 OpenAI 客户端时会读不到环境变量。
load_dotenv()

if not os.getenv("DASHSCOPE_API_KEY"):
    print("错误: 未找到 DASHSCOPE_API_KEY 环境变量！")
    print("请先在 .env 文件中配置您的阿里云百炼 API Key。")
    sys.exit(1)

# 2. 确保环境变量加载完毕后，再导入本地模块
from loop import agent_loop

def main():
    print("="*50)
    print("🤖 欢迎使用基于 Qwen 的 Nano Claude Code Agent")
    print("架构参考: shareAI-lab/learn-claude-code")
    print("="*50)
    print("输入 'exit' 或 'quit' 退出。\n")

    # 初始化对话上下文
    messages = [
        {
            "role": "system", 
            "content": (
                "你是一个强大的 AI 编程助手和系统控制终端。\n"
                "你可以使用 bash/read_file/write_file/edit_file 完成工程任务。\n"
                "复杂任务先用 todo；耗时命令优先 run_background；分支探索优先 delegate_task。\n"
                "需要多任务依赖时使用 dag_create/dag_update/dag_list。\n"
                "需要技能模板时使用 load_skill；需要团队协作时使用 team_* 与 protocol_*。\n"
                "需要隔离工作目录时使用 worktree_bind/worktree_get/worktree_unbind。\n"
                "在回答问题时，请一步步思考，利用工具去验证你的想法。"
            )
        }
    ]

    while True:
        try:
            # 接收用户输入
            query = input("😎 用户> ")
            if query.strip().lower() in ['exit', 'quit']:
                print("👋 再见！")
                break
            if not query.strip():
                continue

            print("🤖 Agent 思考中...")
            
            # 将任务丢进核心 ReAct 循环
            response = agent_loop(query, messages)
            
            # 打印大模型最终得出的回答
            print(f"\n💡 最终回复:\n{response}\n")
            print("-" * 50)
            
        except KeyboardInterrupt:
            # 允许使用 Ctrl+C 优雅退出
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 运行时发生错误: {e}\n")

if __name__ == "__main__":
    main()
