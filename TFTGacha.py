import json
import random
from collections import defaultdict

class TFTGacha():

	def __init__(self):
		f = open("./resources/set3/champions.json")
		champions = json.load(f)

		self.champion_dict = defaultdict(list)
		for champion in champions:
			self.champion_dict[champion["cost"]].append({"name": champion["name"], "traits": champion["traits"]})	

		f = open("./resources/set3/items.json")
		items = json.load(f)
		self.item_dict = defaultdict(list)
		self.item_dict["base"] = items[0: 7]
		self.item_dict["base"].append(items[8])

		self.item_dict["combined"] = items[9:]
		self.item_dict["combined"].append(items[7])

	def _getChampionDict(self):
		return self.champion_dict

	def _getItemDict(self):
		return self.item_dict
	
	# Logic to choose a champion
	def summonChampion(self, level):
		prob_dict = {
			1: {1: 1, 2: 0, 3: 0, 4: 0, 5: 0},
			2: {1: 1, 2: 0, 3: 0, 4: 0, 5: 0},
			3: {1: .65, 2: .3, 3: .05, 4: 0, 5: 0},
			4: {1: .5, 2: .35, 3: .15, 4: 0, 5: 0},
			5: {1: .37, 2: .35, 3: .25, 4: .03, 5: 0},
			6: {1: .245, 2: .35, 3: .3, 4: .1, 5: .05},
			7: {1: .2, 2: .3, 3: .33, 4: .15, 5: .02},
			8: {1: .15, 2: .25, 3: .35, 4: .2, 5: .05},
			9: {1: .10, 2: .15, 3: .35, 4: .3, 5: .1}
		}

		rng = random.random()
		curr_prob = 0 
		for k, v in prob_dict[level].items():
			curr_prob += v
			if rng <= curr_prob:
				champion_select = random.randint(0, len(self.champion_dict[k]) - 1) 
				return self.champion_dict[k][champion_select]["name"]

	# Checks to see if champion exists
	def championExists(self, champion):
		for k in self.champion_dict.keys():
			for champ in self.champion_dict[k]:
				if champ["name"].lower() == champion.lower():
					return True
		return False

	# Gets correct spelling of champion
	def getChampionName(self, champion):
		for k in self.champion_dict.keys():
			for champ in self.champion_dict[k]:
				if champ["name"].lower() == champion.lower():
					return champ["name"]

	# Get champion traits from champion name
	def getChampionTraits(self, champion):
		for k in self.champion_dict.keys():
			for champ in self.champion_dict[k]:
				if champ["name"].lower() == champion.lower():
					return champ["traits"] 

	# Get champion tier (normal -> legendary) from champion name
	def getChampionTier(self, champion):
		for k in self.champion_dict.keys():
			for champ in self.champion_dict[k]:
				if champ["name"].lower() == champion.lower():
					return k

	# Get champion image from champion name
	def getChampionImage(self, champion):
		return ("./resources/set3/champions/" + str(champion).lower()).replace(" ", "").replace("-", "").replace("'", "") + ".png"

	# Logic to choose an item
	def summonItem(self, level):
		prob_dict = {
			1: 1,
			2: 1,
			3: 1,
			4: .95,
			5: .75,
			6: .55, 
			7: .45,
			8: .1,
			9: .05
		}

		rng = random.random()	
		if rng <= prob_dict[level]:
			item_select = random.randint(0, len(self.item_dict["base"]) - 1) 
			return self.item_dict["base"][item_select]["name"]
		else:
			item_select = random.randint(0, len(self.item_dict["combined"]) - 1) 
			return self.item_dict["combined"][item_select]["name"]

	# Get item id from item name
	def getItemId(self, chosen):
		for k in self.item_dict.keys():
			for item in self.item_dict[k]:
				if chosen.lower() == item["name"].lower():
					return item["id"]

	# Gets correct spelling of item
	def getItemName(self, chosen):
		for k in self.item_dict.keys():
			for item in self.item_dict[k]:
				if chosen.lower() == item["name"].lower():
					return item["name"]

	# Checks to see if item exists
	def itemExists(self, chosen):
		for k in self.item_dict.keys():
			for item in self.item_dict[k]:
				if chosen.lower() == item["name"].lower():
					return True
		return False

	# Get item image from item name
	def getItemImage(self, item):
		return "./resources/set3/items/" + str(self.getItemId(item)).zfill(2) + ".png"
	
	# Get trait image from trait name
	def getTraitImage(self, trait):
		return ("./resources/set3/traits/" + str(trait).lower()).replace(" ", "").replace("-", "").replace("'", "") + ".png"
