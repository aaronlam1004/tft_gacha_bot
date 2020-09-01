import pymongo
import bson
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
			"thumbnail": "./resources/imgs/sadporo.png",
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
			1: 4,
			2: 8,
			3: 16,
			4: 32,
			5: 64,
			6: 128,
			7: 256,
			8: 512		
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

	def hasChampion(self, champion):
		if champion in self.champions:
			return True
		return False

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

		curr_query = {"id": self.id}
		new_query = {"$pull": {"champions": champion}}
		self.db["users"].update(curr_query, new_query)

		readd = [champion] * (count - 1)
		new_query  = {"$push": {"champions": {"$each": readd}}}
		self.db["users"].update(curr_query, new_query)

		self._update()
	
	def hasItem(self, item):
		if item in self.items:
			return True
		return False

	def addItem(self, item):
		curr_query = {"id": self.id} 
		new_query = {"$push": {"items": item}}
		self.db["users"].update(curr_query, new_query)
		self._update()

	def removeItem(self, item):
		count = 0
		for i in self.items:
			if item == i:
				count += 1

		curr_query = {"id": self.id}
		new_query = {"$pull": {"items": item}}
		self.db["users"].update(curr_query, new_query)

		readd = [item] * (count - 1)
		new_query  = {"$push": {"items": {"$each": readd}}}
		self.db["users"].update(curr_query, new_query)

		self._update()
		
	def setThumbnail(self, champion = None, img = None):
		if champion == None and img == None:
			curr_query = {"id": self.id} 
			new_query = {"$set": {"thumbnail": "./resources/imgs/sadporo.png"}}
			self.db["users"].update(curr_query, new_query)
			self._update()
		else:
			curr_query = {"id": self.id} 
			new_query = {"$set": {"thumbnail": img}}
			self.db["users"].update(curr_query, new_query)
			self._update()
	
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
		
		if self.level < 9:
			new_xp = self.xp + amount
			new_level = self.level
			if self.xp_table[self.level] <= new_xp:
				new_xp -= self.xp_table[self.level]
				new_level += 1
				level_up = True
			curr_query = {"id": self.id} 
			new_query = {"$set": {"xp": new_xp, "level": new_level}}
			self.db["users"].update(curr_query, new_query)
			self._update()
		return level_up
