from langchain_openai import ChatOpenAI


def new_llm(model: str, openrouter_api_key: str, streaming: bool = False):
    return ChatOpenAI(
        model=model,
        temperature=0,
        base_url="https://openrouter.ai/api/v1",
        api_key=openrouter_api_key,
        streaming=streaming,
    )
