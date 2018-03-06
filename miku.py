import asyncio
import discord
from mikuUtils import *
from mikuDBHelper import dbHelper
from discord.ext import commands
from os import environ

prefix = "?miku "
bot = commands.Bot(command_prefix = prefix)
db = dbHelper()


@bot.event
async def on_ready():
    log("event:on_ready: bot online - " + bot.user.name)
    await bot.change_presence(game = discord.Game(name = "Let's Report People!"))


@bot.command()
async def health(*arg):
    db.__init__()
    await bot.say("OK")


@bot.command(pass_context=True)
async def hello(ctx, *arg):
    if len(arg) == 0:
        await bot.say("Konnichiwa " + getEventOwnerId(ctx) + "!")


@bot.command(pass_context=True)
async def bye(ctx, *arg):
    if len(arg) == 0:
        await bot.say("kthxbi " + getEventOwnerId(ctx) + "!")


@bot.command(pass_context=True)
async def request(ctx, *arg):
    if len(arg) != 1:
        await bot.say("Invalid Syntax! Baaaka! Usage: " + prefix + "request @user")
        return
    requestor = getEventOwnerId(ctx)
    requestee = fixId(arg[0])
    if isInvalidUserId(requestee):
        await bot.say("Are wa dare? Usage: " + prefix + "request @user")
        return
    if isMiku(requestee):
        await bot.say("Miku would luv to, but Miku doesn't report people >_<")
        return
    log("command:request: %s %s" % (requestor, requestee))
    if (db.get_report(requestee, requestor))[2] == "0":
        await bot.say(requestee + " currently has no outstanding reports against " + requestor)
    else:
        db.request(requestor, requestee, now())
        await bot.say(requestee + ", " + requestor + " is requesting you to unreport :)")


@bot.command(pass_context=True)
async def requests(ctx, *arg):
    if len(arg) != 0:
        await bot.say("Invalid Syntax! Baaaka! Usage: " + prefix + "requests")
        return
    user = getEventOwnerId(ctx)
    requests_from_me = db.get_requests_from(user)
    requests_to_me = db.get_requests_to(user)
    log("command:requests: %s" % (user))
    if len(requests_from_me) and len(requests_to_me):
        await bot.say(user + " has requested unreports from: " + requests_from_me + "\nAnd the following have requested unreports from " + user + ": " + requests_to_me)
    elif not len(requests_from_me) and len(requests_to_me):
        await bot.say("The following have requested unreports from " + user + ": " + requests_to_me)
    elif len(requests_from_me) and not len(requests_to_me):
        await bot.say(user + " has requested unreports from: " + requests_from_me)
    else:
        await bot.say("No requests for " + user + " :)")


@bot.command(pass_context=True)
async def report(ctx, *arg):
    if len(arg) != 1 and (len(arg) < 3 or arg[1] != "for"):
        await bot.say("Invalid Syntax! Baaaka! Usage: " + prefix + "report @user [ for <reason> ]")
        return
    reporter = getEventOwnerId(ctx)
    reportee = fixId(arg[0])
    if isInvalidUserId(reportee):
        await bot.say("Are wa dare? Usage: " + prefix + "report @user [ for <reason> ]")
        return
    if isMiku(reportee):
        await bot.say("Yowai ningen... Watashi wa kamida!!")
        return
    if reporter == reportee:
        await bot.say("I know you're a fool, but don't prove it by reporting yourself >_<")
        return
    log("command:report: %s %s" % (reporter, reportee))
    db.report(reporter, reportee, now())
    await bot.say(reporter + " just reported " + reportee + " " + " ".join(arg[1:]))


@bot.command(pass_context=True)
async def unreport(ctx, *arg):
    if len(arg) != 1:
        await bot.say("Invalid Syntax! Baaaka! Usage: " + prefix + "unreport @user")
        return
    reporter = getEventOwnerId(ctx)
    reportee = fixId(arg[0])
    if isInvalidUserId(reportee):
        await bot.say("Are wa dare? Usage: " + prefix + "unreport @user")
        return
    if isMiku(reportee):
        await bot.say("Arigato :) but fyi, you can never report me...")
        return
    if reporter == reportee:
        await bot.say("...? Anta honki ka?")
        return
    log("command:unreport: %s %s" % (reporter, reportee))
    if db.unreport(reporter, reportee):
        db.delete_request(reportee, reporter)
        await bot.say(reporter + " did a good deed and unreported " + reportee)
    else:
        await bot.say("Sugoi! " + reporter + " doesn't have any reports for " + reportee)


@bot.command(pass_context=True)
async def reported(ctx, *arg):
    if len(arg) != 1 and len(arg) != 2:
        await bot.say("Anta baka desu ka? Usage: " + prefix + "reported @user_reportee [ @user_reporter=self ]")
        return
    if len(arg) == 2:
        reporter = fixId(arg[1])
    else:
        reporter = getEventOwnerId(ctx)
    reportee = fixId(arg[0])
    if isInvalidUserId(reporter) or isInvalidUserId(reportee):
        await bot.say("Are wa dare? Usage: " + prefix + "reported @reportee [ @reporter=self ]")
        return
    if isMiku(reportee):
        await bot.say("Such cute kidz... Kawaiii")
        return
    if reporter == reportee:
        await bot.say("Try reporting yourself! Nani? Omae wa mou shindeiru!!")
        return
    log("command:reported: %s %s" % (reporter, reportee))
    response = db.get_report(reporter, reportee)
    await bot.say("%s reported %s %s times... %s" % response)


