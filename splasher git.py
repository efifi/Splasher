# bot.py
import mysql.connector
import os
import discord

production = False       # test or production database connections and ENV
dropall = False          # drop tables - testing and first time only
createtest = False       # test data

if production:
    mydb = mysql.connector.connect(
      host="efis.com",
      user="i",
      passwd="SP",
      database = "eDB"
    )
    TOKEN = "NzEaVA20"
    GUILD = "Spted"
else:
    mydb = mysql.connector.connect(
      host="localhost",
      user="ce",
      passwd="SU",
      database = "DB"
    )

    from dotenv import load_dotenv
    load_dotenv()
    TOKEN = os.getenv('DISCORD_TOKEN')
    GUILD = os.getenv('DISCORD_GUILD')

try:
    client = discord.Client()
except:
    print("Error connecting to discord")


@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')
    # Connect to database
    try:
        mydb.ping()
    except:
        print("trying to reconnect to SQL server")
        mydb.connect()

    mycursor = mydb.cursor(buffered=True)

# DEBUGGING - delete junk table
#    dropall = False

    if dropall == True:
            sql = "DROP TABLE IF EXISTS users"
            err = mycursor.execute(sql)
            print("error drop users - ", err)
            sql = "DROP TABLE IF EXISTS votes"
            err = mycursor.execute(sql)
            print("error drop votes - ", err)

    # see if our tables are created.... done once only, never again
    try:
      mycursor.execute(
        "CREATE TABLE users (name VARCHAR(20) PRIMARY KEY, longname VARCHAR(20), votesbyme INT, votesforme INT, votetotal INT, myscore FLOAT, mytotvotes INT)")
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        print("Probably expected result - error creating user table - ",e)

    try:
      mycursor.execute(
        "CREATE TABLE votes (name VARCHAR(20), namevotedfor VARCHAR(20), PRIMARY KEY(name, namevotedfor), votevalue INT)")
    except (mysql.connector.Error, mysql.connector.Warning) as e:
        print("Probably expected result - error creating vote table - ",e)

#
#
#  Create test data
#
#
    if createtest == True:
        print("** Creating Test data ")
#
# efifi Data
#
        createck = False
        if createck == True:
            sql = "INSERT INTO users (name, longname, votesbyme, votesforme, votetotal, myscore, mytotvotes) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            val = [
                ('210745782934962176', 'efifi', int(3), int(0), int(0), int(0), int(9)),
                ('327691210632331264', 'little_bro999', int(0), int(1), int(4), int(4), int(0)),
                ('327692134406946817', 'ShootThePoop', int(0), int(1), int(3), int(3), int(0)),
                ('467584475472330762', '~*', int(0), int(1), int(2), int(2), int(0))
            ]
            mycursor.executemany(sql, val)
            mydb.commit()
            sql = "INSERT INTO votes (name, namevotedfor, votevalue) VALUES (%s, %s, %s)"
            val = [
                ('210745782934962176', '327691210632331264', int(4)),
                ('210745782934962176', '327692134406946817', int(3)),
                ('210745782934962176', '467584475472330762', int(2))
            ]
            mycursor.executemany(sql, val)
            mydb.commit()
#
# ~* Data
#
        sql = "INSERT INTO users (name, longname, votesbyme, votesforme, votetotal, myscore, mytotvotes) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = [
            ('210745782934962176', 'efifi', int(0), int(1), int(2), int(2), int(0)),
            ('327691210632331264', 'little_bro999', int(0), int(1), int(4), int(4), int(0)),
            ('327692134406946817', 'ShootThePoop', int(0), int(1), int(3), int(3), int(0)),
            ('467584475472330762', '~*', int(3), int(0), int(0), int(0), int(9))
        ]
        mycursor.executemany(sql, val)
        mydb.commit()
        sql = "INSERT INTO votes (name, namevotedfor, votevalue) VALUES (%s, %s, %s)"
        val = [
            ('467584475472330762', '327691210632331264', int(4)),
            ('467584475472330762', '327692134406946817', int(3)),
            ('467584475472330762', '210745782934962176', int(2))
        ]
        mycursor.executemany(sql, val)
        mydb.commit()

    print("** Splasher Bot is ready for action ** ")
    return

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to my Discord server!'
    )

@client.event
async def on_message(message):
# bot must not respond to itself
    if message.author == client.user:
        return

#    print("Parameters = ",message.content)
    parameters = message.content.split(" ")

# we need to drop excess spaces......
    while "" in parameters: parameters.remove("")
    if len(parameters) == 0:
        usercommand = ""
    else:
        usercommand = parameters[0]

# !r has 2 parameters
    if usercommand == '!r':
        if len(parameters) > 3:
