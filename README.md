# AIlen - AI Discord Bot

AIlen is a Discord bot that uses an AI model to generate responses to user messages. It can be mentioned in channels, and it will reply to the message it is mentioned in. It also supports slash commands for clearing the conversation context.

## Features

- **AI-powered responses:** AIlen uses an AI model to generate human-like responses to user messages.
- **Conversation context:** The bot keeps a history of the conversation to provide more relevant responses.
- **Slash commands:** AIlen supports slash commands for managing the conversation context.
- **Reply context:** If you reply to a message and mention the bot, the bot will have the context of the replied-to message.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- A Discord bot token
- An API key for the AI model

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/jakubmrowicki/AIlen.git
    ```
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create a `.env` file in the root of the project and add the following environment variables:
    ```
    DISCORD_BOT_TOKEN=your-discord-bot-token
    API_KEY=your-api-key
    ```

### Running the Bot

To run the bot, use the following command:

```bash
python bot.py
```

## Usage

### Mentioning the Bot

To interact with the bot, you can mention it in a message. For example:

`@AIlen What is the meaning of life?`

If you reply to a message and mention the bot, the bot will have the context of the replied-to message.

### Slash Commands

AIlen supports the following slash commands:

- `/clear_context`: Clears the conversation context.

## Configuration

The bot can be configured using the following environment variables:

- `DISCORD_BOT_TOKEN`: The Discord bot token.
- `API_KEY`: The API key for the AI model.
- `API_URL`: The URL of the AI model API.
- `MODEL`: The name of the AI model to use.
- `MAX_TOKENS`: The maximum number of tokens to generate in a response.
- `MAX_HISTORY_LENGTH`: The maximum number of messages to keep in the conversation history.
