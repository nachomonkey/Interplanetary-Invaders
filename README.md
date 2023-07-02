# Interplanetary Invaders

Shoot off into the solar system after space invaders attack Earth!  But beware, each planet is riddled with new tricks and threats...  Earn new vehicles like NASA's Curiosity rover, conquer intimidating bosses, and shoot many, many lasers.  Realistic physics, diverse power-ups, vivid explosions, and sciencey vibes separate this game from your typical space-invaders clone.

## Installation

First make sure you have Python installed and set up (python 3.7 or greater), and then run this from the command prompt:

```bash
python -m pip install interplanetary-invaders --user
```



## Running the game

After installing with `pip`, run the game with this command:

```bash
python -m interplanetary_invaders
```

Or run the `run_game.py` script to launch it from the repo directory.

Installation with `pip` may also create the `interplanetary-invaders` command-line entrypoint.



## Playing the game

 ![Gameplay Screenshot](https://raw.githubusercontent.com/nachomonkey/Interplanetary-Invaders/master/docs/collage.png)

First pick a mission in Map mode. Alien spaceships come from the top-left of the screen. Dodge falling rocks and don't let the spaceships come to you. Win by blowing all the spaceships up with your lasers.

##### Gameplay controls:

* **Left/Right Arrow keys**: Move your vehicle left and right
* **Space bar / UP Arrow**: Fire lasers upward
* **Y**: Opens the deploy item menu
* **Number keys (1 to 9)**: A faster way to deploy items
* **Q and E**: Aims the pivoting turret on the Curiosity Rover or Jupiter Hovercraft vehicles
* **Left Shift**: Fires Flak Bursts upwards while the Flak Bursts item is active. Hold longer to fire higher.
* **F2**: Take screenshot

You can also play with a game controller. The controls are mapped for the X-Box 360 controller.

##### Developer's notes:

Your vehicle has two health bars: Health (green) and Shield (blue). Damage you take will first deplete your Shield health. Even the smallest fraction of Shield health will protect your vehicle from any hit- including a live alien spaceship ramming in to you.

Items are very important! It is nearly impossible to play the game without usage of items. The "Auto Gun" item lets you hold down Spacebar to fire continuously instead of having to mash the key. It will save your keyboard.

The levels on Earth (especially Tropical Terror and Icy Invasion) are the most difficult levels in the game. These levels come before the Stores get unlocked, so items are limited. Don't give up; the game gets a lot better once you make it past Earth.

Certain levels (especially on Venus) will quickly damage your vehicle without you being hit. This is thermal damage, caused by the high temperature of that level. You must purchase the Venus Crawler vehicle from a Store and select it before playing these missions; it can survive the heat. To use the Venus Crawler on a different planet, you first need to purchase the "Space Transport License II" item from a Store.

*The game does not have a proper ending at the moment, but I dare you to beat all of the missions.*



## Acknowledgements

### Game assets:

* Credit to NASA for many of the realistic space images used in the game, as described in the credits.
* [Flak Bursts sound](https://freesound.org/people/zimbot/sounds/209984/) (modified) is by [zimbot](https://freesound.org/people/zimbot/) (CC BY 4.0)
* Cash Register sound is by [kiddpark](https://freesound.org/people/kiddpark/) (CC BY 4.0)
* The green alien crash sound was made with a sound by [spoonsandlessspoons](https://freesound.org/people/spoonsandlessspoons/) (CC BY 4.0)

### Other contributers:

* @XracerX- documentation edits, moved from mp3 to ogg

  

## License

This software is under the GNU GPLv3 License. See the [LICENSE](https://github.com/nachomonkey/Interplanetary-Invaders/blob/master/LICENSE) file to read it.