#            print("invalid parameters ....... too many")
            thankuser = "invalid parameters ....... too many "
            await message.channel.send(thankuser)
            return
        if len(parameters) < 3:
#            print("invalid parameters ....... too few")
            thankuser = "invalid parameters ....... too few"
            await message.channel.send(thankuser)
            return
        membername = parameters [1]
        ranking = parameters [2]

# !rt has none or 1 parameter
    if usercommand == '!rt':
        if len(parameters) > 2:
#            print("invalid parameters ....... too many")
            thankuser = "invalid parameters ....... too many "
            await message.channel.send(thankuser)
            return
        if len(parameters) == 2:
            numbertoshow = parameters [1]
        else:
            numbertoshow = str(1)
# Help command

    if usercommand == '!rh':
        print('rh command')

        footer = str(message.guild.member_count) + " users in guild"
        retstr1 = str("""```yaml\nCurrently there are 3 commands you can issue ```""")
        retstr2 = str("""```\n'!r @username #Value' - vote 1-5```""")
        retstr3 = str("""```\n'!rt n' - Show the highest ranking splashers, 10 at a time, n = page number```""")
        retstr4 = str("""```\n'!rh' - this help ```""")

        allstr = retstr1 + retstr2 + retstr3 + retstr4

        embed = discord.Embed(title="Splasher Help", color = 0xE86222)
        embed.add_field(name="How to ***vote*** for your favorite splasher\n", value=allstr, inline=False)
        embed.set_footer(text=footer)
        embed.set_thumbnail(url="https://cdn.dribbble.com/users/429762/screenshots/1804795/potion_dribbble_800_600.png")
        await message.channel.send(embed=embed)
        return

# try a code block - but its not working or its not a code block?
    if usercommand == '!rt':
        print('rt command')

        if not (numbertoshow.isdecimal()):
            #            print("opps invalid ranking value - must be numeric")
            thankuser = "opps invalid number to display - must be numeric"
            await message.channel.send(thankuser)
            return
        try:
            mydb.ping()
        except:
            print("trying to reconnect to SQL server")
            mydb.connect()

        # In case they passed a ZERO always show page 1
        nnumbertoshow = int(numbertoshow)
        if nnumbertoshow == 0:
            nnumbertoshow = 1

        pagesize = int(10)
        nnumbertoshow = (nnumbertoshow - 1) * pagesize
        nnumbertoend = nnumbertoshow + pagesize

        mycursor = mydb.cursor(buffered=True)
        sql = "SELECT * FROM users WHERE myscore > 0 ORDER BY myscore DESC"
        mycursor.execute(sql)
        results = mycursor.fetchall()

        embed = discord.Embed(title="Top Splashers", color = 0xE86222)

        retstr = str("""```yaml\n""")

        foundany = False
        numbershown = int(0)
        for x in results:
# XXXX should be 10 to show at a time....
#            print(numbershown, nnumbertoshow, nnumbertoend)

            if numbershown >= nnumbertoshow and numbershown < nnumbertoend:
                foundany = True
                fresponse = x[1]
                # pad the answer to 20 chars so it formats correctly for the user
                for y in range(len(fresponse),20):
                       fresponse = fresponse + " "

                respfmt = " {:20} - {:>10} "
    #            print(fresponse, str(x[5]))
                retstr = retstr + "\n" + str(numbershown+1) + " " + fresponse[0:15] + " - " + str(x[5])[0:4]
            else:
                if numbershown > nnumbertoend:
                    break
            numbershown = numbershown + 1

        if foundany == False:
            retstr = retstr + "No users found in that range\n"
            retstr = retstr + str(nnumbertoshow) + " - " + str(nnumbertoend) + "\n"

        footer = str(message.guild.member_count) + " users in guild"
        retstr = retstr + str(""" ```""")
        embed.add_field(name="***Splashers*** rule \n", value=retstr, inline=False)
        embed.set_thumbnail(url="https://cdn.dribbble.com/users/429762/screenshots/1804795/potion_dribbble_800_600.png")
        embed.set_footer(text=footer)
        await message.channel.send(embed=embed)
        return

    if usercommand == '!ra':
        print('ra command')
        try:
            mydb.ping()
        except:
            print("trying to reconnect to SQL server")
            mydb.connect()

        mycursor = mydb.cursor(buffered=True)
        sql = "SELECT * FROM users ORDER BY longname"
        mycursor.execute(sql)
        results = mycursor.fetchall()

        embed = discord.Embed(title="User Statistics", color=0xE86222)
        retstr = str("""```yaml\n""")
        retstr = retstr + "\nName               Sc  fm Tot  bm mTot  gen"
        retstr = retstr + "\n-------------------------------------------"

        for x in results:
            fresponse = x[1]
            if x[2] > (0):
                avgscore = x[6] / x[2]
            else:
                avgscore = 0
            # pad the answer to 20 chars so it formats correctly for the user
            for y in range(len(fresponse), 20):
                fresponse = fresponse + " "

            retstr = retstr + "\n" + fresponse[0:15] + " - " + str(x[5])[0:3] + " - " + str(x[3]) + " - " + str(x[4]) + " - " + str(x[2]) + " - " + str(x[6]) + " - " + str(avgscore)[0:4]

        footer = str(message.guild.member_count) + " users in guild"
        retstr = retstr + str(""" ```""")
        embed.add_field(name="***Splashers*** rule \n sc = my score \n fm = votes for me \n Tot = Total of votes for me \n bm = number of people voted for \n mTot = total of my votes \n gen = my generosity ", value=retstr, inline=False)
        embed.set_thumbnail(url="https://cdn.dribbble.com/users/429762/screenshots/1804795/potion_dribbble_800_600.png")
        embed.set_footer(text=footer)
        await message.channel.send(embed=embed)
        return

