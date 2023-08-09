WIDTH = 800
HEIGHT = 600
FPS = 60
TILESIZE = 32
WATER_COLOR = (77,166,255)

# hitbox offsets - all of them are in the Y direction, except barrier (x, y)
OFFSET_VALUE = {
    'Tree': -80,
    'Object': -80,
    'Store': -100,
    'Bush': -35,
    'Barrier': (-20, -30)
}

#magic

magic_data = {
    'fire': {'cost': 30, 'cooldown': 800, 'damage': 50},
    'ice': {'cost': 30, 'cooldown': 800, 'damage': 50},
    'wind': {'cost': 30, 'cooldown': 800, 'damage': 50},
    'heal': {'cost': 30, 'cooldown': 800, 'amount': 50}
}

#enemies
monster_data = {
	'blue': {'health': 100,'exp':10,'damage':15, 'speed': 2.8, 'resistance': 5, 'attack_radius': 80, 'notice_radius': 300},
	'green': {'health': 200,'exp':25,'damage':30, 'speed': 2, 'resistance': 10, 'attack_radius': 120, 'notice_radius': 400},
	'pink': {'health': 50,'exp':5,'damage':10, 'speed': 3.5, 'resistance': 3, 'attack_radius': 60, 'notice_radius': 200},
	'purple': {'health': 150,'exp':15,'damage':20, 'speed': 2.5, 'resistance': 7, 'attack_radius': 50, 'notice_radius': 320}}