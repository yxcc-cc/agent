import os
from dotenv import load_dotenv

load_dotenv()

# 通用配置
DB_PATH = "ecommerce.db"

# 🔁 切换模型提供商：支持 "openai" 或 "deepseek"
PROVIDER = "deepseek"

# OpenAI 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = "https://api.openai.com/v1"   # 默认，也可自定义代理

# DeepSeek 配置
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# 自动选择
if PROVIDER == "deepseek":
    API_KEY = DEEPSEEK_API_KEY
    BASE_URL = DEEPSEEK_BASE_URL
    MODEL_NAME = "deepseek-chat"   # DeepSeek-V3，极低成本
else:
    API_KEY = OPENAI_API_KEY
    BASE_URL = OPENAI_BASE_URL
    MODEL_NAME = "gpt-4o-mini"