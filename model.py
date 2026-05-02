from textwrap import dedent
from typing import TypedDict, Optional, Literal

from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

class FlowState(TypedDict):
    messages: list
    ai_message: str

class SupportState(FlowState, total=False):
    name: Optional[str]
    category: Optional[Literal["technical", "billing"]]
    device_serial_number: Optional[str]
    invoice_id: Optional[str]


class ExtractedSupportInfo(BaseModel):
    """Structured fields extracted from the user's last message."""

    name: Optional[str] = None
    category: Optional[Literal["technical", "billing"]] = None
    device_serial_number: Optional[str] = None
    invoice_id: Optional[str] = None


class Workflow:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.extraction_llm = llm.with_structured_output(ExtractedSupportInfo)
        self.graph = self.build_graph()

    def build_graph(self):
        # Build the Graph
        workflow = StateGraph(SupportState)
        workflow.add_node("interpreter", self.interpreter_node)
        workflow.add_node("router", self.router_node)

        workflow.add_edge(START, "interpreter")
        workflow.add_edge("interpreter", "router")
        workflow.add_edge("router", END)

        return workflow.compile()

    def interpreter_node(self, state: SupportState):
        """Uses LLM to extract info from the last message."""
        last_msg = state["messages"][-1].content

        prompt = dedent(f"""
            Extract information from the user's message.
            Current state: name={state.get("name")}, category={state.get("category")}.

            User says: "{last_msg}"

            Set each field only when clearly stated or implied; leave unknown fields unset (null).
            device_serial_number: only when the issue is technical.
            invoice_id: only when the issue is billing.
        """)

        data: ExtractedSupportInfo = self.extraction_llm.invoke(
            [
                SystemMessage(content="You are a data extractor."),
                HumanMessage(content=prompt),
            ]
        )
        # Preserve prior state when the model returns null for a field (partial updates).
        return {
            "name": data.name or state.get("name"),
            "category": data.category or state.get("category"),
            "device_serial_number": data.device_serial_number or state.get("device_serial_number"),
            "invoice_id": data.invoice_id or state.get("invoice_id"),
        }

    def stage_1_required(self, state: SupportState):
        missing = []
        if not state.get("name"):
            missing.append("your name")
        if not state.get("category"):
            missing.append("if this is a 'technical' or 'billing' issue")
        return {"ai_message": f"I still need: {' and '.join(missing)}."}

    def router_node(self, state: SupportState):
        """Determines what information is missing and generates the prompt."""
        # Stage 1 route
        required_1 = {"name", "category"}
        if not all(state.get(key) for key in required_1):
            return self.stage_1_required(state)

        # Stage 2 route
        if state["category"] == "technical" and not state["device_serial_number"]:
            return {
                "ai_message": f"Thanks {state['name']}. Since it's technical, what is your **Device Serial Number**?"
            }
        elif state["category"] == "billing" and not state["invoice_id"]:
            return {
                "ai_message": f"Thanks {state['name']}. For billing, I'll need your **Invoice ID**."
            }
        
        # END route
        ai_message = dedent(f"""I have all the info!
        Name: {state['name']}
        Category: {state['category']}
        {f"Device Serial Number: {state['device_serial_number']}" if state['category'] == "technical" else ""}
        {f"Invoice ID: {state['invoice_id']}" if state['category'] == "billing" else ""}

        Processing your request...
        """)
        return {"ai_message": ai_message}
