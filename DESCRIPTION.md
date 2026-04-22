# Project Description

## 1. Project Overview

- **Project Name:** RoboBash

- **Brief Description:**
  RoboBash is a 2-player local arena combat game built with Pygame, where each player builds a custom battle robot from six categories of interchangeable parts (Controller, Linkage, Gun, Motor, Power, Chassis) and then fights the opponent in a procedurally generated arena. Every part has trade-offs in damage, weight, power consumption, and mobility, so players must balance their loadout against weight capacity and power capacity limits before the match begins.

  After the match ends, every significant event, such as movement coordinates, shots fired, hits vs. misses, damage dealt, HP over time, is exported to CSV files and surfaced in a full statistics dashboard built with Matplotlib and Tkinter. The dashboard shows six different visualizations so players can analyze their performance and compare different robot builds across multiple matches.

- **Problem Statement:**
  Most arena fighting games hide their build systems behind locked progression or simplified stat bars, and almost none expose the underlying match data to the player. RoboBash solves two problems at once. It gives players a transparent, stat-driven robot customization system where every trade-off is visible up front, and it turns match telemetry into an accessible analytics dashboard so players can actually see *why* a build won or lost.

- **Target Users:**
  Players who enjoy local-multiplayer arcade combat games, fans of mech/robot customization games (Armored Core, Custom Robo), and anyone curious about data-driven game analytics. The game is suitable for casual play sessions with a friend on one keyboard.

- **Key Features:**
  - Six-category robot customization system with 3 parts per category (18 parts total)
  - Real-time weight and power capacity validation before battle
  - Two-player local combat on a single keyboard (WASD + SPACE vs. Arrow Keys + ENTER)
  - Procedurally generated obstacle layout each match
  - Three distinct weapon types with unique firing behavior (Machine Gun spread, Light Gun, Laser Cannon)
  - CSV logging of every match for persistent historical data
  - Post-match analytics dashboard with 6 different data visualizations
  - Resizable window that preserves aspect ratio

- **Screenshots:**
  See the `screenshots/` directory for gameplay and visualization captures.
  - Gameplay: `screenshots/gameplay/`
  - Data Dashboard: `screenshots/visualization/`

- **Proposal:**
  The original project proposal is available in this repository: [Proposal.pdf](./Proposal.pdf)

- **YouTube Presentation:**
  Watch the project demonstration here: []

  The video covers: (1) a short intro and demonstration of the game and statistics dashboard, (2) an explanation of the class design and how classes interact, and (3) an explanation of the statistics and data visualization.

---

## 2. Concept

### 2.1 Background

- **Why this project exists:** I wanted to build a game that wasn't just fun to play, but also *readable* — where the design decisions a player makes during the build phase are reflected in concrete numbers after the match ends. Most arcade games treat stats as invisible; RoboBash treats them as the main feature.

- **What inspired it:** The project was inspired by mech-building games like Armored Core and Custom Robo, combined with a curiosity about competitive esports analytics dashboards. The goal was to merge those two worlds into something small enough for a class project but deep enough to be genuinely replayable.

- **Importance/Highlight:** Arena combat games often feel random to new players. By exposing the underlying match data — accuracy, positioning heatmaps, damage-per-weapon, HP curves — RoboBash turns every match into a feedback loop. Players can see exactly which build choices paid off and iterate on them.

### 2.2 Objectives

- Deliver a complete, playable 2-player arena combat game with meaningful build choices.
- Implement a modular Object-Oriented Part system so adding new parts is trivial.
- Record all match-relevant data automatically during gameplay with no player input required.
- Provide a post-match dashboard with at least 6 distinct visualizations covering accuracy, positioning, damage, and build performance.
- Persist match history across sessions via CSV so long-term build comparisons are possible.

---

## 3. UML Class Diagram

The UML class diagram shows all classes, their key attributes and methods, and their relationships (inheritance and association).

**Submission Requirement:**
- The UML Class Diagram is attached as a separate file: [UML.pdf](./UML.pdf)

---

## 4. Object-Oriented Programming Implementation

The project is organized around the following classes:

- **Part (Base Class):** Abstract base for every equippable robot component. Holds shared attributes (`name`, `weight`, `sprite_image`, `data`) and defines the `apply_modifier(robot)` interface that subclasses override.

- **Chassis (inherits Part):** Determines the robot's maximum HP. Heavier chassis give more HP.

- **Motor (inherits Part):** Adds to the robot's speed modifier based on its power output.

