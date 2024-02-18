from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from langchain import hub
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, HumanMessage
from tools import agent_tools

app = Flask(__name__)
client = OpenAI()

llm = ChatOpenAI(model="gpt-4")
prompt = hub.pull("hwchase17/openai-tools-agent")
agent = create_openai_tools_agent(llm, agent_tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=agent_tools, verbose=True)
chat_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/handle_question', methods=['POST'])
def handle_question():
    audio = request.files['audio']
    audio_path = "audio.webm"
    audio.save(audio_path)
    audio_file = open("audio.webm", "rb")
    
    question = client.audio.transcriptions.create(
      model="whisper-1", 
      file=audio_file,
      response_format="text"
    )
    
    print(f"The question is: {question}")
    
    chat_history.append(HumanMessage(content=question))
    
    agent_input = {
        "input": question,
        "chat_history": chat_history,
    }
  
    response = agent_executor.invoke(agent_input)
    output = response['output']
    chat_history.append(AIMessage(content=output))
    
    speech_path = "static/speech.mp3"
    speech_response = client.audio.speech.create(
      model="tts-1", 
      voice="nova", 
      input=output
    )
    
    speech_response.stream_to_file(speech_path)
    
    return jsonify({'speech_url': speech_path})

if __name__ == '__main__':
    app.run(debug=True)