@bot.command(pass_context=True)
async def reporter(ctx, *arg):
    if len(arg) > 1:
        await bot.say("Anata wa hontoni bakada! Usage: " + prefix + "reporter [ @reporter=self ]")
        return
    if len(arg) == 1:
        user = fixId(arg[0])
        if isInvalidUserId(user):
            await bot.say("Are wa dare? Usage: " + prefix + "reporter [ @reporter=self ]")
            return
        if isMiku(user):
            await bot.say("Miku is a good girl nyah! She doesn't report people nyaa..")
            return
    else:
        user = getEventOwnerId(ctx)
    log("command:reporter: " + user)
    response = db.get_report_verbose("reporter", user)
    if response:
        await bot.say(user + " reported all these bad people: " + response)
    else:
        await bot.say(user + " hasn't reported anyone recently")


@bot.command(pass_context=True)
async def reportee(ctx, *arg):
    if len(arg) > 1:
        await bot.say("Anata wa hontoni bakada! Usage: " + prefix + "reportee [ @reportee=self ]")
        return
    if len(arg) == 1:
        user = fixId(arg[0])
        if isInvalidUserId(user):
            await bot.say("Are wa dare? Usage: " + prefix + "reportee [ @reportee=self ]")
            return
        if isMiku(user):
            await bot.say("Miku is a good girl nyah! Noone wants to report her nyaa..")
            return
    else:
        user = getEventOwnerId(ctx)
    log("command:reportee: " + user)
    response = db.get_report_verbose("reportee", user)
    if response:
        await bot.say(user + " was reported by all these nice people: " + response)
    else:
        await bot.say(user + " hasn't been reported by anyone recently")


@bot.command(pass_context=True)
async def reports(ctx, *arg):
    if len(arg) > 1:
        await bot.say("Anata wa hontoni bakada! Usage: " + prefix + "reportee [ @reportee=self ]")
        return
    if len(arg) == 1:
        user = fixId(arg[0])
        if isInvalidUserId(user):
            await bot.say("Are wa dare? Usage: " + prefix + "reportee [ @reportee=self ]")
            return
        if isMiku(user):
            await bot.say("Miku is a good girl nyah! Noone wants to report her nyaa..")
            return
    else:
        user = getEventOwnerId(ctx)
    log("command:reports: " + user)
    res = db.get_report_verbose("reporter", user)
    if res:
        response = user + " reported all these bad people: " + res + "\n"
    else:
        response = user + " hasn't reported anyone recently\n"
    res = db.get_report_verbose("reportee", user)
    if res:
        response += user + " was reported by all these nice people: " + res
    else:
        response += user + " hasn't been reported by anyone recently"
    await bot.say(response)


@bot.command(pass_context=True)
async def stats(ctx, *arg):
    if len(arg) > 1:
        await bot.say("Anata wa hontoni bakada! Usage: " + prefix + "stats [ @user=self ]")
        return
    if len(arg) == 1:
        user = fixId(arg[0])
        if isInvalidUserId(user):
            await bot.say("Are wa dare? Usage: " + prefix + "stats [ @user=self ]")
            return
    else:
        user = getEventOwnerId(ctx)
    log("command:stats: " + user)
    response = db.get_report_aggregated(user)
    await bot.say("%s got reported %s times and reported others %s times :D" % response)


@bot.command()
async def reset(*arg):
    if len(arg) != 2:
        return
    mode = arg[0]
    user = fixId(arg[1])
    if isInvalidUserId(user):
        return
    if mode != "reportee" and mode != "reporter":
        return
    log("command:reset:%s: %s" % (mode, user))
    rows = db.reset_reports(mode, user)
    await bot.say("Changed rows: " + str(rows))


@bot.command(pass_context=True)
async def approve(ctx, *arg):
    if len(arg) != 1:
        await bot.say("Invalid Syntax! Baaaka! Usage: " + prefix + "approve @requestor")
        return
    requestor = fixId(arg[0])
    requestee = getEventOwnerId(ctx)
    if isInvalidUserId(requestor):
        await bot.say("Are wa dare? Usage: " + prefix + "approve @requestor")
        return
    if isMiku(requestor):
        await bot.say("Miku doesn't report people, but Miku might change her mind if you keep this you!!")
        return
    log("command:approve: %s %s" % (requestor, requestee))
    if db.delete_request(requestor, requestee):
        db.unreport(requestee, requestor)
        await bot.say(requestor + ", " + requestee + " has approved your unreport request")
    else:
        await bot.say(requestor + ", " + requestee + " has not requested any unreport")


@bot.command(pass_context=True)
async def reject(ctx, *arg):
    if len(arg) != 1:
        await bot.say("Invalid Syntax! Baaaka! Usage: " + prefix + "reject @requestor")
        return
    requestor = fixId(arg[0])
    requestee = getEventOwnerId(ctx)
    if isInvalidUserId(requestor):
        await bot.say("Are wa dare? Usage: " + prefix + "approve @requestor")
        return
    if isMiku(requestor):
        await bot.say("Miku doesn't report people, but Miku might change her mind if you keep this you!!")
        return
    log("command:reject: %s %s" % (requestor, requestee))
    if db.delete_request(requestor, requestee):
        await bot.say(requestor + ", " + requestee + " has rejected your unreport request")
    else:
        await bot.say(requestor + ", " + requestee + " has not requested any unreport")



bot.run(environ.get("DISCORD_TOKEN"))



