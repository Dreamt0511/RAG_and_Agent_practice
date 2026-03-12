from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated
from langgraph.graph.message import add_messages


# 定义状态
class OrderProcessingState(TypedDict):
    order_id: str
    status: str
    actions: Annotated[List[str], add_messages]


# 定义节点函数
def validate_order(state: OrderProcessingState):
    if not state.get("order_id"):
        raise ValueError("Invalid order ID")
    return {
        "status": "validated",
        "actions": ["Order validated"]
    }


def check_inventory(state: OrderProcessingState):
    return {
        "status": "inventory_checked",
        "actions": ["Inventory checked"]
    }


def confirm_payment(state: OrderProcessingState):
    return {
        "status": "payment_confirmed",
        "actions": ["Payment confirmed"]
    }


# 构建图
def build_order_graph():
    graph = StateGraph(OrderProcessingState)

    graph.add_node("validate", validate_order)
    graph.add_node("inventory", check_inventory)
    graph.add_node("payment", confirm_payment)

    graph.set_entry_point("validate")
    graph.add_edge("validate", "inventory")
    graph.add_edge("inventory", "payment")
    graph.add_edge("payment", END)

    return graph.compile()


# 执行
if __name__ == "__main__":
    app = build_order_graph()

    # === 可视化部分 ===
    # 方法1：保存为 PNG（需要安装 grandalf: pip install grandalf）
    try:
        png_data = app.get_graph().draw_mermaid_png()
        with open("order_workflow.png", "wb") as f:
            f.write(png_data)
        print("流程图已保存到 order_workflow.png")
    except Exception as e:
        print(f"PNG生成失败: {e}")

    # 方法2：打印 ASCII 图
    print("\n=== ASCII 流程图 ===")
    print(app.get_graph().draw_ascii())

    # 执行图
    result = app.invoke({
        "order_id": "ORD12345",
        "status": "",
        "actions": []
    })

    print("\nExecution Trace:")
    for action in result["actions"]:
        print(f"- {action}")