import chainlit as cl
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain.schema.runnable.config import RunnableConfig

from src.utils.graph_utils import _create_graph_builder


@cl.on_message
async def on_message(msg: cl.Message):
    config = {"configurable": {"thread_id": cl.context.session.id}}
    answer_prefix_tokens = ["Final", " Answer", "Final Answer:"]
    cb = cl.LangchainCallbackHandler(
        stream_final_answer=True,
        answer_prefix_tokens=answer_prefix_tokens,)
    final_answer = cl.Message(content="")

    inputs = {
        "question": msg.content
    }
    builder = _create_graph_builder()

    with SqliteSaver.from_conn_string(":memory:") as memory:
        graph_with_memory = builder.compile(checkpointer=memory)
        for msg, metadata in graph_with_memory.stream(inputs,
                                                      stream_mode="messages",
                                                      config=RunnableConfig(callbacks=[cb], **config)):
            print("-------------")
            print(msg)
            if (
                    msg.content
                    and not isinstance(msg, HumanMessage)
                    and metadata["langgraph_node"] == "answer_node"
            ):
                await final_answer.stream_token(msg.content)

    await final_answer.send()

    # thread = {"configurable": {"thread_id": 141}}
    # with SqliteSaver.from_conn_string(":memory:") as memory:
    #     graph_with_memory = builder.compile(checkpointer=memory)
    #     for output in graph_with_memory.stream(inputs, thread):
    #         print(output)
    #         if 'web_answer_node' in output:
    #             print("======================= SUCCESS =============")
    #             await final_answer.stream_token(output["web_answer_node"]["final_answer"])
    #
    # await final_answer.send()
