import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from langchain.llms import OpenAI
from langchain.chains import ConversationChain, LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
import datetime
from slack_sdk import WebClient
import re

# Initialize app with bot token and socket mode handler
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Langchain implimentation
template = """Assistant is a large language model trained by OpenAI.

Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

{history}
Human: {human_input}
Assistant:"""

prompt = PromptTemplate(
    input_variables = ["history", "human_input"],
    template = template
)

chatgpt_chain = LLMChain(
    llm=OpenAI(temperature=0),
    prompt=prompt,
    verbose=True,
    memory=ConversationBufferWindowMemory(k=2),
)

client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

def get_username_from_id(user_id):
    response = client.users_info(user=user_id)
    return response['user']['name']

def replace_tags(messages):
    # Define the regex pattern to match patterns like <@U063XFA8JAC>
    pattern = re.compile(r'<@([^>]+)>')
    
    # Use a list comprehension to replace each occurrence in every message
    messages = [pattern.sub(r'\1', message) for message in messages]
    return messages

def cleanMessage(messages):
    return [message for message in messages if not message[0].startswith(' ')]


def fetch_messages_from_last_24_hours(channel_id, token):
    # Calculate the timestamp for 24 hours ago
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    # Convert to Slack's timestamp format
    oldest_timestamp = one_day_ago.timestamp()

    # Initialize a Slack client
    client = WebClient(token=token)

    # Fetch the channel's history
    response = client.conversations_history(
        channel=channel_id,
        oldest=oldest_timestamp
    )
    messages = [message['text'] for message in response['messages']]
    named_messages = replace_tags(messages)
    # Return the messages
    return named_messages

@app.event("app_mention")
def handle_app_mention_events(body, logger, client):
    logger.info(body)
    # Extract the text and user from the event body
    text = body['event']['text']
    user_id = body['event']['user']
    channel_id = body['event']['channel']
    
    # Respond to the mention (for example, you could use your chat model here)
    output = chatgpt_chain.predict(human_input=text)
    
    # Send an ephemeral message to the user who mentioned the app
    client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        text=output
    )
    
    # Fetch the last 24 hours of messages (if you still need this functionality)
    messages = cleanMessage(fetch_messages_from_last_24_hours(channel_id, os.environ.get("SLACK_BOT_TOKEN")))
    print(messages)



# Start the app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()