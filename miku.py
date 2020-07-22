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
    await bot.change_presence(activity = discord.Game(name = "Let's Report People!"))


@bot.command()
async def health(ctx, *arg):
    db.__init__()
    await ctx.send("OK")


@bot.command()
async def hello(ctx, *arg):
    if len(arg) == 0:
        await ctx.send("Konnichiwa " + getEventOwnerId(ctx) + "!")


@bot.command()
async def bye(ctx, *arg):
    if len(arg) == 0:
        await ctx.send("kthxbi " + getEventOwnerId(ctx) + "!")


@bot.command()
async def request(ctx, *arg):
    if len(arg) != 1:
        await ctx.send("Invalid Syntax! Baaaka! Usage: " + prefix + "request @user")
        return
    requestor = getEventOwnerId(ctx)
    requestee = fixId(arg[0])
    if isInvalidUserId(requestee):
        await ctx.send("Are wa dare? Usage: " + prefix + "request @user")
        return
    if isMiku(requestee):
        await ctx.send("Miku would luv to, but Miku doesn't report people >_<")
        return
    log("command:request: %s %s" % (requestor, requestee))
    if db.request(requestor, requestee, now()):
        await ctx.send(requestee + ", " + requestor + " is requesting you to unreport :)")
    else:
        await ctx.send(requestee + " currently has no outstanding reports against " + requestor)    


@bot.command()
async def requests(ctx, *arg):
    if len(arg) != 0:
        await ctx.send("Invalid Syntax! Baaaka! Usage: " + prefix + "requests")
        return
    user = getEventOwnerId(ctx)
    requests_from_me = db.get_requests_from(user)
    requests_to_me = db.get_requests_to(user)
    log("command:requests: %s" % (user))
    if len(requests_from_me) and len(requests_to_me):
        await ctx.send(user + " has requested unreports from: " + requests_from_me + "\nAnd the following have requested unreports from " + user + ": " + requests_to_me)
    elif not len(requests_from_me) and len(requests_to_me):
        await ctx.send("The following have requested unreports from " + user + ": " + requests_to_me)
    elif len(requests_from_me) and not len(requests_to_me):
        await ctx.send(user + " has requested unreports from: " + requests_from_me)
    else:
        await ctx.send("No requests for " + user + " :)")


@bot.command()
async def report(ctx, *arg):
    if len(arg) != 1 and (len(arg) < 3 or arg[1] != "for"):
        await ctx.send("Invalid Syntax! Baaaka! Usage: " + prefix + "report @user [ for <reason> ]")
        return
    reporter = getEventOwnerId(ctx)
    reportee = fixId(arg[0])
    if isInvalidUserId(reportee):
        await ctx.send("Are wa dare? Usage: " + prefix + "report @user [ for <reason> ]")
        return
    if isMiku(reportee):
        await ctx.send("Yowai ningen... Watashi wa kamida!!")
        return
    if reporter == reportee:
        await ctx.send("I know you're a fool, but don't prove it by reporting yourself >_<")
        return
    log("command:report: %s %s" % (reporter, reportee))
    db.report(reporter, reportee, now())
    await ctx.send(reporter + " just reported " + reportee + " " + " ".join(arg[1:]))


@bot.command()
async def unreport(ctx, *arg):
    if len(arg) != 1:
        await ctx.send("Invalid Syntax! Baaaka! Usage: " + prefix + "unreport @user")
        return
    reporter = getEventOwnerId(ctx)
    reportee = fixId(arg[0])
    if isInvalidUserId(reportee):
        await ctx.send("Are wa dare? Usage: " + prefix + "unreport @user")
        return
    if isMiku(reportee):
        await ctx.send("Arigato :) but fyi, you can never report me...")
        return
    if reporter == reportee:
        await ctx.send("...? Anta honki ka?")
        return
    log("command:unreport: %s %s" % (reporter, reportee))
    if db.unreport(reporter, reportee):
        db.delete_request(reportee, reporter)
        await ctx.send(reporter + " did a good deed and unreported " + reportee)
    else:
        await ctx.send("Sugoi! " + reporter + " doesn't have any reports for " + reportee)


@bot.command()
async def reported(ctx, *arg):
    if len(arg) != 1 and len(arg) != 2:
        await ctx.send("Anta baka desu ka? Usage: " + prefix + "reported @user_reportee [ @user_reporter=self ]")
        return
    if len(arg) == 2:
        reporter = fixId(arg[1])
    else:
        reporter = getEventOwnerId(ctx)
    reportee = fixId(arg[0])
    if isInvalidUserId(reporter) or isInvalidUserId(reportee):
        await ctx.send("Are wa dare? Usage: " + prefix + "reported @reportee [ @reporter=self ]")
        return
    if isMiku(reportee):
        await ctx.send("Such cute kidz... Kawaiii")
        return
    if reporter == reportee:
        await ctx.send("Try reporting yourself! Nani? Omae wa mou shindeiru!!")
        return
    log("command:reported: %s %s" % (reporter, reportee))
    response = db.get_report(reporter, reportee)
    await ctx.send("%s reported %s %s times... %s" % response)


