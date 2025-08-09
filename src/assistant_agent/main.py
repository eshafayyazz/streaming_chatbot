import chainlit as cl
import os
from agents import Agent, RunConfig, AsyncOpenAI, Runner, OpenAIChatCompletionsModel
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from openai.types.responses import ResponseTextDeltaEvent
gemini_api_key = "AIzaSyCSdmdMxXLXunUb6dVNV2uZVuRoRduud10"
#step 1: Provider
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)
#step 2: Model
model = OpenAIChatCompletionsModel(
    model="gemini-1.5-flash",
    openai_client=provider,
)
#config: Defined at Run Level
run_config = RunConfig(
    model=model,
    model_provider=provider,
    tracing_disabled=True,
)
#step 3: Agent
agent1 = Agent(
    instructions="You're a helpful assistant that can answer questions and tasks.",
    name="Panaversity Support Agent",
)
@cl.on_chat_start
async def handle_chat_start():
    cl.user_session.set("history", [])
    await cl.Message(content="Hello! I'm the Panaversity support agent! How can I assist you today?").send()
@cl.on_message
async def handle_message(message: cl.Message):
    history = cl.user_session.get("history")

    msg= cl.Message(content="")
    await msg.send()

    #standard interface
    history.append({"role": "user","content": message.content,})
    result= Runner.run_streamed(
        agent1,
        input=history,
        run_config=run_config,
        )
    async for event  in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
              await msg.stream_token(event.data.delta)
            
    history.append({"role": "assistant","content": result.final_output,})
    cl.user_session.set("history", history)
    # await cl.Message(content=result.final_output).send()
