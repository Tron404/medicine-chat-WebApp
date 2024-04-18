import requests

headers = {
	"Accept" : "application/json",
	"Content-Type": "application/json",
    }

import numpy as np
import logging
import os

url = os.environ["API_URL"]

logger = logging.getLogger("events")
logging.basicConfig(filename="event_log.log", encoding="utf-8", level=logging.INFO, filemode="w")
def query(payload):
    # {'error': 'Input validation error: `inputs` tokens + `max_new_tokens` must be <= 4096. Given: 191 `inputs` tokens and 4095 `max_new_tokens`', 'error_type': 'validation'}
    response = requests.post(url, headers=headers, json=payload)
    response = response.json()
    print(response)
    if type(response) == dict and "error_type" in response.keys():
        print(f"Error: {response['error_type']}")
        logger.error("Context too big")
        return None
    else:   
        return response[0]["generated_text"]

def mock_query(payload):
        try:
            length = len(payload["inputs"].split(" "))
            print(payload["inputs"])
            if length > payload["parameters"]["max_new_tokens"] - 300:
                raise Exception(f"Output is too long: {length}")
            output = " ".join(np.random.choice(["word", "test", "yes", "nice", "llm"], size = np.random.randint(1000, 1250), replace=True))
            output = [{"generated_text": output}]
            return output
        except Exception as e:
            logger.error("Context too big")
            print(type(e).__name__)

def request(prompt: str) -> str:
    our_system_prompt = "\nYou are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information. Be as concise and direct in your answers, and try to limit the use of filler words.\n" # Please do NOT change this
    prompt = f"<s>[INST] <<SYS>>{our_system_prompt}<</SYS>>\n\n{prompt} [/INST]"
    output = query(
        {
            "inputs": prompt,
            "parameters": {
                "return_full_text": False,
                "max_new_tokens": 2048
            }
        }
    )

    # output = mock_query(
    #      {
    #         "inputs": prompt,
    #         "parameters": {
    #              "max_new_tokens": 2048
    #         }
    #      }
    # )
    
    return output

role_to_input = {
    "assistant": "AI",
    "user": "Human"
}

def send_request(state) -> str:
    answer = ""
    if state.previous_context_limit:
        context_limit = state.previous_context_limit
    else:
        # //2 because each participants' turn is stored separately
        context_limit = len(state.message_history)//2
    while not state.message_fail and context_limit > 0:
        # context = [f"Human: {user_message}\nAI: {model_message}" for user_message, model_message in state.message_history[-context_limit:1]]
        context = [f"{role_to_input[message['role']]}: {message['content']}\n" for message in state.message_history[-(context_limit*2-1):]]
        context = "\n".join(context)
        context += "AI: "
        answer = request(context)
        if answer:
            answer = answer.replace("\n", "")
            state.message_fail = False
            break
        else:
            if context_limit <= 0:
                state.message_fail = True
                return
            logger.info(f"Context size changed: {context_limit} --> {context_limit-1}")
            context_limit -= 1
            state.previous_context_limit = context_limit

    logger.info(f"Answer generated, used previous {context_limit} messages.\n\tNumber of conversation turns {len(state.message_history)//2}.")
    return answer