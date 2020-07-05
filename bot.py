import discord
import re
import sys
from TFTGacha import TFTGacha

if __name__ == '__main__':

	client = discord.Client()
	tft = TFTGacha()

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
					await channel.send("Updating server...")
			for e in client.emojis:
				await discord.Emoji.delete(e)
			for guild in client.guilds:
				for channel in guild.text_channels:
					await channel.send("Server finished updating!")

	@client.event
	async def on_message(message):
		if message.author == client.user:
			return

		elif message.content.startswith('$tft champion') or message.content.startswith('$tft c'):
			for _ in range(3):
				champ = tft.summonChampion(5)
				champ_img = discord.File(('./set3/champions/' + str(champ).lower() ).replace(" ", "").replace("-", "").replace("'", "") + '.png', filename = "champ.png")
				champ_descrip = ""

				for trait in tft.getTraits(champ):
					#emoji = await find_emoji(message, trait)
					#champ_descrip = champ_descrip + trait + " " + str(emoji) + "\n" 
					champ_descrip = champ_descrip + trait + "\n" 

				embedded = discord.Embed(
					title = str(champ),
					description = champ_descrip,
					colour = discord.Colour(tier_colors[tft.getTier(champ)])
				)
				embedded.set_thumbnail(url = "attachment://champ.png")

				await message.channel.send(file = champ_img, embed = embedded)

	@client.event
	async def on_reaction_add(reaction, user):
		try:
			message = str(user.mention) + " has claimed **" +  str(reaction.message.embeds[0].title) + "**"
			await reaction.message.channel.send(message)
		except:
			pass	

	client.run('DISCORD BOT KEY GOES HERE')
