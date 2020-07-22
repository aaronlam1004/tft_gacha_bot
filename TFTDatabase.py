import pymongo
import bson
from PIL import Image, ImageDraw, ImageFont
import io
import discord

class TFTDatabase:

	def __init__(self):
		client = pymongo.MongoClient("mongodb://localhost:27017")
		self.tft_db = client["tft_gacha"]

	def userExists(self, user):
		if self.tft_db["users"].find({"id": bson.int64.Int64(user.id)}).count() == 1:
			return True
		return False

	def addUser(self, user):
		user_col = self.tft_db["users"]
		values = {
			"id": user.id,
			"title": "{user}'s Collection".format(user = user.name),
			"thumbnail": "./resources/sadporo.png",
			"champions": [],
			"items": [],	
			"level": 1,
			"xp": 0,
			"gold": 10
		}
		user_col.insert_one(values)

	def getUser(self, user):
		return User(self.tft_db["users"].find_one({"id": bson.int64.Int64(user.id)}), self.tft_db)


class User:
	def __init__(self, user_data, db):
		self.id = user_data["id"]
		self.title = user_data["title"]
		self.thumbnail = user_data["thumbnail"]
		self.champions = user_data["champions"]
		self.items = user_data["items"]
		self.level = user_data["level"]
		self.xp = user_data["xp"]
		self.gold = user_data["gold"]

		self.db = db
		self.xp_table = {
			1: 8,
			2: 16,
			3: 32,
			4: 64,
			5: 128,
			6: 256,
			7: 512,
			8: 1024		
		}

	def _update(self):
		updated = self.db["users"].find_one({"id": bson.int64.Int64(self.id)})
		self.id = updated["id"]
		self.title = updated["title"]
		self.thumbnail = updated["thumbnail"]
		self.champions = updated["champions"]
		self.items = updated["items"]
		self.level = updated["level"]
		self.xp = updated["xp"]
		self.gold = updated["gold"]
	
	def addChampion(self, champion):
		curr_query = {"id": self.id} 
		new_query = {"$push": {"champions": champion}}
		self.db["users"].update(curr_query, new_query)
		self._update()

	def removeChampion(self, champion):
		count = 0
		for champ in self.champions:
			if champ == champion:
				count += 1
		if count == 0:
			return False
		else:
			curr_query = {"id": self.id}
			new_query = {"$pull": {"champions": champion}}
			self.db["users"].update(curr_query, new_query)
			readd = [champion] * (count - 1)
			new_query  = {"$push": {"champions": {"$each": readd}}}
			self.db["users"].update(curr_query, new_query)
			self._update()
			return True
			
	def addItem(self, item):
		curr_query = {"id": self.id} 
		new_query = {"$push": {"items": item}}
		self.db["users"].update(curr_query, new_query)
		self._update()
		
	def setThumbnail(self, champion = None, img = None):
		if champion == None and img == None:
			curr_query = {"id": self.id} 
			new_query = {"$set": {"thumbnail": "./resources/sadporo.png"}}
			self.db["users"].update(curr_query, new_query)
			self._update()
			return True
		elif champion in self.champions:
			curr_query = {"id": self.id} 
			new_query = {"$set": {"thumbnail": img}}
			self.db["users"].update(curr_query, new_query)
			self._update()
			return True	
		else:
			return False
	
	def changeGold(self, amount):
		if self.gold + amount >= 0:
			curr_query = {"id": self.id} 
			new_query = {"$set": {"gold": self.gold + amount}}
			self.db["users"].update(curr_query, new_query)
			self._update()
			return True
		else:
			return False
	
	def gainXP(self, amount):
		level_up = False
		xp_table = {
			1: 0,
			2: 2,
			3: 6,
			4: 10,
			5: 20,
			6: 32,
			7: 50,
			8: 66		
		}
		if self.level < 9:
			new_xp = self.xp + amount
			new_level = self.level
			if xp_table[self.level] <= new_xp:
				new_xp -= xp_table[self.level]
				new_level += 1
				level_up = True
			curr_query = {"id": self.id} 
			new_query = {"$set": {"xp": new_xp, "level": new_level}}
			self.db["users"].update(curr_query, new_query)
			self._update()
		return level_up

	def getLevel(self, profile_img_buffer, profile_name):
		xp_table = {
			1: 0,
			2: 2,
			3: 6,
			4: 10,
			5: 20,
			6: 32,
			7: 50,
			8: 66		
		}

		width = 500
		height = 200
		image = Image.new('RGB', (width, height))
		draw = ImageDraw.Draw(image)

		background = Image.open("./resources/background.jpg")
		background = background.resize((500, 200))
		image.paste(background, (0, 0))

		avatar = Image.open(profile_img_buffer)
		avatar = avatar.resize((75, 75))
		image.paste(avatar, (25, 25))
		
		font = ImageFont.truetype("./resources/Friz Quadrata Regular.ttf", size = 18)
		text = f'{profile_name}\nLevel: {self.level}\nGold: {self.gold}'
		text_width, text_height = draw.textsize(text, font = font)
		draw.text((110, 100 - text_height), text, fill = (255, 255, 255), font = font)

		if self.level < 9:
			draw.rectangle([25, 120, width - 50, height - 50], fill = (255, 0, 0))
			level_amount = xp_table[self.level]

			if level_amount == 0:
				level_amount = 1
			
			if self.xp > 0:
				draw.rectangle([25, 120, (width - 50) * (self.xp / level_amount), height - 50], fill = (0, 255, 0))

		text = f'XP: {self.xp}/{xp_table[self.level]}'
		text_width, text_height = draw.textsize(text, font = font)
		draw.text((25, 160), text, fill = (255, 255, 255), font = font)	
	
		buff = io.BytesIO()
		#image.save("test_imgs/test.png", format="PNG")
		image.save(buff, format="PNG")
		buff.seek(0)
		return buff
