import asyncio

from langgraph.graph import StateGraph
from langchain_core.messages import HumanMessage

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Markdown, Static, LoadingIndicator
from textual.containers import VerticalScroll, Horizontal


class SupportBotApp(App):
    def __init__(self, graph: StateGraph):
        self.graph = graph
        super().__init__()

    CSS = """
    Screen { background: #1a1b26; }
    #chat_area { height: 1fr; border: solid #333; padding: 1; margin: 1; }
    Input { dock: bottom; margin: 1; border: double #565f89; }
    .user_msg { color: #7aa2f7; margin-bottom: 1; }
    .bot_msg { color: #9ece6a; margin-bottom: 1; }
    #loading_row { height: auto; align: center middle; margin-top: 1; }
    #loading_row.hidden { display: none; }
    #loading_message { color: #9ece6a; margin-left: 1; }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "clear", "Clear Chat")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="chat_area"):
            lines = [
                "# Customer Support Bot",
                "How can I help you today?",
            ]
            yield Markdown(
                markdown="\n".join(lines),
                id="history"
            )
            with Horizontal(id="loading_row", classes="hidden"):
                yield LoadingIndicator()
                yield Static("Computing answer...", id="loading_message")
        yield Input(placeholder="Type your message here...")
        yield Footer()

    def on_mount(self) -> None:
        self.state = {
            "name": None,
            "category": None,
            "device_serial_number": None,
            "invoice_id": None,
            "messages": [],
            "ai_message": "",
        }

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        user_text = event.value.strip()
        if not user_text:
            return

        # UI Update: Clear input and show user message
        event.input.value = ""
        history = self.query_one("#history", Markdown)
        history.update(history._markdown + f"\n\n**You**: {user_text}")

        # Run LangGraph in a worker on the main loop; block in a thread pool so the UI can repaint.
        self.state["messages"].append(HumanMessage(user_text))
        self.run_worker(self.run_graph())

    async def run_graph(self):
        loading_row = self.query_one("#loading_row", Horizontal)
        loading_row.remove_class("hidden")
        self.query_one("#chat_area").scroll_end(animate=True)
        try:
            # Invoke the graph with current state (blocking LLM calls must not run on the UI thread).
            state = await asyncio.to_thread(self.graph.invoke, self.state)
            self.state = state  # Update internal state
            bot_response = f"\n\n**🤖 Bot**: {state['ai_message']}"

            # UI Update: Bot response
            history = self.query_one("#history", Markdown)
            history.update(history._markdown + bot_response)
        finally:
            loading_row.add_class("hidden")

        # Scroll to bottom
        self.query_one("#chat_area").scroll_end(animate=True)
