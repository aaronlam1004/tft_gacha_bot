from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

class TFTImage:

	# Draws profile cards
	@staticmethod
	def profileCard(user, pic, username):
		width = 500
		height = 200

		image = Image.new('RGB', (width, height))
		draw = ImageDraw.Draw(image)

		background = Image.open("./resources/imgs/background.jpg")
		background = background.resize((width, height))
		image.paste(background, (0, 0))

		avatar = Image.open(pic)
		avatar = avatar.resize((75, 75))
		image.paste(avatar, (25, 25))
		
		thumbnail = Image.open(user.thumbnail)
		thumbnail.resize((50, 50))
		image.paste(thumbnail, (width - 115, 25))

		coin = Image.open("./resources/imgs/coin.png")
		coin = ImageOps.fit(coin, size = (25, 25))
		image.paste(coin, (110, 75), coin)

		font = ImageFont.truetype("./resources/fonts/Everson Mono Bold.ttf", size = 18)
		draw.text((140, 75), f'{user.gold}', fill = (255, 255, 255), font = font)
		text_height = draw.textsize(f'{user.gold}', font = font)[1]
		draw.text((110, 70 - text_height), f'Level: {user.level}', fill = (255, 255, 255), font = font)
		font = ImageFont.truetype("./resources/fonts/Everson Mono Bold.ttf", size = 25)
		draw.text((110, 20), f'{username}', fill = (255, 255, 255), font = font)

		if user.level < 9:
			draw.rectangle([25, 120, width - 50, height - 50], fill = (255, 0, 0))
			level_amount = user.xp_table[user.level]

			if level_amount == 0:
				level_amount = 1
			
			if user.xp > 0:
				draw.rectangle([25, 120, (width - 50) * (user.xp / level_amount), height - 50], fill = (0, 255, 0))

		text = f'XP: {user.xp}/{user.xp_table[user.level]}'
		text_width = draw.textsize(text, font = font)[0]
		draw.text((25, 150), text, fill = (255, 255, 255), font = font)	

		buff = io.BytesIO()
		image.save(buff, format = "PNG")
		buff.seek(0)
		return buff


	# Draws the character cards for units
	@staticmethod
	def championCard(tft, champ):
		champ = tft.getChampionName(champ)

		borders = {
			1: (23, 36, 51), 
			2: (64, 191, 119),
			3: (65, 117, 190),  
			4: (196, 38, 197), 
			5: (244, 154, 45)
		}

		width = 300
		height = 250

		image = Image.new('RGB', (width, height))
		draw = ImageDraw.Draw(image)

		background = Image.open("./resources/imgs/background.jpg")
		background = background.resize((width, height))
		image.paste(background, (0, 0))

		champion = Image.open(tft.getChampionImage(champ)) 
		champion.resize((75, 75))
		champion = ImageOps.expand(champion, border = 10, fill = borders[tft.getChampionTier(champ)])
		image.paste(champion, (25, 25))

		font = ImageFont.truetype("./resources/fonts/Everson Mono Bold.ttf", size = 25)
		draw.text((120, 30), champ, fill = (255, 255, 255), font = font)
		text_height = draw.textsize(champ, font = font)[1]

		coin = Image.open("./resources/imgs/coin.png")
		coin = ImageOps.fit(coin, size = (25, 25))
		image.paste(coin, (120, 25 + text_height + 10), coin)

		font = ImageFont.truetype("./resources/fonts/Everson Mono Bold.ttf", size = 18)
		draw.text((145, 25 + text_height + 10), str(tft.getChampionTier(champ)), fill = (255, 255, 255), font = font)

		font = ImageFont.truetype("./resources/fonts/Everson Mono.ttf", size = 18)

		yPlacement = 120
		for trait in tft.getChampionTraits(champ):
			t = Image.open(tft.getTraitImage(trait))
			t = ImageOps.fit(t, size = (45, 45))
			image.paste(t, (25, yPlacement), t)
			draw.text((75, yPlacement + 10), trait, fill = (255, 255, 255), font = font)
			yPlacement += 45 

		buff = io.BytesIO()
		image.save(buff, format = "PNG")
		buff.seek(0)
		return buff