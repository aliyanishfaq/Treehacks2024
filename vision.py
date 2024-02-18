from IPython.display import display, Image, Audio
import cv2  
import base64
import time
from openai import OpenAI
import os
import requests

client = OpenAI()

def generate_frame_descriptions(video_path): 
    video = cv2.VideoCapture(video_path)

    base64Frames = []
    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

    video.release()

    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                "You are given frames from a video. Your task is to describe the action in each frame, focusing on positioning and movement of individuals. Detail if the individual is standing, sitting, moving, or if there's an absence in a frame where they previously were.",
                *map(lambda x: {"image": x, "resize": 768}, base64Frames[0::50]),
            ],
        },
    ]
    params = {
        "model": "gpt-4-vision-preview",
        "messages": PROMPT_MESSAGES,
        "max_tokens": 200,
    }

    result = client.chat.completions.create(**params)
    output = result.choices[0].message.content
    
    return output

def determine_fall(frame_descriptions): 
    PROMPT = """
    You will be provided with a series of descriptions for consecutive frames from a video. Your task is to analyze these descriptions to determine if they indicate that a fall has occurred. During any of the frame descriptions, if the person seems to begin moving downwards (indicated by change in posture), and then partially or totally disappears from the frame, it is to be considered a very likely indication that the individual has fallen. 
    You must either output yes or no. If you are unsure, output yes. You must not output any reasoning/explaination.
    """ 
    
    output = gpt_4(PROMPT, frame_descriptions)
    
    return output 

def gpt_4(system, user, model="gpt-4-1106-preview"):
    print("Using GPT-4")
    messages = [
        {
            "role": "system", 
            "content": system
        },
        {
            "role": "user", 
            "content": user
        }
    ]
    
    try: 
        response = client.chat.completions.create(
        model=model,
        messages=messages, 
        temperature=0,
        )
        
        gpt_response = response.choices[0].message.content.strip()

        return gpt_response
    except Exception as e: 
        print(f"Error in OpenAI API call: {e}")
        return None


video_path = "sample_test_video.mp4"
frame_descriptions = generate_frame_descriptions(video_path)
fall_or_not = determine_fall(frame_descriptions)
print(fall_or_not)
