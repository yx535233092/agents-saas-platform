from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_openai import ChatOpenAI
import json


class State(TypedDict):
    message: str
    response: str


model = ChatOpenAI(
    model="xiaomi/mimo-v2-flash:free",
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)


def call_model(state: State):
    response = model.invoke([{"role": "user", "content": state["message"]}])
    return {"response": response.content}


def chat_flow(state: State):
    response = call_model(state)
    return response


workflow = StateGraph(State)
workflow.add_node("chat", chat_flow)
workflow.set_entry_point("chat")
workflow.add_edge("chat", END)

app = workflow.compile()
result = app.invoke({"message": "你好"})
print(json.dumps(result, ensure_ascii=False, indent=4))
