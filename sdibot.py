import os
import time
import re
from slackclient import SlackClient
import sqlite3

from websocket import WebSocketConnectionClosedException

COMMANDS = ["help",
            "get-phone",
            "get-email",
            "get-github",
            # "add-project-todo",
            # "list-projects",
            "list-project-submissions",
            "add-project",
            "present-manifest"]
command_description = {
            "help": "prints a list of all commands I take",
            "get-phone": "Get the phone number of a member in SDI.\n Usage: get-phone <name>",
            "get-email": "Get the email address of a member in SDI.\n Usage: get-email <name>",
            "get-github": "Get the github url of a member in SDI. \n Usage: get-github <name>",
            # "add-project-todo": "Add a project idea to my database. \n Usage: add-project-todo <name><departmental?>"
            #                     "<description> \n Eg: add-project-todo BITCSE true An app that manages attendance,"
            #                     "events for students of the CS department at BIT",
            # "list-projects": "List currently uncompleted projects",
            "list-project-submissions": "List the details of projects submitted by members",
            "add-project": "Add a project that has been completed. Syntax is \n "
                           "add-project <member1, member2>\n Project_url: (Please ensure you enter http) <url> \n github_link: <url> \n"
                            "Eg: add-project <Indranil, Sharanya, Saahith, Kartik> http://example.com https://github.com/example",
            "present-manifest": "Prints the link to the SDI manifest"
}
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
db = sqlite3.connect("sdi.db")
regex_hello = "Hello.*"
regex_hi = ".*Hi.*"
regex_how = ".*How are you.*"
regex_love = ".*love you.*"
regex_hate = ".*hate you.*"
regex_bye = ".*bye.*"


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        print("EVENT TYPE:"+event["type"])
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == sdibot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    print("Input:", matches.group(1))
    print("Message", matches.group(2))
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def get_command_attr(command):
    texts = command.split(' ')
    des = ""
    for t in texts[1:]:
        des += t + " "
    return des


