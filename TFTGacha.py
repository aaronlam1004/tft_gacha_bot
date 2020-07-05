import json
import random
from collections import defaultdict

class TFTGacha():

	def __init__(self):
		f = open('./set3/champions.json')
		champions = json.load(f)

		self.champion_dict = defaultdict(list)
		for champion in champions:
			self.champion_dict[champion['cost']].append((champion['name'], champion['traits']))	

		f = open('./set3/items.json')
		items = json.load(f)
		self.item_dict = defaultdict(list)
		self.item_dict["base"] = items[0: 9]
		self.item_dict["combined"] = items[9:]

	def _getChampionDict(self):
		return self.champion_dict

	def _getItemDict(self):
		return self.item_dict
	
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
				return self.champion_dict[k][champion_select][0]

	def getTraits(self, champion):
		for k in self.champion_dict.keys():
			for champ in self.champion_dict[k]:
				if champ[0] == champion:
					return champ[1]

	def getTier(self, champion):
		for k in self.champion_dict.keys():
			for champ in self.champion_dict[k]:
				if champ[0] == champion:
					return k
