from langchain_core.prompts import PromptTemplate
from langchain_community.llms.tongyi import Tongyi

prompt_temp = PromptTemplate.from_template(
    "姓名：{name}，性别：{gender}，年龄：{age}，职业：{profession}基于已有信息继续拓展，写一段求职时的自我介绍"
)

prompt_text = prompt_temp.format_prompt(
    name = "小明",gender = "男", age = 21, profession = "工程师"
)
"""
print(prompt_temp)
print("="*50)
print(prompt_text.text)
"""

model = Tongyi(model="qwen-plus")
res = model.stream(prompt_text)
for chunk in res:
    print(chunk,end = "",flush=True)
