from dotenv import load_dotenv
from flask import Flask, render_template
from flask_socketio import SocketIO
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from tools import agent_tools

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# llm = ChatOpenAI(model="gpt-4")
# agent = initialize_agent(agent_tools, llm, agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# agent_chain = agent.invoke(
#       {
#         "input": f"What is the temperature in San Francisco right now?"
#       }
#     )
# output = agent_chain['output']
# print(output)

@app.route('/')
def index():
    return render_template('index.html')  

@socketio.on('audio_data')
def handle_audio_stream(audio_chunk):
    # Process the incoming audio chunk
    print(audio_chunk)
  
if __name__ == "__main__": 
  socketio.run(app, debug=True)