# PESU-Auth-Bot

A simple bot to authenticate users in any discord server using their PESU credentials.

## Usage

The users can verify themselves using the `/auth` command anytime once the setup is done.

### Run/Deploy the bot yourself

1. Clone the repository
2. Make sure you have Python 3.10 installed
3. Install the dependencies using `pip install -r requirements.txt`
4. modify the `config.yml` file in the root directory of the project:
    ```yaml
    bot:
        token: ''
        developer_user_ids:
            - <discord_developer_id_1>
            - <discord_developer_id_2>
        developer_guild_ids:
            - <discord_developer_guild_id_1>
            - <discord_developer_guild_id_2>
        developer_channel_ids:
            - <discord_developer_channel_id_1>
            - <discord_developer_channel_id_2>

        prefix: 'bot-prefix'
    db: '' 
    ```
5. Run the bot using the `bot.py` file

6. add bot token and db url in env file

<hr>
