import chainlit as cl
from langchain_core.runnables import Runnable, RunnableConfig
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

from mvc.config import OPENROUTER_API_KEY, MODEL_NAME
from mvc.services.llm import new_llm


@cl.on_chat_start
async def on_chat_start():
    # OpenRouter integration using standard ChatOpenAI
    llm = new_llm(
        model=MODEL_NAME,
        openrouter_api_key=OPENROUTER_API_KEY,
        streaming=True,
    )

    # Modern LCEL
    runnable = llm | StrOutputParser()
    cl.user_session.set("runnable", runnable)

    # Initialize state with 1 positional argument for SystemMessage
    cl.user_session.set(
        "history",
        [
            SystemMessage(
                "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions."
            )
        ],
    )


@cl.on_message
async def on_message(message: cl.Message):
    runnable: Runnable = cl.user_session.get("runnable")
    history: list[BaseMessage] = cl.user_session.get("history")

    # 1 positional argument for HumanMessage
    history.append(HumanMessage(message.content))

    msg = cl.Message(content="")

    # Thread tracking config
    config: RunnableConfig = {"configurable": {"thread_id": cl.context.session.id}}

    async for chunk in runnable.astream(history, config=config):
        await msg.stream_token(chunk)

    # 1 positional argument for AIMessage
    history.append(AIMessage(msg.content))
    await msg.send()
