import re
from datetime import datetime

pattern = re.compile("^<@\d+>$")
logfile = open("main.log", "a")


def isInvalidUserId(string):
    return pattern.match(string) is None


def fixId(string):
    if len(string) > 3 and string[:3] == "<@!":
        string = string[:2] + string[3:]
    return string


def getEventOwnerId(ctx):
    author = ctx.message.author.id
    if len(author) > 1 and author[0] == "!":
        author = author[1:]
    return "<@" + author + ">"


def log(msg):
    logfile.write(now() + ' ' + msg + '\n')
    logfile.flush()


def now():
    return str(datetime.now()).split('.')[0]


def isMiku(user):
    return user == "<@417036625726537758>" # Miku's Id!
