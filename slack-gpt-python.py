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
template = """
Human: 
You are a summarizer for a professional organization! This group has lots of people, so sometimes, important details get lost in all the texts.

###Input String###:
{human_input}


###Task###:
Create a summary of the following text conversations, and be sure to include ALL dates, calls, and events planned. If a decision was reached on a topic, be sure to say what the initial topic was and briefly tell me the decision that has been made.


Assistant:"""

prompt = PromptTemplate(
    input_variables = ["human_input"],
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

def starts_with_U_and_number(s):
    return s.startswith('U') and len(s) > 1 and s[1].isdigit()

def cleanMessage(messages):
    messages = [message for message in messages if not message[0].startswith(' ')]
    m_lists = []
    i = 0
    while i < len(messages)-1:
        str_list = []
        str_list.append(messages[i][:11])
        str_list.append(messages[i][12:])
        i+=1
        while (not starts_with_U_and_number(messages[i])) and i<len(messages)-1:
            str_list.append(messages[i])
            i += 1
        m_lists.append(str_list)
    m_lists = m_lists[::-1]
    cleaned = []
    for i in m_lists:
        cleaned.append([i[0]] + i[:0:-1])

    final = []
    for ls in cleaned:
        print(get_username_from_id(ls[0]))
        ls[0] = get_username_from_id(ls[0])
        temp = ls[0] + ":"
        for words in ls[1:]:
            temp = temp + words + "|"
        final.append(temp)
    return final




def fetch_user_dict(token):
    client = WebClient(token=token)
    user_response = client.users_list()
    return {user['id']: user['real_name'] for user in user_response['members']}





def replace_user_tags(messages, user_dict):
    def repl(match):
        user_id = match.group(1)
        return '@' + user_dict.get(user_id, 'UnknownUser')
    
    pattern = re.compile(r'<@(U[A-Z0-9]+)>')
    
    return [pattern.sub(repl, message) for message in messages]





def fetch_messages_from_last_24_hours(channel_id, token):
    # Calculate the timestamp for 24 hours ago
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    # Convert to Slack's timestamp format
    oldest_timestamp = one_day_ago.timestamp()

    # Initialize a Slack client
    client = WebClient(token=token)

    # Fetch the list of all users
    user_response = client.users_list()
    # Create a dictionary mapping user IDs to user names
    user_dict = {user['id']: user['real_name'] for user in user_response['members']}
    
    # Fetch the channel's history
    response = client.conversations_history(
        channel=channel_id,
        oldest=oldest_timestamp
    )

    named_messages = []
    for message in response['messages']:
        user_id = message.get('user')
        user_name = user_dict.get(user_id, 'Unknown User')
        named_messages.append(f"{user_name}: {message['text']}")

    return named_messages


@app.event("app_mention")
def handle_app_mention_events(body, logger, client):
    logger.info(body)
    # Extract the text and user from the event body
    text = body['event']['text']
    user_id = body['event']['user']
    channel_id = body['event']['channel']

    # Fetch the last 24 hours of messages (if you still need this functionality)
    messages = fetch_messages_from_last_24_hours(channel_id, os.environ.get("SLACK_BOT_TOKEN"))
    user_dict = fetch_user_dict(os.environ["SLACK_BOT_TOKEN"])
    processed_messages = replace_user_tags(messages, user_dict)
    processed_messages = processed_messages[::-1]
    result = "|".join(processed_messages)
    # Respond to the mention (for example, you could use your chat model here)
    output = chatgpt_chain.predict(human_input=result)
    
    # Send an ephemeral message to the user who mentioned the app
    client.chat_postEphemeral(
        channel=channel_id,
        user=user_id,
        text=output
    )
    
    


# Start the app
if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()