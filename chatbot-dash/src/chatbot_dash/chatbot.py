"""Chatbot multiple models."""

# pylint: disable=E1129, E1120, C0116, C0103
import solara
import solara.lab
from llama_index.core.llms.llm import LLM
from chatbot_dash.config import FILE_PATH, LLM_DICT, PROMPT
from chatbot_dash.components.chat_options import ChatOptions
from chatbot_dash.components.editable_message import EditableMessage
from chatbot_dash.components.model_info import ModelInfo
from chatbot_dash.config import get_logger
from solara.lab import task


logger = get_logger(__file__)

"""when set, history will be erased on model change."""
reset_on_change: solara.Reactive[bool] = solara.Reactive(False)
"""when set, make all assistant response editable."""
# TODO CHECK rationale. Not sure how useful it is, as the previous conversation may become inconsitent.
edit_mode: solara.Reactive[bool] = solara.Reactive(False)
# we initialize history with the system prompt
messages: solara.Reactive[list[dict]] = solara.reactive(
    ([{"role": "system", "content": PROMPT}])
)
edit_index = solara.reactive(None)
current_edit_value = solara.reactive("")
model_labels: solara.Reactive[dict[int, str]] = solara.reactive({})
is_menu_open = solara.reactive(False)
current_llm_name: solara.Reactive[str] = (
    solara.reactive("llama3.1")
    if "llama3.1" in LLM_DICT
    else solara.reactive(list(LLM_DICT.keys())[0])
)

@solara.component
def Page():
    # hide solara message at the bottom ("This website runs on solara")
    solara.Style(FILE_PATH.joinpath("style.css")) 
    solara.Title("Aithena")

    # could be a useful dependency if we wanted to regenerate when external
    # tools modify the message history. Unused for now.
    user_message_count = len([m for m in messages.value if m["role"] == "user"])

    current_llm: solara.Reactive[LLM] = solara.reactive(  # type: ignore
        LLM_DICT[current_llm_name.value]
    )

    logger.info(f"current model name: {current_llm_name}")
    logger.info(f"current model: {current_llm}")

    def create_user_message(message):
        """"Update the message history with a new user message."""
        messages.value = [
            *messages.value,
            {"role": "user", "content": message},
        ]
        logger.debug(f"create a new user message: {message}")
        call_llm()

    @task
    async def call_llm():
        """Send chat history to the llm and update chat history with the response."""
        logger.debug("calling llm with chat history")
        
        response = current_llm.value.stream_chat(messages=messages.value)

        logger.debug("received a response from the llm, streaming...")
        messages.value = [
            *messages.value,
            {"role": "assistant", "content": ""},
        ]
        for chunk in response:
            if chunk:
                update_response(chunk.delta)
        logger.debug("response completed...")

    def update_response(chunk: str):
        """Add next chunk to current llm response.
        This is needed when we are using LLMs in stream mode.
        """
        messages.value = [
            *messages.value[:-1],
            {
                "role": "assistant",
                "content": messages.value[-1]["content"] + chunk,
            },
        ]

    with solara.Column(
        style={
            "width": "100%",
            "position": "relative",
            "height": "calc(100vh - 50px)",
            "padding-bottom": "15px",
            "overflow-y": "auto",
        },
    ):
        ChatOptions(current_llm_name, messages, edit_mode, reset_on_change)

        solara.ProgressLinear(call_llm.pending)

        with solara.lab.ChatBox():
            """Display message history."""
            for index, item in enumerate(messages.value):
                is_last = index == len(messages.value) - 1
                if item["role"] == "system": # do not display system prompt
                    continue
                if item["content"] == "": # do not display initial empty message content
                    continue
                with solara.Column(gap="0px"):
                    with solara.Div(style={"background-color": "rgba(0,0,0.3, 0.06)"}):
                        """Display a message.
                        NOTE ChatMessage work as a container, and has a children component.
                        For editable message, we pass on our component that will replace the 
                        default Markdown component that displays the message content.
                        """
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
                            if edit_mode.value and item["role"] == "assistant":
                                EditableMessage(messages, item["content"], index, edit_index, current_edit_value)
                            else:
                                solara.Markdown(item["content"])

                    if item["role"] == "assistant":
                        """display the model name under the llm response."""
                        if current_llm.value.class_name == "azure_openai_llm":
                            ModelInfo(
                                model_labels,
                                index,
                                f"azure/{current_llm.value.engine}",
                                call_llm,
                                is_last,
                            )
                        else:
                            ModelInfo(model_labels, index, current_llm.value.model, call_llm, is_last)


        """Anchor the chat input at the bottom of the screen."""
        solara.lab.ChatInput(
            send_callback=create_user_message,
            disabled=call_llm.pending,
            style={
                "position": "fixed",
                "bottom": "0",
                "width": "100%",
                "padding-bottom": "5px",
            },
        )
