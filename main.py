from model import Workflow
from view import SupportBotApp
from services.llm import new_llm

from config import (
    MODEL_NAME,
    OPENROUTER_API_KEY
)

if __name__ == "__main__":
    llm = new_llm(
        model=MODEL_NAME,
        openrouter_api_key=OPENROUTER_API_KEY,
    )
    workflow = Workflow(llm=llm)
    png_data = workflow.graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(png_data)
    app = SupportBotApp(graph=workflow.graph)
    app.run()
