import os
import dotenv
from openai import OpenAI


class QwenLLM:
    def __init__(self):
        dotenv.load_dotenv('asst.env')
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_base_url = os.getenv('API_BASE_URL')
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base_url
        )

    def inference(self,
                  messages=None,
                  model="qwen-plus",
                  enable_search=False,
                  enable_thinking=False,
                  stream=False,
                  max_tokens=2048,
                  temperature=0.7,
                  ):
        if messages is None:
            messages = []
        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=stream,  # 是否流式返回
                # 扩展配置
                extra_body={
                    "enable_search": enable_search,  # 联网搜索
                    "enable_thinking": enable_thinking,  # 深度思考
                },
                # 控制参数
                max_tokens=max_tokens,
                temperature=temperature,
            )
            if not stream:
                answer = completion.choices[0].message.content
            else:
                return completion
        except Exception as e:
            answer = f"错误! {e}"
            print(f"错误信息：{e}")
        return answer