@bot.command()
async def reporter(ctx, *arg):
    if len(arg) > 1:
        await ctx.send("Anata wa hontoni bakada! Usage: " + prefix + "reporter [ @reporter=self ]")
        return
    if len(arg) == 1:
        user = fixId(arg[0])
        if isInvalidUserId(user):
            await ctx.send("Are wa dare? Usage: " + prefix + "reporter [ @reporter=self ]")
            return
        if isMiku(user):
            await ctx.send("Miku is a good girl nyah! She doesn't report people nyaa..")
            return
    else:
        user = getEventOwnerId(ctx)
    log("command:reporter: " + user)
    response = db.get_report_verbose("reporter", user)
    if response:
        await ctx.send(user + " reported all these bad people: " + response)
    else:
        await ctx.send(user + " hasn't reported anyone recently")


@bot.command()
async def reportee(ctx, *arg):
    if len(arg) > 1:
        await ctx.send("Anata wa hontoni bakada! Usage: " + prefix + "reportee [ @reportee=self ]")
        return
    if len(arg) == 1:
        user = fixId(arg[0])
        if isInvalidUserId(user):
            await ctx.send("Are wa dare? Usage: " + prefix + "reportee [ @reportee=self ]")
            return
        if isMiku(user):
            await ctx.send("Miku is a good girl nyah! Noone wants to report her nyaa..")
            return
    else:
        user = getEventOwnerId(ctx)
    log("command:reportee: " + user)
    response = db.get_report_verbose("reportee", user)
    if response:
        await ctx.send(user + " was reported by all these nice people: " + response)
    else:
        await ctx.send(user + " hasn't been reported by anyone recently")


@bot.command()
async def reports(ctx, *arg):
    if len(arg) > 1:
        await ctx.send("Anata wa hontoni bakada! Usage: " + prefix + "reportee [ @reportee=self ]")
        return
    if len(arg) == 1:
        user = fixId(arg[0])
        if isInvalidUserId(user):
            await ctx.send("Are wa dare? Usage: " + prefix + "reportee [ @reportee=self ]")
            return
        if isMiku(user):
            await ctx.send("Miku is a good girl nyah! Noone wants to report her nyaa..")
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
    await ctx.send(response)


@bot.command()
async def stats(ctx, *arg):
    if len(arg) > 1:
        await ctx.send("Anata wa hontoni bakada! Usage: " + prefix + "stats [ @user=self ]")
        return
    if len(arg) == 1:
        user = fixId(arg[0])
        if isInvalidUserId(user):
            await ctx.send("Are wa dare? Usage: " + prefix + "stats [ @user=self ]")
            return
    else:
        user = getEventOwnerId(ctx)
    log("command:stats: " + user)
    response = db.get_report_aggregated(user)
    await ctx.send("%s got reported %s times and reported others %s times :D" % response)


@bot.command()
async def approve(ctx, *arg):
    if len(arg) != 1:
        await ctx.send("Invalid Syntax! Baaaka! Usage: " + prefix + "approve @requestor")
        return
    requestor = fixId(arg[0])
    requestee = getEventOwnerId(ctx)
    if isInvalidUserId(requestor):
        await ctx.send("Are wa dare? Usage: " + prefix + "approve @requestor")
        return
    if isMiku(requestor):
        await ctx.send("Miku doesn't report people, but Miku might change her mind if you keep this up!!")
        return
    log("command:approve: %s %s" % (requestor, requestee))
    if db.unreport(requestee, requestor):
        await ctx.send(requestor + ", " + requestee + " has approved your unreport request")
    else:
        await ctx.send(requestee + ", " + requestor + " has not requested any unreport")


@bot.command()
async def reject(ctx, *arg):
    if len(arg) != 1:
        await ctx.send("Invalid Syntax! Baaaka! Usage: " + prefix + "reject @requestor")
        return
    requestor = fixId(arg[0])
    requestee = getEventOwnerId(ctx)
    if isInvalidUserId(requestor):
        await ctx.send("Are wa dare? Usage: " + prefix + "approve @requestor")
        return
    if isMiku(requestor):
        await ctx.send("Miku doesn't report people, but Miku might change her mind if you keep this up!!")
        return
    log("command:reject: %s %s" % (requestor, requestee))
    if db.delete_request(requestor, requestee):
        await ctx.send(requestor + ", " + requestee + " has rejected your unreport request")
    else:
        await ctx.send(requestee + ", " + requestor + " has not requested any unreport")



bot.run(environ.get("DISCORD_TOKEN"))
