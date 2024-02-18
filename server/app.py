from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
from langchain import hub
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.messages import AIMessage, HumanMessage
#from tools import agent_tools
from dotenv import load_dotenv
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from twilio.rest import Client
import googlemaps
import os
import requests

app = Flask(__name__)
client = OpenAI()

load_dotenv()

account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
from_number = os.getenv('TWILIO_PHONE_NUMBER')
gmaps_key = os.getenv('GOOGLE_MAPS_KEY')
gmaps = googlemaps.Client(key=gmaps_key)

@tool
def get_location_of_individual_in_emergency(): 
  """
  Returns the address of an individual in an emergency.  

  Returns:
  str: A human-readable address representing the individual's location. If the location cannot be determined
       or converted into an address, a default message indicating that no address was found is returned.
    
  """
  url = "https://www.googleapis.com/geolocation/v1/geolocate"
  params = {'key': gmaps_key}
  headers = {'Content-Type': 'application/json'}
  data = {
        "homeMobileCountryCode": 310,
        "homeMobileNetworkCode": 410,
        "radioType": "gsm",
        "carrier": "Vodafone",
        "considerIp": "true"
    }

  response = requests.post(url, params=params, headers=headers, json=data)
  
  if response.status_code == 200:
    data = response.json()
  else:
    raise Exception(f"Error in geolocation request: {response.text}")
    
  latitude = float(data['location']['lat'])
  longitude = float(data['location']['lng'])
  
  result = gmaps.reverse_geocode((latitude, longitude))
  if result:
    location = result[0].get('formatted_address', 'No address found')
  else:
    location = 'No address found'
    
  return location

@tool
def send_emergency_call(message):
    """
    Sends an emergency call to with a specified message using Twilio. You must explicitly state the location as context in the call. The phone number will always be the same, so don't worry about it.
    
    Parameters:
    message (str): The message to be read during the call.
    
    Returns: 
    bool: True if the call was successfully initiated, False otherwise.

    """
    try: 
      # Twilio credentials - ideally, fetch from environment variables or a secure config
      # Fetch Twilio credentials from environment variables
      account_sid = os.getenv('TWILIO_ACCOUNT_SID')
      auth_token = os.getenv('TWILIO_AUTH_TOKEN')
      from_number = os.getenv('TWILIO_PHONE_NUMBER')

      # Initialize the Twilio client
      client = Client(account_sid, auth_token)

      # Create the call with TwiML to say the emergency message
      call = client.calls.create(
          twiml=f'<Response><Say>{message}</Say></Response>',
          to="+14156361256",
          from_='+18667643449'  # Your Twilio number
      )
      return True  
    
    except Exception as e: 
      return False 


agent_tools = []
agent_tools.append(get_location_of_individual_in_emergency)
agent_tools.append(send_emergency_call)

# https://python.langchain.com/docs/modules/agents/tools/custom_tools

llm = ChatOpenAI(model="gpt-4")
prompt = hub.pull("hwchase17/openai-tools-agent")
agent = create_openai_tools_agent(llm, agent_tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=agent_tools, verbose=True)
chat_history = []

@app.route('/')
def index():
    print('Audio Input')
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
    app.run(host='0.0.0.0', debug=True)
