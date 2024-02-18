from dotenv import load_dotenv
from flask import Flask, render_template
from flask_socketio import SocketIO
from langchain import hub
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, HumanMessage
from tools import agent_tools

load_dotenv()

# app = Flask(__name__)
# socketio = SocketIO(app, cors_allowed_origins="*")

# @app.route('/')
# def index():
#     return render_template('index.html')  

# @socketio.on('audio_data')
# def handle_audio_stream(audio_chunk):
#     # Process the incoming audio chunk
#     print(audio_chunk)a
  
# if __name__ == "__main__": 
#   socketio.run(app, debug=True)

llm = ChatOpenAI(model="gpt-4")
# agent = initialize_agent(agent_tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)
prompt = hub.pull("hwchase17/openai-tools-agent")
agent = create_openai_tools_agent(llm, agent_tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=agent_tools, verbose=True)

chat_history = []

def process_input(user_input): 
  chat_history.append(HumanMessage(content=user_input))

  agent_input = {
        "input": user_input,
        "chat_history": chat_history,
    }
  
  response = agent_executor.invoke(agent_input)
  output = response['output']
  chat_history.append(AIMessage(content=output))
  
  return output
  
while True:
    user_input = input("You: ")
    if user_input.lower() == "quit":
        break
    response = process_input(user_input)
    print("Agent:", response)


# agent_chain = agent.invoke(
#       {
#         "input": f"I think I'm having a heart attack. Help!"
#       }
#     )
# output = agent_chain['output']
# print(output)
