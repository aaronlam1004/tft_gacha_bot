import discord
import re
import json
import sys
from TFTGacha import TFTGacha

if __name__ == '__main__':

	client = discord.Client()
	tft = TFTGacha()
	
	data = {}
	with open('storage.json', 'r') as json_file:
		data = json.load(json_file)

	tier_colors = {
		1: 0x172433,
		2: 0x40bf77,
		3: 0x4175be,
		4: 0xc426c5,
		5: 0xf49a2d
	}

	async def find_emoji(message, trait):
		e = trait.lower().replace(" ", "").replace("-", "")
		if len(client.emojis) > 0:
			for emoji in client.emojis:
				if e in emoji:
					emoji_id = re.match('[0-9]+', emoji)
					return await client.get_emoji(emoji_id)
		with open('./set3/traits/' + e + ".png", "rb") as img:
			return await message.guild.create_custom_emoji(name = e, image = img.read())

	@client.event
	async def on_ready():
		print('We have logged in as {0.user}'.format(client))

		if len(sys.argv) == 2 and sys.argv[1] == "--update":
			for guild in client.guilds:
				for channel in guild.text_channels:
					await channel.send("Removing all custom emojis from server...")
			for e in client.emojis:
				await discord.Emoji.delete(e)
			for guild in client.guilds:
				for channel in guild.text_channels:
					await channel.send("Bot finished updating!")

	@client.event
	async def on_message(message):
		if message.author == client.user:
			return

		elif message.content.startswith('$tft summon') or message.content.startswith('$tft s'):
			for _ in range(3):
				imgs = []
				item = tft.summonItem(5)
				item_id = str(tft.getItemId(item)).zfill(2)
				item_img = discord.File('./set3/items/' + str(item_id) + '.png', filename = "item.png")
				imgs.append(item_img)

				champ = tft.summonChampion(5)
				champ_img = discord.File(('./set3/champions/' + str(champ).lower() ).replace(" ", "").replace("-", "").replace("'", "") + '.png', filename = "champ.png")
				imgs.append(champ_img)
				champ_descrip = ""

				for trait in tft.getChampionTraits(champ):
					#emoji = await find_emoji(message, trait)
					#champ_descrip = champ_descrip + trait + " " + str(emoji) + "\n" 
					champ_descrip = champ_descrip + trait + "\n"

				embedded = discord.Embed(
					title = champ,
					description = champ_descrip,
					colour = discord.Colour(tier_colors[tft.getChampionTier(champ)])
				)

				embedded.set_thumbnail(url = "attachment://champ.png")
				embedded.set_footer(text  = item, icon_url = "attachment://item.png")

				await message.channel.send(files = imgs, embed = embedded)
		
		elif message.content.startswith('$tft list') or message.content.startswith('$tft ls') :
			if not message.author in data:
				data[str(message.author)] = {"title": str(message.author) + '\'s Collection', "thumbnail": "./sadporo.png", "champions": [], "items": []}
				with open("storage.json", 'w') as outfile:
					json.dump(data, outfile)

			thumb = discord.File(data[str(message.author)]["thumbnail"], filename = "thumbnail.png")
			embedded = discord.Embed(
				title = data[str(message.author)]["title"]
			)
			embedded.set_thumbnail(url = "attachment://thumbnail.png")
			await message.channel.send(file = thumb, embed = embedded)

	@client.event
	async def on_reaction_add(reaction, user):
		try:
			message = str(user.mention) + " has claimed **" +  str(reaction.message.embeds[0].title) + "**"
			await reaction.message.channel.send(message)
		except:
			pass	

	with open("key.txt", "r") as key:
		client.run(key.read().rstrip("\n"))
