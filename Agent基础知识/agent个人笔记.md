一.如果工具具有精心选择的名称、描述和args_schema，模型将表现得更好。
LangChain支持从以下几种方式创建工具
1.Tool装饰器的函数---这是最常见的。(80%的场景用装饰器（快速、简单）)
2.通过从BaseTool 子类化-这是最灵活的方法，它提供了最大的控制程度，但代价是需要付出更多的努力和编写更多的代码。(20%的关键工具用BaseTool（可靠、可控）,生产环境使用)
3.从MCP的服务端获得工具
视频链接：
【【AI大模型】🚀全网最新版“LangChain1.0✚LangGraph1.0”企业级Agent智能体开发实战教程！（马士兵-码士集团）】
https://www.bilibili.com/video/BV18KULB5EcP?p=15&vd_source=8270dac49dcebe01a55868cae7bc3c79

二.PostgreSQL相关：
1.在 psql 中，可以使用元命令 \dt 来列出当前数据库里的所有表
2。\q 断开连接

三、为了防止输入给大模型的参考文档太长溢出模型的上下文窗口，要在发送给大模型之前大概检查一下输入文本的token数
可以使用官方Tokenizer
import tiktoken  # OpenAI的tokenizer