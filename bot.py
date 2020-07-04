import discord
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

	@client.event
	async def on_ready():
		print('We have logged in as {0.user}'.format(client))
	
	@client.event
	async def on_message(message):
		if message.author == client.user:
			return
		if message.content.startswith('$tft summon'):
			for _ in range(3):
				champ = tft.summonChampion(5)
				champ_img = discord.File(('./set3/champions/' + str(champ).lower() ).replace(" ", "").replace("-", "").replace("'", "") + '.png', filename = "champ.png")
				champ_descrip = ""

				for trait in tft.getTraits(champ):
					emoji = None
					with open(('./set3/traits/' + trait.lower()).replace(" ", "").replace("-", "") + ".png", "rb") as img:
						emoji = await message.guild.create_custom_emoji(name = trait.lower().replace(" ", "").replace("-", ""), image = img.read())
					champ_descrip = champ_descrip + trait + " " + str(emoji) + "\n" 

				embedded = discord.Embed(
					title = str(champ),
					description = champ_descrip,
					colour = discord.Colour(tier_colors[tft.getTier(champ)])
				)
				embedded.set_thumbnail(url = "attachment://champ.png")

				await message.channel.send(file = champ_img, embed = embedded)

	@client.event
	async def on_reaction_add(reaction, user):
			def check(reaction, user):
				return str(reaction.emoji) == '👍'
			message = await client.fetch_message(reaction.message.channel, reaction.message.id)
				
	
	client.run('NzI4MzkwMDM2ODY5MDg3MzIz.Xv5tmg.T-Wp9UOYvcYXen9jyr1tMB1QQog')
