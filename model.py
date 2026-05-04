from textwrap import dedent
from typing import Optional, Literal

from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI


class SupportState(BaseModel):
    name: str = Field(default="", description="The user's name.")
    category: Optional[Literal["technical", "billing"]] = Field(
        default=None,
        description="The type of issue the user is experiencing. 'technical' or 'billing'.",
    )
    device_serial_number: Optional[str] = Field(
        default=None,
        description="The serial number of the device the user is experiencing an issue with.",
    )
    invoice_id: Optional[str] = Field(
        default=None, description="The invoice ID of the user's account."
    )


class Workflow:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.messages: list[BaseMessage] = []
        self.state = SupportState()

    def run(self, user_text: str):
        self.messages.append(HumanMessage(user_text))
        x = self.interpreter()
        for k, v in x.items():
            setattr(self.state, k, v)
        return self.flow()

    def interpreter(self):
        """Uses LLM to extract info from the last message."""
        last_msg = self.messages[-1].content
        hmsg = dedent(f"""
            Extract information from the user's message.
            Current state: name={self.state.name}, category={self.state.category}.

            User says: "{last_msg}"

            Set each field only when clearly stated or implied; leave unknown fields unset (null).
            device_serial_number: only when the issue is technical.
            invoice_id: only when the issue is billing.
        """)
        model = self.llm.with_structured_output(SupportState)
        data = model.invoke(
            [
                SystemMessage(content="You are a data extractor."),
                HumanMessage(content=hmsg),
            ]
        )
        # Preserve prior state when the model returns null for a field (partial updates).
        return {
            "name": data.name or self.state.name,
            "category": data.category or self.state.category,
            "device_serial_number": data.device_serial_number
            or self.state.device_serial_number,
            "invoice_id": data.invoice_id or self.state.invoice_id,
        }

    def flow(self):
        """Determines what information is missing and generates the prompt."""

        # Step 1 ask for name
        if not self.state.name:
            text = "What is your name?"
            return {"ai_message": text}
        
        # Step 2 ask for category
        if not self.state.category:
            text = "Is this a 'technical' or 'billing' issue?"
            return {"ai_message": text}
        # Step 2.a: if "technical", ask for device serial number
        if self.state.category == "technical" and not self.state.device_serial_number:
            text = f"Thanks {self.state.name}. Since it's technical, what is your **Device Serial Number**?"
            return {"ai_message": text}
        # Step 2.b: if "billing", ask for invoice id
        elif self.state.category == "billing" and not self.state.invoice_id:
            text = (
                f"Thanks {self.state.name}. For billing, I'll need your **Invoice ID**."
            )
            return {"ai_message": text}

        # END route
        text = dedent(f"""I have all the info!
            Name: {self.state.name}
            Category: {self.state.category}
            {f"Device Serial Number: {self.state.device_serial_number}" if self.state.category == "technical" else ""}
            {f"Invoice ID: {self.state.invoice_id}" if self.state.category == "billing" else ""}
            Processing your request...""")
        return {"ai_message": text}
