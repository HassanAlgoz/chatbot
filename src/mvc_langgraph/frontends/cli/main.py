from mvc_langgraph.model import Workflow
from mvc_langgraph.frontends.cli.view import SupportBotApp
from mvc_langgraph.services.llm import new_llm

from mvc_langgraph.config import MODEL_NAME, OPENROUTER_API_KEY

if __name__ == "__main__":
    llm = new_llm(
        model=MODEL_NAME,
        openrouter_api_key=OPENROUTER_API_KEY,
    )
    workflow = Workflow(llm=llm)
    app = SupportBotApp(workflow=workflow)
    app.run()
