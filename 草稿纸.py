from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
from langchain_community.llms.tongyi import Tongyi

example_template = PromptTemplate.from_template("单词{word}，反义词{antonym}")

examples_data = [
    {"word": "big", "antonym": "small"},
    {"word": "left", "antonym": "right"}
]

few_shot_template = FewShotPromptTemplate(
    example_prompt=example_template,
    examples=examples_data,
    prefix="告知我单词的反义词，我提供的示例如下",
    suffix="回复格式按照前面的示例告诉我（如果遇到不太符合的情况请回复暂未知晓，不要做过多解释），{input_word}的反义词是？",
    input_variables=["input_word"]
)


prompt_text = few_shot_template.invoke(input={"input_word":"down"}).to_string()
model = Tongyi(model= "qwen-max")
print(prompt_text)
print(model.invoke(prompt_text))