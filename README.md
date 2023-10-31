# Slack Summarizer Bot with Langchain

## Overview

This code is an implementation of a Slack bot that summarizes text conversations in a professional organization's channel. The bot extracts messages from the Slack channel, processes them, and uses the Langchain library to generate summaries. Here is a brief overview of the code and how to use it:

## Prerequisites

Before using this code, make sure you have the following prerequisites in place:

- Python installed on your system.
- A Slack workspace with the appropriate permissions to create a bot and access channels.
- API tokens:
    - `SLACK_BOT_TOKEN` for the Slack bot.
    - `SLACK_APP_TOKEN` for the Slack app.

## Installation

1. Clone or download this code repository to your local machine.

2. Install the required Python packages using pip:
    - pip install slack_bolt
    - pip install slack_sdk
    - pip install langchain


## Configuration

Make sure to configure the following environment variables:

- `SLACK_BOT_TOKEN`: The API token for the Slack bot.
- `SLACK_APP_TOKEN`: The API token for the Slack app.

## Usage

1. Initialize the Slack bot and Langchain implementation by running the code: python slack-gpt-python.py

2. Mention the Slack bot in a channel to trigger it. You can mention the bot in any channel where it has been installed.

3. The bot will fetch and process messages in the channel. It will use Langchain to create summaries, including dates, calls, and events, as specified in the `template`.

4. The bot will respond to the mention with the generated summary.

## Code Structure

- The code initializes a Slack bot using the Slack Bolt framework and configures it with the bot token.
- It defines a Langchain prompt template for conversation summarization.
- The code handles message processing, cleaning, and fetching from Slack channels.
- The `handle_app_mention_events` function responds to mentions by extracting and processing messages, using the Langchain model, and sending an ephemeral message with the summary back to the user who mentioned the bot.
- The `SocketModeHandler` is used to start the Slack bot in socket mode.

## Note

- This code assumes that you have set up the Slack app and bot with the appropriate permissions and tokens.
- The Langchain library is used for generating summaries, and you can customize the summarization template as needed.
- Make sure you have the necessary environment variables set as mentioned in the configuration section.

Enjoy using your Slack Summarizer Bot with Langchain!
