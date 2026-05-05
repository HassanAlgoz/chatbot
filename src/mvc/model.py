import io
from uuid import uuid4

from langchain_core.messages import AIMessage, BaseMessage, SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI


system_prompt = """You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions."""

class Workflow:
    def __init__(self, llm: ChatOpenAI):
        self.runnable = llm | StrOutputParser()
        self.messages: list[BaseMessage] = [
            SystemMessage(system_prompt)
        ]

    async def astream(self, message: str):
        self.messages.append(HumanMessage(message))
        chunks = []
        async for chunk in self.runnable.astream(self.messages):
            chunks.append(chunk)
            yield chunk
        self.messages.append(AIMessage("".join(chunks)))


    def messages_to_markdown(self) -> str:
        text = io.StringIO()
        for msg in self.messages:
            # Who is speaking?
            who = f"**{msg.type}**"
            if isinstance(msg, HumanMessage):
                who = f"**👤 User**"
            elif isinstance(msg, AIMessage):
                who = f"**🤖 Bot**"
            elif isinstance(msg, SystemMessage):
                who = f"**💻️ System**"
            # What is the message?
            what = f"{msg.content}"
            text.write(f"{who}: {what}\n\n")
        return text.getvalue()