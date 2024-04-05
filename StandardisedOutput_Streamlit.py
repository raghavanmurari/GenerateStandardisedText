from dotenv import load_dotenv
load_dotenv('.env')
import base64
import requests
import streamlit as st
from PIL import Image
import openai
import time
import os

uploaded_file = st.file_uploader("Please choose a file")
api_key = os.environ.get('OPENAI_API_KEY')
assistant_id = "asst_le9kuuk9Z7qBt03kEISYHGBB"

# Below is a function to encode the image. To encode, first the image must be converted to a binary file.
# This conversion is done using the command "rb". It means READ BINARY.
# The binary file is then encoded using "base64.b64encode()". The input must always be binary

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

#create a thread
def create_thread(ass_id,prompt):
    thread = openai.beta.threads.create()
    my_thread_id = thread.id

    #create a message
    message = openai.beta.threads.messages.create(
        thread_id=my_thread_id,
        role="user",
        content=prompt
    )

    #run
    run = openai.beta.threads.runs.create(
        thread_id=my_thread_id,
        assistant_id=ass_id,
    )

    return run.id, thread.id

def check_status(run_id, thread_id):
    run = openai.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id,
    )
    return run.status

if uploaded_file is not None:
    prompt2 = st.text_input("Transcribed Text")
    image = Image.open(uploaded_file)
    # below code removes the display of file name
    st.markdown('''
            <style>
                .uploadedFile {display: none}
            <style>''',
                unsafe_allow_html=True)
    st.image(image, width= 200)

    # Path to your image. The uploaded file's name is stored in image_path.
    image_path = uploaded_file.name
    # OpenAI API Key. This is generated taken the OpenAI website
    # api_key = os.getenv('API_KEY')

    # Getting the base64 string. The image file must be encoded
    base64_image = encode_image(image_path)

    # HEADER is a dictionary with a key:value pair. The purpose of this is to carry the API Key to GPT4.
    # Also, the Content-Type tells the GPT4 to give the data in JSON format only

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "List out the important object in this image. Omit the objects in background"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }
    # Below REQUESTS.POST() sends JSON request with Bearer Token authentication to the URL mentioned
    if prompt2 != '':
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        prompt1 = response.json()['choices'][0]["message"]["content"]
        st.write("GPT Text:\n", prompt1)


        if prompt1 and prompt2:
            prompt = prompt2 + prompt1
            my_run_id, my_thread_id = create_thread(assistant_id, prompt)
            status = check_status(my_run_id, my_thread_id)
            while (status != "completed"):
                status = check_status(my_run_id, my_thread_id)
                time.sleep(1)

            response = openai.beta.threads.messages.list(thread_id=my_thread_id)

            if response.data:
                st.write("Standardised text is:\n", response.data[0].content[0].text.value)
