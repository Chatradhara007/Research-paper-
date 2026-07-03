import os
from dotenv import load_dotenv
load_dotenv()

from core.chat import chat_with_memory
import traceback

try:
    print(chat_with_memory("hello"))
except Exception as e:
    traceback.print_exc()