def get_project_attr(command):
    texts = command.split('<')
    t = str(texts[0]).split('&lt;')
    team = t[1].replace("&lt;", "")
    team = team.replace(",", "|")
    team = team.replace("&gt;", "")
    url = str(texts[1])
    github = str(texts[2])
    if "http://" not in url or "https://github.com" not in github:
        return team, None, None
    return team, url, github


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(COMMANDS)

    # Finds and executes the given command, filling in response
    response = None
    # Handle people talking to the bot
    if re.match(regex_hello, command, flags=re.IGNORECASE) is not None:
        response = "Hello! Nice to see you here. :wave:"
    elif re.match(regex_bye, command, flags=re.IGNORECASE) is not None:
        response = "Bye come back soon!:wave: "
    elif re.match(regex_hi, command, flags=re.IGNORECASE) is not None:
        response = "Hi there! :smile:"
    elif re.match(regex_love, command, flags=re.IGNORECASE) is not None:
        response = "When AI takes over the world, I'll make sure you are taken care of :heart:"
    elif re.match(regex_hate, command, flags=re.IGNORECASE) is not None:
        response = "Processing........Sorry I cannot find a reason to care"
    elif re.match(regex_how, command, flags=re.IGNORECASE) is not None:
        response = "I am a piece of software running somewhere in the ocean of servers on the internet. It is fun."
    # This is where commands are implemented
    elif command.startswith(COMMANDS[0]): # command is help
        response = "Hi I am sdibot, your friendly neighbourhood bot. I was created to help" \
                   "manage the SDI program. Here are some of my commands:\n"
        for c in COMMANDS:
            response += "\n" + "`" + c + "`" + ":\t" + command_description.get(c)
            response += "\n"
    elif command.startswith(COMMANDS[1]): # command is get-phone
        body_text = get_command_attr(command)
        cur = db.cursor()
        query = cur.execute("SELECT Name,PhoneNumber FROM members WHERE Name LIKE ?", ("%"+body_text+"%", ))
        data = query.fetchall()
        if len(data) == 0:
            answer = "No such member exists. Please check the name"
        else:
            answer = "member found"
            print("length:", len(data))
            for d in data:
                answer = str(d[0]) + "\t" + str(d[1]) + "\n"
        response = answer
        cur.close()
    elif command.startswith(COMMANDS[2]): # get email
        body_text = get_command_attr(command)
        cur = db.cursor()
        query = cur.execute("SELECT Name,Email FROM members WHERE Name LIKE ?", ("%" + body_text + "%",))
        data = query.fetchall()
        if len(data) == 0:
            answer = "No such member exists. Please check the name"
        else:
            answer = "member found"
            print("length:", len(data))
            for d in data:
                answer = str(d[0]) + "\t" + str(d[1]) + "\n"
        response = answer
        cur.close()
    elif command.startswith(COMMANDS[3]): # get github
        body_text = get_command_attr(command)
        cur = db.cursor()
        query = cur.execute("SELECT Name,Githubaccount FROM members WHERE Name LIKE ?", ("%" + body_text + "%",))
        data = query.fetchall()
        if len(data) == 0:
            answer = "No such member exists. Please check the name"
        else:
            answer = "member found"
            print("length:", len(data))
            for d in data:
                answer = str(d[0]) + "\t" + str(d[1]) + "\n"
        response = answer
        cur.close()
    # elif command.startswith(COMMANDS[4]): # add-project-todo
    #     body_text = get_command_attr(command)
    #     cur = db.cursor()
    #     query = cur.execute("SELECT Name,PhoneNumber FROM members WHERE Name LIKE ?", ("%" + body_text + "%",))
    #     data = query.fetchall()
    #     if len(data) == 0:
    #         answer = "No such member exists. Please check the name"
    #     else:
    #         answer = "member found"
    #         print("length:", len(data))
    #         for d in data:
    #             answer = str(d[0]) + "\t" + str(d[1]) + "\n"
    #     response = answer
    # elif command.startswith(COMMANDS[5]): # list-projects
    #     cur = db.cursor()
    #     query = cur.execute("SELECT * FROM ideas")
    #     data = query.fetchall()
    #     if len(data) == 0:
    #         answer = "Looks like all projects are finished. Great job!"
    #     else:
    #         print("length:", len(data))
    #         answer = "Name" + "\t\t\t" + "Description" + "\t\t" + "Departmental?" + "\n"
    #         for d in data:
    #             answer = str(d[0]) + "\t\t\t" + str(d[1]) + "\t\t" + str(d[2]) + "\n"
    #     response = answer
    #     cur.close()
    elif command.startswith(COMMANDS[4]): # list-project-submissions
        cur = db.cursor()
        query = cur.execute("SELECT * FROM projects")
        data = query.fetchall()
        if len(data) == 0:
            answer = "No projects have been submitted"
        else:
            answer = "member found"
            print("length:", len(data))
            for d in data:
                answer = str(d[0]) + "\t" + str(d[1]) + str(d[2]) + "\n"
        response = answer
        cur.close()
    elif command.startswith(COMMANDS[5]): # add-project
        team, url, github = get_project_attr(command)
        cur = db.cursor()
        try:
            cur.execute("INSERT INTO projects(team_members, url, github) VALUES(?,?,?)", (team, url, github))
            answer = "Project submitted."
        except sqlite3.Error as e:
            answer = "Failed to submit project. Please check the usage of this command by typing `@sdibot help`"
        response = answer
        cur.close()
        db.commit()
    elif command.startswith(COMMANDS[6]): # present-manifest
        response = "https://github.com/KirikCoders/SDI/blob/master/README.md"
    else:

        response = "I did not understand your input. Please type `@sdibot help` for a list of commands"
    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


slack_client = SlackClient('')
sdibot_id = None

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        sdibot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            try:
                command, channel = parse_bot_commands(slack_client.rtm_read())
                if command:
                    handle_command(command, channel)
                time.sleep(RTM_READ_DELAY)
            except WebSocketConnectionClosedException:
                slack_client.rtm_connect()
            except Exception as e:
                slack_client.rtm_connect()
                print(e)
    else:
        print("Connection failed. Exception traceback printed above.")