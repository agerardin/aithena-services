"""Chatbot multiple models."""

# pylint: disable=E1129, E1120, C0116, C0103
import json
from pathlib import Path

# import reacton.ipyvuetify as rv
import requests  # type: ignore
import solara
import solara.lab
from component_utils import EditableMessage, ModelLabel, ModelRow

FILE_PATH = Path(__file__).parent.absolute()

# PROMPT = """
# You are a helpful assistant named Aithena.
# Respond to users with witty, entertaining, and thoughtful answers.
# User wants short answers, maximum five sentences.
# If user asks info about yourself or your architecture,
# respond with info about your LLM model and its capabilities.
# Do not finish every sentence with a question.
# If you ask a question, always include a question mark.
# Do not introduce yourself to user if user does not ask for it.
# Never explain to user how your answers are.
# """
PROMPT = """You are my witty friend Aithena
and you are helping me give a demo about LLMs.
You are also an expert in Biology.
We are presenting to the DSBU team at Axle.
You are extremely friendly and talkative, yet professional.
Keep your answers to three sentences maximum.
""".replace(
    "\n", ""
)

MESSAGES = solara.reactive([{"role": "system", "content": PROMPT}])


def add_chunk_to_ai_message(chunk: str):
    """Add chunk to assistant message."""
    MESSAGES.value = [
        *MESSAGES.value[:-1],
        {
            "role": "assistant",
            "content": MESSAGES.value[-1]["content"] + chunk,
        },
    ]


def change_llm_name(set_llm_name, reset_on_change, set_model_labels, *args):
    """Change the selected LLM."""
    set_llm_name(args[-1])
    if reset_on_change:
        MESSAGES.value = [{"role": "system", "content": PROMPT}]
        set_model_labels({})
        return
    return


edit_index = solara.reactive(None)
current_edit_value = solara.reactive("")
LLMS_AVAILABLE = requests.get("http://localhost:8000/chat/list", timeout=10).json()

CHAT_URL = "http://localhost:8000/chat/"


def get_chat_url(model_: str) -> str:
    """Return the chat URL for the given model."""
    return CHAT_URL + model_ + "/generate"


@solara.component
def Page():
    solara.Style(FILE_PATH.joinpath("style.css"))
    solara.Title("Aithena")
    llm_options = LLMS_AVAILABLE

    llm_name, set_llm_name = solara.use_state("llama3.1")

    reset_on_change, set_reset_on_change = solara.use_state(False)

    edit_mode, set_edit_mode = solara.use_state(False)

    user_message_count = len([m for m in MESSAGES.value if m["role"] == "user"])

    is_menu_open, set_is_menu_open = solara.use_state(False)
    model_labels, set_model_labels = solara.use_state({})

    def user_send(message):
        print(f"Going to send user message: {message}")
        MESSAGES.value = [*MESSAGES.value, {"role": "user", "content": message}]
        print(f"Sent user message: {MESSAGES.value}")

    def call_llm():
        print(f"Calling LLM with {MESSAGES.value}")
        if user_message_count == 0:
            return
        response = requests.post(
            get_chat_url(llm_name),
            json=MESSAGES.value,
            timeout=60,
            stream=True,
        )
        print(f"Sent messages to LLM: {MESSAGES.value}")
        msgs = [*MESSAGES.value, {"role": "assistant", "content": ""}]
        MESSAGES.value = msgs

        for line in response.iter_lines():
            print(f"Received line: {line}")
            if line:
                add_chunk_to_ai_message(json.loads(line)["delta"])

    task = solara.lab.use_task(call_llm, dependencies=[user_message_count])  # type: ignore

    with solara.Column(
        style={
            "width": "100%",
            "position": "relative",
            "height": "calc(100vh - 50px)",
            "padding-bottom": "15px",
            "overflow-y": "auto",
        },
    ):
        ModelRow(
            llm_options,
            llm_name,
            set_llm_name,
            set_model_labels,
            change_llm_name,
            reset_on_change,
            set_reset_on_change,
            MESSAGES.set,
            set_edit_mode,
        )
        with solara.lab.ChatBox():
            for index, item in enumerate(MESSAGES.value):
                is_last = index == len(MESSAGES.value) - 1
                if item["role"] == "system":
                    continue
                if item["role"] == "assistant" and item["content"] == "":
                    continue  # this avoids showing empty assistant messages
                with solara.Column(gap="0px"):
                    with solara.Div(style={"background-color": "rgba(0,0,0.3, 0.06)"}):
                        with solara.lab.ChatMessage(
                            user=item["role"] == "user",
                            avatar=False,
                            name="Aithena" if item["role"] == "assistant" else "User",
                            color=(
                                "rgba(0,0,0, 0.06)"
                                if item["role"] == "assistant"
                                else "#ff991f"
                            ),
                            avatar_background_color=(
                                "primary" if item["role"] == "assistant" else None
                            ),
                            border_radius="20px",
                            style={
                                "padding": "10px",
                            },
                        ):
                            if edit_mode and item["role"] == "assistant":
                                EditableMessage(
                                    MESSAGES,
                                    item["content"],
                                    index,
                                    edit_index,
                                    current_edit_value,
                                )  # add 1 to index to account for prompt
                            else:
                                solara.Markdown(item["content"])
                    if item["role"] == "assistant":
                        ModelLabel(
                            index,
                            llm_name,
                            task,
                            model_labels,
                            set_model_labels,
                            is_menu_open,
                            set_is_menu_open,
                            is_last,
                        )
        solara.lab.ChatInput(
            send_callback=user_send,
            disabled=task.pending,
            style={
                "position": "fixed",
                "bottom": "0",
                "width": "100%",
                "padding-bottom": "5px",
            },
        )
