# sdibot
SDI bot manages the slack workspace for members of SDI

# What you need
1. slackclient package.
  install it using `pip install slackclient`
2. The slack api token (will be provided on request or you can generate your own)

# Commands right now

`help`:    prints a list of all commands I take

`get-phone`:    Get the phone number of a member in SDI.
Usage: get-phone <name>

`get-email`:    Get the email address of a member in SDI.
Usage: get-email <name>

`get-github`:    Get the github url of a member in SDI.
Usage: get-github <name>

`list-project-submissions`:    List the details of projects submitted by members

`add-project`:    Add a project that has been completed. Syntax is
add-project <member1, member2>
Project_url: (Please ensure you enter http) <url>
github_link: <url> 
Eg: add-project <Indranil, Sharanya, Saahith, Kartik> http://example.com https://github.com/example

`present-manifest`:    Prints the link to the SDI manifest
