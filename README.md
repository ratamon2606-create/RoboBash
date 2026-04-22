# RoboBash

## Project Description

- **Project by:** Ratamon Charoenratanakun
- **Game Genre:** Action, Arena Combat, 2-Player Local Multiplayer

RoboBash is a 2-player local arena combat game where each player builds a custom battle robot from six categories of interchangeable parts, then fights the opponent in a procedurally generated arena. Every match is automatically recorded, and a post-match analytics dashboard shows six data visualizations (accuracy, HP over time, positional heatmap, damage per weapon, weight vs. damage across all matches, and shooting frequency) so players can analyze their build choices.

---

## Installation

To clone this project:
```sh
git clone https://github.com/ratamon2606-create/RoboBash.git
cd RoboBash
```

To create and run the Python environment for this project:

**Windows:**
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**Mac / Linux:**
```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Requires Python 3.10 or newer.

---

## Running Guide

After activating the Python environment, run the game:

**Windows:**
```bat
python RoboBash.py
```

**Mac / Linux:**
```sh
python3 RoboBash.py
```

The `asset/` folder must be in the same directory as `RoboBash.py` — it contains all sprites, fonts, and audio.

---

## Tutorial / Usage

1. **Start Menu** — Click the START button to begin.
2. **Garage (Build Phase)** — Player 1 builds first, then Player 2.
   - Click a category tab on the left (Controller, Linkage, Gun, Motor, Power, Chassis) or use the arrow keys to cycle parts.
   - Watch the DPS, Weight, and Power bars at the top. If Weight exceeds your Linkage's capacity, or Power exceeds your Power unit's capacity, the bars turn red and you cannot proceed.
   - Click NEXT once your build is legal.
3. **Arena (Battle Phase)** — Both robots spawn on opposite sides of a procedurally generated obstacle layout.

### Controls

| Action | Player 1 | Player 2 |
|---|---|---|
| Move Up | W | ↑ |
| Move Down | S | ↓ |
| Move Left | A | ← |
| Move Right | D | → |
| Fire Weapon | SPACE | ENTER |

4. **End Screen** — When one robot is destroyed, the winner is announced. Choose **REMATCH** to replay with the same builds, or **EXIT** to close the game and open the **Match Analytics Dashboard** with all six data visualizations.

---

## Game Features

- **18 interchangeable parts** across 6 categories, each with real trade-offs in damage, weight, speed, and power draw.
- **Three unique weapons:** Machine Gun (3-projectile spread), Light Gun (fast, light), Laser Cannon (heavy, high damage).
- **Procedural arena:** obstacle layout is randomized every match, with safe zones around spawn points.
- **Directional sprites:** every robot build generates its own composite sprites for all four facing directions.
- **Weight and power validation:** illegal builds are blocked before the match starts.
- **Automatic match logging:** every movement, shot, hit/miss, and damage event is saved to CSV.
- **Analytics dashboard:** six visualizations (pie chart, line graph, heatmap, bar chart, scatter plot, table) in a Tkinter window.
- **Historical data:** the scatter plot pulls from all past matches, not just the current one.
- **Resizable window** with preserved aspect ratio.

---

## Known Bugs

- If an audio file in `asset/` is missing or in an unsupported format (e.g., `.mp3` on systems where SDL_mixer cannot decode it), the sound is replaced with a silent dummy and a warning is printed. The game remains playable.
- If a sprite asset is missing, a red placeholder square is drawn in its place.
- Very rarely, obstacle generation fails to find a valid placement within 100 attempts and simply skips that obstacle — this does not affect gameplay.

---

All planned features were completed.

---

## External Sources

Acknowledgements:
1. Pygame — [pygame.org](https://www.pygame.org) — game engine (LGPL)
2. Matplotlib — [matplotlib.org](https://matplotlib.org) — data visualizations
3. Determination — [dafont.com](https://www.dafont.com/determination.font) Lucca Cedro — main UI font
4. Dogica Pixel — [dafont.com](https://www.dafont.com/dogica.font) Roberto Mocci — small UI font
5. Burn the Map — [artlist.io](https://artlist.io/royalty-free-music/song/burn-the-map/6000740) AlexGrohl — background music for battle arena
6. Iron Bang — [pixabay.com](https://pixabay.com/id/sound-effects/film-efek-khusus-iron-bang-119810/) masp005 — sound effect for changing parts in garage
7. Gun Fire — [pixabay.com](https://pixabay.com/sound-effects/film-special-effects-gun-fire-346766/) Foisal72 — sound effect for Machine Gun shooting
8. Gunshot — [pixabay.com](https://pixabay.com/sound-effects/film-special-effects-gunshot-352466/) Universfield— sound effect for Light Gun shooting
9. Laser Gun — [pixabay.com](https://pixabay.com/sound-effects/film-special-effects-laser-gun-174976/) VoiceBosch — sound effect for Laser Cannon shooting