- **Linkage (inherits Part):** Controls the robot's weight capacity and subtracts a speed penalty proportional to its weight (tracks, wheels, legs).

- **Gun (inherits Part):** Sets the robot's base damage, cooldown, and weapon name. Three weapons are supported: Machine Gun (spread fire), Light Gun, and Laser Cannon.

- **Controller (inherits Part):** CPU module that modifies damage and cooldown on top of the gun's base values (Standard / Sniper / Rapid).

- **Power (inherits Part):** Defines the robot's power capacity limit, which constrains which other parts can be equipped legally.

- **Projectile:** Represents a single in-flight bullet. Tracks its own position, velocity, damage, owner, weapon type, and timestamp. Handles its own wall, obstacle, and enemy collision checks.

- **Robot:** The main gameplay entity. Composed of six `Part` objects chosen from the loadout. Responsible for aggregating stats from all equipped parts, building directional sprites, handling movement with collision, and taking damage.

- **DataTracker:** The statistics engine. Logs every movement sample, shot fired, hit/miss result, and damage event during a match, and exports two CSVs (`movement_logs.csv` and `match_logs.csv`) after the match ends.

- **GameManager:** The top-level controller. Manages the current game state (`START`, `GARAGE`, `ARENA`), holds the player list, projectiles, obstacles, and the `DataTracker`. Responsible for initializing matches, generating the battle arena, and triggering the end-of-match transition.

---

## 5. Statistical Data

### 5.1 Data Recording Method

Data is collected in real time during each match by the `DataTracker` class, which exposes a single `log_event(event_type, data)` method that the main game loop calls whenever something statistically relevant happens:

- **Movement** samples are logged every 0.5 seconds with both players' X, Y coordinates and HP.
- **Shots fired** are logged the instant a projectile is spawned, capturing the weapon type and timestamp.
- **Shot results** (hit or miss) are logged the moment a projectile resolves against the enemy, a wall, or an obstacle.
- **Damage events** are logged on every successful hit, recording shooter, target, weapon, damage amount, and the target's remaining HP.

When the match ends, `DataTracker.export_to_csv()` writes the data to two persistent CSV files:
- `movement_logs.csv` — per-sample positional and HP data for every match.
- `match_logs.csv` — one summary row per player per match (loadout, total weight, total damage dealt, shots fired, hits).

Because both files are appended rather than overwritten, match history accumulates across play sessions and feeds the dashboard's long-term scatter plot.

### 5.2 Data Features

The recorded data supports six distinct analyses:

- **Accuracy Ratio** — hit/miss counts per player (pie chart).
- **HP Reduction Over Time** — HP timeline per player (line graph).
- **Map Control Heatmap** — density of positions visited across the arena (2D histogram).
- **Damage by Weapon Type** — total damage aggregated per weapon (bar chart).
- **Weight vs. Damage (All Matches)** — historical comparison pulled from `match_logs.csv` (scatter plot).
- **Shooting Frequency** — mean and median intervals between shots per weapon, computed with the `statistics` module (table).

---

## 7. External Sources

### Libraries / Frameworks
- **Pygame** — game rendering, input, and audio. [https://www.pygame.org](https://www.pygame.org) — LGPL.
- **Matplotlib** — statistics dashboard plots. [https://matplotlib.org](https://matplotlib.org) — Matplotlib License (BSD-style).
- **Tkinter** — dashboard window. Python standard library.

### Fonts
- **Determination** — main UI font. Lucca Cedro [https://www.dafont.com/determination.font]
- **Dogica Pixel** — small UI font. Roberto Mocci [https://www.dafont.com/dogica.font]

### Audio
- Background music and SFX located in `asset/`
- **Burn the Map** — Background music for battle arena. AlexGrohl [https://artlist.io/royalty-free-music/song/burn-the-map/6000740]
- **Iron bang** — Sound effect for changing parts in garage. masp005 [https://pixabay.com/id/sound-effects/film-efek-khusus-iron-bang-119810/]
- **Gun fire** — Sound effect for Machine Gun shooting. Foisal72 [https://pixabay.com/sound-effects/film-special-effects-gun-fire-346766/]
- **Gunshot** — Sound effect for Light Gun shooting. Universfield [https://pixabay.com/sound-effects/film-special-effects-gunshot-352466/]
- **Laser Gun** — Sound effect for Laser Canon shooting. VoiceBosch [https://pixabay.com/sound-effects/film-special-effects-laser-gun-174976/]

### Art
- Robot part sprites, obstacles, and backgrounds located in `asset/` created by myself (designed by me, drafted by Gemini, and edited via Procreate).