#    if message.content.startswith('!r '):
    elif usercommand == '!r':
         print('r command')
         try:
            mydb.ping()
         except:
            print("trying to reconnect to SQL server")
            mydb.connect()

         mycursor = mydb.cursor(buffered=True)
    # lets strip the input into pieces
    # lets check for the member
    # do we have an @ at the start? we wont if there was the name becomes
    # <@!327692134406946817>
#         print("membername = ", membername)
         membername = membername.lstrip('@')
#         print("membername striped = ", membername)

    # now strip out the <@! and >
         membername = membername.lstrip('<@!')
         membername = membername.rstrip('>')
#         print("membername cleaned = ", membername)

#         print("ranking = ", ranking)
#         print("rankingdecimal = ", ranking.isdecimal())

    # next we need an integer from 1-5
         if not(ranking.isdecimal()):
#            print("opps invalid ranking value - must be numeric")
            thankuser = "opps invalid ranking value - must be numeric"
            await message.channel.send(thankuser)
            return
         rankval = int(ranking)
#         print("rankval = ", rankval)
         if rankval < 0 or rankval > 5:
#            print("opps invalid ranking value - must be 1-5")
            thankuser = "opps invalid ranking value - must be1-5"
            await message.channel.send(thankuser)
            return

    # do we have a valid member?
         foundguild = False
         for guild in client.guilds:
             if guild.name == GUILD:
                 foundguild = True
                 break
         if foundguild == False:
 #            print("cannot find guild")
             await message.channel.send("invalid guild")
             return

#         for guildroles in guild.roles:
#            print("Guild Roles.......... ", guildroles.id, guildroles.name)

         found = False
         for member in guild.members:
#             print("**** all three ", membername, member.name, member.id)
             if membername == member.name:
#                 print("found member name ", member.id)
                 found = True
    # we use IDs not names, swap name for id.
                 memberid = member.id
                 callmember = member.name
                 break
             elif membername == str(member.id):
#                 print("found member number ", member.name)
                 memberid = member.id
                 callmember = member.name
                 found = True
                 break

         if found == False:
#             print("cannot find member")
             await message.channel.send("invalid member - choose a valid member please")
             return

         areweasplasher = False
         for whatroles in member.roles:
             if whatroles.name == "Splasher":
                 areweasplasher = True
         if areweasplasher == False:
#             print("invalid roles.... ...... ", whatroles.name, whatroles.id)
             await message.channel.send("The person you voted for is not a splasher")
             return

         # whats my Discord member.id?
#         print("author....", message.author.id)
         for member in guild.members:
#             print("**** all three ", membername, callmember, member.id)
             if message.author.id == member.id:
#                 print("found my member name ", member.id, member.name)
                 mymemberid = member.id
                 myname = member.name
                 # are we allowed?
                 break

         if mymemberid == memberid:
            thankuser = "Nice try, voting for yourself?"
            await message.channel.send(thankuser)
            return

# we now have the correct string
    # now we need to start checking the database for this entery.
     # now we need to insert secondary table.... insert - first vote for this person
         sql = "SELECT * FROM votes WHERE name = %s and namevotedfor = %s"
         val = (str(mymemberid), str(memberid))
         mycursor.execute(sql, val)
         results = mycursor.fetchall()
         firstvote = True
         if (mycursor.rowcount == 0):
             oldvotevalue = 0
#             print("my first vote for this person? ", firstvote)
         else:
             firstvote = False
#             print("results ",results[0][1])
             for row in results:
                 oldvotevalue = row[2]
#             print("voting again for this person? ", firstvote)
#
#
#  The person i voted for
#
#
         sql = "SELECT * FROM users WHERE name = " + str(memberid)
         mycursor.execute(sql)
         curvalues = mycursor.fetchall()
