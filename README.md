# CS50: Cat VS Slimes v0.50

Welcome to Cat vs Slimes, my Harvard's CS50 course final project, which was developed using the Pygame library for python and the software Tiled, which handles the map creation.
![MEOWgician](/screenshots_gifs/cat.gif)

## Game Objective

In CS50, your objective is to help our **MEOWgician** to defeat all slimes that have been terrorizing the village. Once 90% or more of the slimes have been defeated,
you have to take our feline hero to the "blessed statue", which will purify the village from all the slime menace.

![Objective not finished](/screenshots_gifs/statue_off.gif) ![Objective finished](/screenshots_gifs/statue_on.gif)

## "Features"

- A controllable character that has multiple states: "idle", "attacking" and "running", where each state has a different animation.
- Interactive map, in which map assets have collision detection and some are interactive.
- Enemies that interact with the player based on the distance between both.
![Slime](/screenshots_gifs/slime_death.gif)
- Player has 4 different spells that can be cycled, each with a unique characteristics and animations.
![Ice spell](/screenshots_gifs/ice_spell.gif)
![Fire spell](/screenshots_gifs/fire_spell.gif)
![Wind spell](/screenshots_gifs/wind_spell.gif)
- Sound effects to increase player experience.
- Game provides a level up mechanic, in which the player receives stat points when it level's up and can increase the hero's attributes.

![Leveling](/screenshots_gifs/levelup.gif)
- Interactive menu, endscreen and a instructions screen, which create a more positive overall experience.
- Responsive GUI that shows the player's main attributes, such as HP, MP and Experience.

## Installing the game

# Prerequisites

Before you begin, ensure you have the following installed on your system:

1. [Python](https://www.python.org/downloads/) (version 3.6 or later)
2. [Pygame](https://www.pygame.org/download.shtml)
3. [PyTMX](https://github.com/bitcraft/PyTMX) (a Python library for parsing TMX map files, to handle the 
Tileset)

# Downloading the Game

**Download or Clone the Repository:**
   - Click on the "Code" button and select "Download ZIP" to download the repository as a ZIP file.
   - Alternatively, you can clone the repository using Git by running the following command in your terminal:
     ```
     git clone https://github.com/cschwatz/Cat_vs_Slimes
     ```

# Installation

In the case that you do not have one or more of the prerequisites:

1. **Python:**
   - Download and install Python from the official website: [Python Downloads](https://www.python.org/downloads/)
   - During installation, make sure to add Python to your system's PATH.
   
2. **Pygame:**
   - Open a terminal/command prompt.
   - Install Pygame using pip by running the following command:
     ```
     pip install pygame
     ```
     
3. **PyTMX:**
   - In the same terminal/command prompt, install PyTMX using pip:
     ```
     pip install pytmx
     ```

# Running the Game

You can run the "Cat_vs_Slimes" game either from the command line or from an IDE of your choice.
**IMPORTANT**: Make sure that you are running the ```main.py``` file and that you do **NOT** rename any file or folder.

## Things That Could Be Improved

Although the game fulfills the objective of Harvard's CS50 final project, some quality of life changes could be implemented:

- **More Variety**: Even though the game is all about slaying slimes, maybe a final boss could've been implemented.
- **improved collision**: Since rectangular hitboxes were used in this project, collision might fell wonky/unfair sometimes. Thus, switching the collision mechanic
to be handled by pygame masks would probably result in a better experience.
- **Sounds**: Sounds seem a little wonky, as in, sometimes they are played correctly and sometimes they are not.
- **Optimization**: The code could be  optimized in many ways. One particular way is to reduce repetition of methods, such as the method ```load_sprite``` which returns a subsurface to act as a frame of an animation. This method is used by many files in the project, which could have been implemented in a single support file and imported to the others.

## Credits

Cat vs Slimes v.050 was created by [Cristian Schwatz](https://github.com/cschwatz). Special thanks to the Pygame community and the people at the Pygame discord.

Since the objective of this project was to improve my ability to write code and develop a "full" game, many assets were taken from [itch.io](https://itch.io/game-assets/)
List of assets taken:
  - **Tileset**:
    - (https://almostapixel.itch.io/small-burg-village-pack)
  - **Sounds**:
    - (https://gamesupply.itch.io/1000-nintendo-sound-effects)
    - (https://harvey656.itch.io/freesfxforanything)
    - (https://yourpalrob.itch.io/classic-arcade-sound-effects)
    - (https://mythril-age.itch.io/mythril-age-sfx-pack-v1)
    - (https://leohpaz.itch.io/rpg-essentials-sfx-free)
  - **Music**:
    - (https://ryanavx.itch.io/final-quest-music-pack)
  - **Sprites**:
    - **Character**:
      - (https://9e0.itch.io/cute-legends-cat-heroes) (Knigth character was used as base for the character)
    - **Spells**:
      - (https://pixerelia.itch.io/vas-basic-spells-and-buffs) (Spell's icons)
      - (https://pimen.itch.io/) (projectile spells)
      - (https://pixel-boy.itch.io/ninja-adventure-asset-pack)(Heal)
    - **Slimes**:
      - (https://joao9396.itch.io/pixel-art-monsters?download) (Slimes)
      - (https://game-endeavor.itch.io/mystic-woods) (Slime's death animation)
  - **User Interface**:
      - (https://crusenho.itch.io/complete-gui-essential-pack)
      - (https://paperhatlizard.itch.io/cryos-mini-gui)
  - **Font**:
      - (https://joebrogers.itch.io/bitpotion)
  - **Menu backgrounds**:
      - (https://caniaeast.itch.io/simple-sky-pixel-backgrounds)
    
## License

This project is published under the Creative Commons Zero (CC0) license. However, it is important to point out that each asset/sprite/sound used in this project
has its own licence, and thus, they are displayed at the credits section, so that everything that was used can be checked.
