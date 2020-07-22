import discord
import sys
from os import path
from TFTGacha import TFTGacha
from TFTDatabase import TFTDatabase
import io

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
				item_img = discord.File(tft.getItemImage(item), filename = "item.png")
				imgs.append(item_img)

				champ = tft.summonChampion(tft_user.level)
				champ_img = discord.File(tft.getChampionImage(champ), filename = "champ.png")
				imgs.append(champ_img)
				champ_descrip = ""

				'''emojis = []'''
				champ_descrip += "Cost: **" + str(tft.getChampionTier(champ)) + "**\n"
				for trait in tft.getChampionTraits(champ):
					'''
					trait_name = trait.lower().replace(" ", "").replace("-", "").replace("'", "")
					trait_img = None
					with open("./resources/set3/traits/" + trait_name + ".png", "rb") as image:
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
		elif message.content.startswith(client_mention + " collection") or message.content.startswith(client_mention + " ls") :
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

				if not tft_user.setThumbnail(champ, tft.getChampionImage(champ)):
					await message.channel.send(message.author.mention + " Could not set profile icon to **" + champ + "** because you do not have it.")
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

				champ = ""
				for i in range(2, len(sent)):
					champ += sent[i] 
					if i != len(sent)	- 1:
						champ += " "

				if tft_user.removeChampion(champ):
					if tft.getChampionImage(champ) == tft_user.thumbnail and champ not in tft_user.champions:
						if len(tft_user.champions) == 0:
							tft_user.setThumbnail()
						else:
							tft_user.setThumbnail(tft_user.champions[0], tft.getChampionImage(tft_user.champions[0]))
					gold = tft.getChampionTier(champ)
					tft_user.changeGold(gold)
					await message.channel.send(message.author.mention + " Successfully sold **" + champ + "** for " + str(gold) + " gold.")
				else:
					await message.channel.send(message.author.mention + " Cannot sell **" + champ + "** because you do not own it.")

		elif message.content.startswith(client_mention + " lvl") or message.content.startswith(client_mention + " up"):
			if not database.userExists(message.author):
				database.addUser(message.author)
			tft_user = database.getUser(message.author)

			avatar_asset = message.author.avatar_url_as(format = "jpg")
			avatar_buffer = io.BytesIO()
			await avatar_asset.save(avatar_buffer)
			avatar_buffer.seek(0)

			if tft_user.level == 1:
				tft_user.gainXP(0)
				await message.channel.send(message.author.mention + " has leveled up! You are now level **" + str(tft_user.level) + "**!")
				progressbar = discord.File(tft_user.getLevel(avatar_buffer, message.author), filename = "progressbar.png")
				await message.channel.send(file = progressbar)
			elif tft_user.changeGold(-4):
				progressbar = discord.File(tft_user.getLevel(avatar_buffer, message.author), filename = "progressbar.png")
				if tft_user.gainXP(4):
					await message.channel.send(message.author.mention + " has leveled up! You are now level **" + str(tft_user.level) + "**!")
					progressbar = discord.File(tft_user.getLevel(avatar_buffer, message.author), filename = "progressbar.png")
					await message.channel.send(file = progressbar)
				else:
					progressbar = discord.File(tft_user.getLevel(avatar_buffer, message.author), filename = "progressbar.png")
					await message.channel.send(file = progressbar)
			else:
				await message.channel.send(message.author.mention + " **You do not have enough gold to gain XP.**")

		elif message.content.startswith(client_mention + " profile") or message.content.startswith(client_mention + " me"):
			if not database.userExists(message.author):
				database.addUser(message.author)
			
			tft_user = database.getUser(message.author)

			avatar_asset = message.author.avatar_url_as(format = "jpg")
			avatar_buffer = io.BytesIO()
			await avatar_asset.save(avatar_buffer)
			avatar_buffer.seek(0)
			
			await message.channel.send(file = discord.File(tft_user.getLevel(avatar_buffer, message.author), filename = "userprogress.png"))

		elif message.content.startswith(client_mention + " help") or message.content.startswith(client_mention + " h"):
			text = ""
			with open("./tutorial.txt", "r") as infile:
				text = infile.read()
			
			while len(text) > 2000:
				await message.author.send(text[0:2000])
				text = text[2000:]
			await message.author.send(text)
	
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

					if tft_user.thumbnail == "./resources/sadporo.png":
						thumbnail = "./resources/set3/champions/" + champ.lower().replace(" ", "").replace("-", "").replace("'", "") + ".png"
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