#         print("Rows = ", mycursor.rowcount)
         if (mycursor.rowcount == 0):
                 sql = "INSERT INTO users (name, longname, votesbyme, votesforme, votetotal, myscore, mytotvotes) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                 val = (str(memberid), callmember, int(0), int(1), rankval, rankval, int(0))
#                 newtotal = rankval
                 newscore = rankval
                 oldscore = 0
                 mycursor.execute(sql, val)
                 mydb.commit()
 #                print(mycursor.rowcount, "was inserted for first entry for person voted for.")
         else:
                 # update users record not insert!!!!!!
                 sql = "UPDATE users SET votesforme = %s, votetotal = %s, myscore = %s WHERE name = " + str(memberid)
                 # we have voted for them previously
                 if firstvote == True:
                     # firtst vote for them
                     newvotes = curvalues[0][3] + 1
                 else:
                     newvotes = curvalues[0][3]

                 oldscore = curvalues[0][4] / curvalues[0][3]
                 newtotal = curvalues[0][4] - oldvotevalue + rankval
                 newscore = newtotal / newvotes

                 val = (newvotes, newtotal, newscore)
                 mycursor.execute(sql, val)
                 mydb.commit()
 #                print(mycursor.rowcount, "user record was updated...")
#
#
#  ME
#
#
         sql = "SELECT * FROM users WHERE name = " + str(mymemberid)
         mycursor.execute(sql)
         results = mycursor.fetchall()
#         print("My Rows = ", mycursor.rowcount)
         if (mycursor.rowcount == 0):
              sql = "INSERT INTO users (name, longname, votesbyme, votesforme, votetotal, myscore, mytotvotes) VALUES (%s, %s, %s, %s, %s, %s, %s)"
              val = (str(mymemberid), myname, int(1), int(0), int(0), int(0), rankval)
              mycursor.execute(sql, val)
              mydb.commit()
#              print(mycursor.rowcount, "was inserted for my main table.")
         else:
              sql = "UPDATE users SET votesbyme = %s, mytotvotes = %s WHERE name = %s"
              # we have voted for them previously
              # no need to update if we are voting for the same person again....
              if firstvote == True:
                  mynewvotes = results[0][2] + 1
              else:
                  mynewvotes = results[0][2]

              newtotvotes = results[0][6] + rankval - oldvotevalue
              val = (int(mynewvotes), int(newtotvotes), str(mymemberid))
              mycursor.execute(sql, val)
              mydb.commit()
#              print(mycursor.rowcount, "user record was updated... ", mynewvotes)
#
#
#  Update subtable votes
#
#
#
         if (firstvote == True):
             sql = "INSERT INTO votes (name, namevotedfor, votevalue ) VALUES (%s, %s, %s)"
             val = (str(mymemberid), str(memberid), rankval)
             mycursor.execute(sql, val)
             mydb.commit()
#             print(mycursor.rowcount, "was inserted in votes")
         else:
             sql = "UPDATE votes SET votevalue = %s WHERE (name = %s and namevotedfor = %s)"
             val = (rankval, str(mymemberid), str(memberid))
             mycursor.execute(sql, val)
#             print("everything ", sql, val, mycursor)
             mydb.commit()
#             print(mycursor.rowcount, "was updated in votes")

         footer = str(message.guild.member_count) + " users in guild"
         retstr1 = str("""```yaml\nThank you for voting for \n""")
         retstr2 = str(""" ```""")
         retstr3 = str(""" Previous Vote  - """)
         retstr4 = str(""" New Vote       - """)
         retstr5 = str(""" Old Ranking    - """)
         retstr6 = str(""" New Ranking    - """)
         retstrend = str("""\n""")
         allstr = retstr1 + str(callmember) + retstrend + retstrend
         allstr = allstr + retstr3 + str(oldvotevalue) + retstrend
         allstr = allstr + retstr4 + str(rankval) + retstrend
         allstr = allstr + retstr5 + str(oldscore) + retstrend
         allstr = allstr + retstr6 + str(newscore) + retstrend
         allstr = allstr + retstr2
#         print(oldvotevalue, rankval, newscore, oldscore)
         embed = discord.Embed(title="Thanks ", color=0xE86222)
         embed.add_field(name="Thankyou  ", value=allstr, inline=False)
         embed.set_footer(text=footer)
         embed.set_thumbnail(
             url="https://cdn.dribbble.com/users/429762/screenshots/1804795/potion_dribbble_800_600.png")
         await message.channel.send(embed=embed)

# Tell the user we voted for them
         thankuser = myname + " voted for you - " + ranking
         user = client.get_user(memberid)
# Try this as smoe users we cannot send to......
         try:
             await user.send(thankuser)
# thank the voting user
         except:
             print("cannot send to this user")
         return
try:
    client.run(TOKEN)
except:
    print("something up with discord")
