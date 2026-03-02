from langchain_core.prompts import FewShotPromptTemplate,PromptTemplate
from langchain_community.llms.tongyi import Tongyi

#示例数据的模板
example_template = PromptTemplate.from_template("单词{word}，反义词{antonym}")

#示例数据
examples_data = [
    {"word":"big","antonym":"small"},
    {"word":"left","antonym":"right"}
]

few_shot_template = FewShotPromptTemplate(
    example_prompt=example_template,#示例数据的模板
    examples = examples_data,#示例数据
    prefix = "告知我单词的反义词，我提供的示例如下",#示例之前的提示词
    suffix = "回复格式严格基于前面的示例告诉我，{input_word}的反义词是？",#示例之后的提示词
    input_variables = ["input_word"]#声明在前缀和后缀中需要注入的变量名
)
#旧写法
# prompt_text = few_shot_template.format_prompt(input_word = "up").to_string()
#新版写法
prompt_text = few_shot_template.invoke(input={"input_word":"up"}).to_string()
print(prompt_text)

model = Tongyi(model="qwen-plus")
print(model.invoke(input=prompt_text))



"""
from langchain_core.prompts import PromptTemplate
from langchain_community.llms.tongyi import Tongyi

prompt_temp = PromptTemplate.from_template(
    "姓名：{name}，性别：{gender}，年龄：{age}，职业：{profession}基于已有信息继续拓展，写一段求职时的自我介绍"
)

prompt_text = prompt_temp.format_prompt(
    name = "小明",gender = "男", age = 21, profession = "工程师"
)

print(prompt_temp)
print("="*50)
print(prompt_text.text)

model = Tongyi(model="qwen-plus")
res = model.stream(prompt_text)
for chunk in res:
    print(chunk,end = "",flush=True)

"""