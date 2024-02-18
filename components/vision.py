from IPython.display import display, Image, Audio
import cv2  
import base64
import time
from openai import OpenAI
import os
import requests


client = OpenAI()

video = cv2.VideoCapture("sample_test_video_2.mp4")

base64Frames = []
while video.isOpened():
    success, frame = video.read()
    if not success:
        break
    _, buffer = cv2.imencode(".jpg", frame)
    base64Frames.append(base64.b64encode(buffer).decode("utf-8"))

video.release()
# print(len(base64Frames), "frames read.")

# if base64Frames:
#     display_handle = display(Image(data=base64.b64decode(base64Frames[0].encode("utf-8"))), display_id=True)
#     time.sleep(0.025)

#     # Update the display with the rest of the frames
#     for img in base64Frames[1:]:
#         display_handle.update(Image(data=base64.b64decode(img.encode("utf-8"))))
#         time.sleep(0.025)
# else:
#     print("No frames to display.")

PROMPT_MESSAGES = [
    {
        "role": "user",
        "content": [
            "You are given frames from a video taken at an old age home. There is a high risk of anomolous behavior, such as falling or seizures. For example, a sudden change from standing to being close to the ground could indicate a fall. Similarly, remaining in the same position with limited movement across several images might suggest a seizure. Analyze each frame, and if there's even a small chance of an anomolous behavior, report it.",
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
print(result.choices[0].message.content)


# Someone falling may look for sudden movement/dissaprance from the screen
# Seizure may look like ... 



# TODO: 
# 1. Prompt to find triggers
# 2. Live stream 