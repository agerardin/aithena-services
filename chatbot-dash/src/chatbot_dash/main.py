"""Chatbot multiple models."""

# pylint: disable=E1129, E1120, C0116, C0103
from chatbot_dash.chatbot import ChatBot
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



# we initialize history with the system prompt
messages: solara.Reactive[list[dict]] = solara.reactive(
    ([{"role": "system", "content": PROMPT}])
)

current_llm_name: solara.Reactive[str] = (
    solara.reactive("llama3.1")
    if "llama3.1" in LLM_DICT
    else solara.reactive(list(LLM_DICT.keys())[0])
)

current_llm: solara.Reactive[LLM] = solara.reactive(  # type: ignore
    LLM_DICT[current_llm_name.value]
)

@solara.component
def Page():
    # hide solara message at the bottom ("This website runs on solara")
    solara.Style(FILE_PATH.joinpath("style.css")) 
    solara.Title("Aithena")

    ChatBot(messages, current_llm_name, current_llm)