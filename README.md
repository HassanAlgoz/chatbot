# Example Chatbot CLI with LangGraph using the MVC Pattern

A demonstration of chatbots that cope with mistakes, deal with naturally random human chat interactions like answering not the direct question and correcting previous inforamtion. All while being long-running reliablly, pausable & resumable as well as being focused on its objective of information gathering.

## Install Dependencies

```sh
uv sync
```

## Usage

Run the CLI:

```sh
uv run python -m mvc.frontends.cli.main
```

Run the Web UI:

```sh
uv run chainlit run src/mvc/frontends/web/app.py -w
```

- `-w` is for hot-reloading (automatic restart when code updates are saved)