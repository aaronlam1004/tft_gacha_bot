import discord
import sys
from os import path
from TFTGacha import TFTGacha
from TFTDatabase import TFTDatabase

if __name__ == '__main__':

	client = discord.Client()
	tft = TFTGacha()
	database = TFTDatabase()

	tier_colors = {
		1: 0x172433,
		2: 0x40bf77,
		3: 0x4175be,
		4: 0xc426c5,
		5: 0xf49a2d
	}

	@client.event
	async def on_ready():
		print("We have logged in as {0.user}".format(client))
		for emoji in client.emojis:
			await emoji.delete()

	@client.event
	async def on_message(message):
		client_mention = str(client.user.mention)[0:2] + "!" + str(client.user.mention)[2:]

		if message.author == client.user:
			return

		elif message.content.startswith(client_mention + " roll") or message.content.startswith(client_mention + " r"):
			if not database.userExists(message.author):
				database.addUser(message.author)
			tft_user = database.getUser(message.author)

			for _ in range(3):
				imgs = []
				item = tft.summonItem(tft_user.level)
				item_img = discord.File("./set3/items/" + str(tft.getItemId(item)).zfill(2) + ".png", filename = "item.png")
				imgs.append(item_img)

				champ = tft.summonChampion(tft_user.level)
				champ_img = discord.File(("./set3/champions/" + str(champ).lower() ).replace(" ", "").replace("-", "").replace("'", "") + ".png", filename = "champ.png")
				imgs.append(champ_img)
				champ_descrip = ""

				'''emojis = []'''
				champ_descrip += "Cost: **" + str(tft.getChampionTier(champ)) + "**\n"
				for trait in tft.getChampionTraits(champ):
					'''
					trait_name = trait.lower().replace(" ", "").replace("-", "").replace("'", "")
					trait_img = None
					with open("./set3/traits/" + trait_name + ".png", "rb") as image:
						trait_img = image.read() 
					trait_emoji = await message.guild.create_custom_emoji(name = trait_name, image = trait_img)
					champ_descrip = trait + " " +  str(trait_emoji) + "\n"
					emojis.append(trait_emoji)
					'''
					champ_descrip += trait + "\n"

				embedded = discord.Embed(
					title = champ,
					description = champ_descrip,
					colour = discord.Colour(tier_colors[tft.getChampionTier(champ)])
				)
				embedded.set_thumbnail(url = "attachment://champ.png")
				embedded.set_footer(text  = item, icon_url = "attachment://item.png")

				reply = await message.channel.send(files = imgs, embed = embedded)
				await reply.add_reaction("👾")
				'''
				for emoji in emojis:
					await emoji.delete()
				'''
		elif message.content.startswith(client_mention + " profile") or message.content.startswith(client_mention + " p") :
			if not database.userExists(message.author):
				database.addUser(message.author)
			tft_user = database.getUser(message.author)

			thumb = discord.File(tft_user.thumbnail, filename = "thumbnail.png")
			embedded = discord.Embed(
				title = tft_user.title
			)
			embedded.set_thumbnail(url = "attachment://thumbnail.png")

			owned_champions = ""
			if len(tft_user.champions) == 0:
				owned_champions = "None"
			else:
				for champion in tft_user.champions:
					owned_champions += champion + "\n"

			embedded.add_field(name = "Champions", value = owned_champions, inline = False)

			owned_items = ""
			if len(tft_user.items) == 0:
				owned_items = "None"
			else:
				for item in tft_user.items:
					owned_items += item + "\n"

			embedded.add_field(name = "Items", value = owned_items, inline = False)

			embedded.add_field(name = "Level", value = str(tft_user.level))
			embedded.add_field(name = "XP", value = str(tft_user.xp))
			embedded.add_field(name = "Gold", value = str(tft_user.gold))
			
			await message.channel.send(file = thumb, embed = embedded)

		elif message.content.startswith(client_mention + " icon") or message.content.startswith(client_mention + " i"):
			sent = message.content.split(" ")
			if len(sent) == 2:
				await message.channel.send(message.author.mention + " **No champion specified.**")
			else:
				if not database.userExists(message.author):
					database.addUser(message.author)
				tft_user = database.getUser(message.author)

				champ = ""
				for i in range(2, len(sent)):
					champ += sent[i] 
					if i != len(sent)	- 1:
						champ += " "

				thumbnail = "./set3/champions/" + champ.lower().replace(" ", "").replace("-", "").replace("'", "") + ".png"
				if not tft_user.setThumbnail(champ, thumbnail):
					await message.channel.send(message.author.mention + " Could not set profile icon to **" + champ + "** because it has not been claimed.")
				else:
					thumb = discord.File(thumbnail, filename = "thumbnail.png")
					embedded = discord.Embed(
						title = champ 
					)
					embedded.set_image(url = "attachment://thumbnail.png")
					await message.channel.send(message.author.mention + " Profile icon set to **" + champ + "**.", embed = embedded, file = thumb)

		elif message.content.startswith(client_mention + " sell"):
			sent = message.content.split(" ")
			if len(sent) == 2:
				await message.channel.send(message.author.mention + " **No champion specified.**")
			else:
				if not database.userExists(message.author):
					database.addUser(message.author)
				tft_user = database.getUser(message.author)

		elif message.content.startswith(client_mention + " get xp") or message.content.startswith(client_mention + " xp"):
			if not database.userExists(message.author):
				database.addUser(message.author)
			tft_user = database.getUser(message.author)
			if tft_user.level == 1:
				tft_user.gainXP(0)
			elif tft_user.goldChange(-4):
				tft_user.gainXP(4)
			else:
				await message.channel.send(message.author.mention + " **You do not have enough gold to gain XP.**")
				
	
	@client.event
	async def on_reaction_add(reaction, user):
		claimed = True 
		if user != client.user:
			for react in reaction.message.reactions:
				if react.me is True:
					if react.emoji == "👾":
						claimed = False 
					else:
						claimed = True
			
			if not claimed and str(reaction)== "👾":
				try:
					await reaction.message.add_reaction("👍")
					champ = str(reaction.message.embeds[0].title)
					item = str(reaction.message.embeds[0].footer.text)
					reply = str(user.mention) + " has claimed **" + champ  + "**" + " and " + "**" + item + "**"
					
					if not database.userExists(user):
						database.addUser(user)
					tft_user = database.getUser(user)
					tft_user.addChampion(champ)

					if tft_user.thumbnail == "./sadporo.png":
						thumbnail = "./set3/champions/" + champ.lower().replace(" ", "").replace("-", "").replace("'", "") + ".png"
						tft_user.setThumbnail(champ, thumbnail)

					tft_user.addItem(item)

					await reaction.message.channel.send(reply)
				except:
					pass
			else:
				await reaction.message.channel.send("**Could not claim. Please try again or claim another.**")

	if path.isfile("./token.txt"):
		with open("token.txt", "r") as key:
			client.run(key.read().rstrip("\n"))
