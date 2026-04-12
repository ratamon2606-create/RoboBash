import pygame
import sys
import random
import time
import csv
import os
import statistics
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 986

real_screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RoboBash")


def load_sound_safe(filename):
    if not os.path.exists(filename):
        print(f"AUDIO WARNING: Cannot find file -> '{filename}'")
        class DummySound:
            def play(self): pass
        return DummySound()
    try:
        return pygame.mixer.Sound(filename)
    except Exception as e:
        print(f"AUDIO ERROR: Failed to load '{filename}'. Pygame Sound objects often reject .mp3 files. Please convert to .wav or .ogg! Error details: {e}")
        class DummySound:
            def play(self): pass
        return DummySound()

bgm_file = "asset/burn the map.mp3"
iron_bang_snd = load_sound_safe("asset/iron bang.mp3")
gunfire_snd = load_sound_safe("asset/gunfire.mp3")
gunshot_snd = load_sound_safe("asset/gunshot.mp3")
laser_snd = load_sound_safe("asset/lasergun.mp3")


WHITE, YELLOW, BLUE, GREEN, DARK_GRAY, BLACK, RED = (255, 255, 255), (255, 204, 0), (51, 153, 255), (51, 204, 51), (40, 40, 40), (0, 0, 0), (255, 50, 50)
try:
    font = pygame.font.Font("asset/determination.ttf", 20)
    font_small = pygame.font.Font("asset/dogicapixel.ttf", 16)
    font_large = pygame.font.Font("asset/determination.ttf", 44) 
    font_title = pygame.font.Font("asset/determination.ttf", 120) 
except:
    font, font_small, font_large, font_title = [pygame.font.SysFont("arial", s, bold=True) for s in [20, 16, 44, 120]]

def load_image_safe(filename, default_size):
    if filename is None: return None
    try: return pygame.image.load(filename).convert_alpha()
    except:
        surf = pygame.Surface(default_size, pygame.SRCALPHA)
        surf.fill((255, 0, 0, 100)) 
        return surf

# ASSETS
try: bg_img = pygame.transform.scale(pygame.image.load("asset/bg.png").convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
except: bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); bg_img.fill((40, 40, 40))

try: battle_bg = pygame.transform.scale(pygame.image.load("asset/battle.png").convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT))
except: battle_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); battle_bg.fill((80, 60, 40))

tab_img = load_image_safe("asset/tab.png", (150, SCREEN_HEIGHT)) 
bar_img = load_image_safe("asset/bar.png", (250, 120)) 

obstacle_filenames = ["parcel.png", "barrel.png", "wire.png", "tool.png", "barrier1.png", "barrier2.png", "side_barrier.png"]
obstacle_images = [img.subsurface(img.get_bounding_rect()).copy() for fname in obstacle_filenames if (img := load_image_safe(f"asset/{fname}", (80, 80))) and img.get_bounding_rect().width > 0]

CATEGORIES = ["controller", "linkage", "gun", "motor", "power", "chassis"]
PARTS_DATA = {
    "controller": [
        {"name": "Standard CPU", "img": None, "dps": 10, "weight": 2, "power": 5, "desc": "STANDARD CPU\n\n\nPROS: Low energy\n\nCONS: None"},
        {"name": "Sniper CPU", "img": None, "dps": 40, "weight": 5, "power": 15, "desc": "SNIPER CPU\n\n\nPROS: +Accuracy\n\nCONS: -Fire Rate"},
        {"name": "Rapid CPU", "img": None, "dps": 50, "weight": 8, "power": 25, "desc": "RAPID CPU\n\n\nPROS: +Fire Rate\n\nCONS: -Accuracy"}
    ],
    "linkage": [
        {"name": "Tank Tracks", "img": ("asset/back_tank.png", "asset/front_tank.png"), "arena_imgs": {"up": "asset/tankwheel_front.png", "down": "asset/tankwheel_front.png", "left": "asset/tankwheel_left.png", "right": "asset/tankwheel_right.png"}, "dps": 0, "weight": 40, "power": 10, "weight_cap": 250, "desc": "TANK TRACKS\n\n\nPROS: +Weight Cap\n\nCONS: Slow"},
        {"name": "Wheels", "img": ("asset/back_wheel.png", "asset/font_wheel.png"), "arena_imgs": {"up": "asset/wheel_front.png", "down": "asset/wheel_front.png", "left": "asset/wheel_side.png", "right": "asset/wheel_side.png"}, "dps": 0, "weight": 20, "power": 20, "weight_cap": 150, "desc": "WHEELS\n\n\nPROS: +Speed\n\nCONS: -Weight Cap"},
        {"name": "Legs", "img": ("asset/legs.png", None), "arena_imgs": {"up": "asset/legswheel.png", "down": "asset/legswheel.png", "left": "asset/legswheel.png", "right": "asset/legswheel.png"}, "dps": 0, "weight": 15, "power": 15, "weight_cap": 100, "desc": "LEGS\n\n\nPROS: +Agility\n\nCONS: Lowest Cap"}
    ],
    "gun": [
        {"name": "Machine Gun", "img": "asset/machine.png", "arena_imgs": {"up": "asset/machine_back.png", "down": "asset/machine_front.png", "left": "asset/machine_left.png", "right": "asset/machine_right.png"}, "dps": 80, "weight": 25, "power": 20, "base_dmg": 8, "base_cd": 15, "desc": "MACHINE GUN\n\n\nPROS: Balanced\n\nCONS: Moderate dmg"},
        {"name": "Light Gun", "img": "asset/light.png", "arena_imgs": {"up": "asset/light_back.png", "down": "asset/light_front.png", "left": "asset/light_left.png", "right": "asset/light_right.png"}, "dps": 40, "weight": 10, "power": 10, "base_dmg": 4, "base_cd": 8, "desc": "LIGHT GUN\n\n\nPROS: Lightweight\n\nCONS: -DPS"},
        {"name": "Laser Cannon", "img": "asset/lazer.png", "arena_imgs": {"up": "asset/lazer_back.png", "down": "asset/lazer_front.png", "left": "asset/lazer_left.png", "right": "asset/lazer_right.png"}, "dps": 150, "weight": 60, "power": 50, "base_dmg": 35, "base_cd": 40, "desc": "LASER CANNON\n\n\nPROS: +DPS\n\nCONS: Heavy drain"}
    ],
    "motor": [
        {"name": "Basic Motor", "img": None, "dps": 0, "weight": 10, "power": 10, "desc": "BASIC MOTOR\n\n\nPROS: Light\n\nCONS: Average speed"},
        {"name": "V8 Engine", "img": None, "dps": 0, "weight": 25, "power": 30, "desc": "V8 ENGINE\n\n\nPROS: +Torque\n\nCONS: Heavy"},
        {"name": "Mag-Lev", "img": None, "dps": 0, "weight": 15, "power": 40, "desc": "MAG-LEV\n\n\nPROS: +Max Speed\n\nCONS: -Acceleration"}
    ],
    "power": [
        {"name": "Lead-Acid", "img": None, "dps": 0, "weight": 10, "power": 0, "power_cap": 80, "desc": "LEAD-ACID\n\n\nPROS: Standard\n\nCONS: Low cap"},
        {"name": "Li-Ion", "img": None, "dps": 0, "weight": 5, "power": 0, "power_cap": 130, "desc": "LI-ION\n\n\nPROS: High cap\n\nCONS: Fragile"},
        {"name": "Nuclear Core", "img": None, "dps": 0, "weight": 35, "power": 0, "power_cap": 200, "desc": "NUCLEAR CORE\n\n\nPROS: Massive power\n\nCONS: Extremely heavy"}
    ],
    "chassis": [
        {"name": "Heavy Armor", "img": "asset/tank.png", "arena_imgs": {"up": "asset/tank_back.png", "down": "asset/tank_front.png", "left": "asset/tank_left.png", "right": "asset/tank_right.png"}, "dps": 0, "weight": 50, "power": 0, "desc": "HEAVY ARMOR\n\n\nPROS: +HP\n\nCONS: Heavy"},
        {"name": "Steel Frame", "img": "asset/steel.png", "arena_imgs": {"up": "asset/steel_back.png", "down": "asset/steel_front.png", "left": "asset/steel_left.png", "right": "asset/steel_right.png"}, "dps": 0, "weight": 25, "power": 0, "desc": "STEEL FRAME\n\n\nPROS: Balanced\n\nCONS: None"},
        {"name": "Aero Body", "img": "asset/wings.png", "arena_imgs": {"up": "asset/wings_back.png", "down": "asset/wings_front.png", "left": "asset/wings_left.png", "right": "asset/wings_right.png"}, "dps": 0, "weight": 10, "power": 5, "desc": "AERO BODY\n\n\nPROS: Light\n\nCONS: Fragile"}
    ]
}


class Part:
    def __init__(self, data_dict):
        self.name = data_dict["name"]
        self.weight = data_dict["weight"]
        self.sprite_image = data_dict.get("img")
        self.data = data_dict
    def apply_modifier(self, robot): pass

class Chassis(Part):
    def apply_modifier(self, robot):
        robot.max_hp = 100 + (self.weight * 8)
        robot.current_hp = robot.max_hp

class Motor(Part):
    def apply_modifier(self, robot):
        robot.speed_modifier += (self.data["power"] / 10)

class Linkage(Part):
    def apply_modifier(self, robot):
        robot.speed_modifier -= (self.weight / 20)
        robot.max_weight_cap = self.data["weight_cap"]

class Gun(Part):
    def apply_modifier(self, robot):
        robot.base_dmg = self.data["base_dmg"]
        robot.cooldown_max = self.data["base_cd"]
        robot.weapon_name = self.name

class Controller(Part):
    def apply_modifier(self, robot):
        if self.name == "Sniper CPU":
            robot.cooldown_max += 15
            robot.base_dmg += 15
        elif self.name == "Rapid CPU":
            robot.cooldown_max = max(4, robot.cooldown_max - 5)
            robot.base_dmg = max(1, robot.base_dmg - 2)

class Power(Part):
    def apply_modifier(self, robot):
        robot.power_cap = self.data["power_cap"]

class Projectile:
    def __init__(self, x, y, vel_x, vel_y, damage_value, owner, weapon_name, timestamp):
        self.damage_value = damage_value
        self.velocity = [vel_x, vel_y]
        self.hitbox_rect = pygame.Rect(x, y, 10, 10)
        self.owner = owner
        self.weapon_name = weapon_name
        self.timestamp = timestamp

    def update_position(self):
        self.hitbox_rect.x += self.velocity[0]
        self.hitbox_rect.y += self.velocity[1]

    def check_collision(self, obstacles, enemy_robot):
        if self.hitbox_rect.left < 40 or self.hitbox_rect.right > SCREEN_WIDTH-40 or \
           self.hitbox_rect.top < 110 or self.hitbox_rect.bottom > SCREEN_HEIGHT-40:
            return False 
            
        for obs in obstacles:
            if self.hitbox_rect.colliderect(obs["rect"]): return False
                
        if enemy_robot.current_hp > 0 and self.hitbox_rect.colliderect(enemy_robot.hitbox_rect):
            return True 
            
        return None

class Robot:
    def __init__(self, loadout_indices, x, y, color, player_id):
        self.player_id = player_id
        self.loadout_indices = loadout_indices
        self.current_hp = 100
        self.max_hp = 100
        self.total_weight = 0
        self.position_x = float(x)
        self.position_y = float(y)
        self.hitbox_rect = pygame.Rect(x, y, 100, 100)
        self.color = color
        
        self.equipped_parts = []
        self.speed_modifier = 4.0
        self.base_dmg = 0
        self.cooldown_max = 20
        self.current_cooldown = 0
        self.facing = (1 if x < SCREEN_WIDTH//2 else -1, 0)
        self.current_dir = "right" if x < SCREEN_WIDTH//2 else "left"
        self.weapon_name = "Unknown"
        self.images = self._create_sprites()
        
        self._instantiate_parts(loadout_indices)
        self.calculate_aggregate_stats()

    def _instantiate_parts(self, indices):
        self.equipped_parts.append(Controller(PARTS_DATA["controller"][indices["controller"]]))
        self.equipped_parts.append(Linkage(PARTS_DATA["linkage"][indices["linkage"]]))
        self.equipped_parts.append(Gun(PARTS_DATA["gun"][indices["gun"]]))
        self.equipped_parts.append(Motor(PARTS_DATA["motor"][indices["motor"]]))
        self.equipped_parts.append(Power(PARTS_DATA["power"][indices["power"]]))
        self.equipped_parts.append(Chassis(PARTS_DATA["chassis"][indices["chassis"]]))

    def calculate_aggregate_stats(self):
        self.total_weight = sum(p.weight for p in self.equipped_parts)
        for part in self.equipped_parts: part.apply_modifier(self)
        self.speed = max(2.0, min(self.speed_modifier, 9.0))

    def move(self, dx, dy, obstacles, enemy):
        self.position_x += dx
        self.hitbox_rect.x = int(self.position_x)
        if self.hitbox_rect.left < 40 or self.hitbox_rect.right > SCREEN_WIDTH - 40 or \
           any(self.hitbox_rect.colliderect(o["rect"]) for o in obstacles) or \
           (enemy.current_hp > 0 and self.hitbox_rect.colliderect(enemy.hitbox_rect)):
            self.position_x -= dx
            self.hitbox_rect.x = int(self.position_x)
            
        self.position_y += dy
        self.hitbox_rect.y = int(self.position_y)
        if self.hitbox_rect.top < 110 or self.hitbox_rect.bottom > SCREEN_HEIGHT - 40 or \
           any(self.hitbox_rect.colliderect(o["rect"]) for o in obstacles) or \
           (enemy.current_hp > 0 and self.hitbox_rect.colliderect(enemy.hitbox_rect)):
            self.position_y -= dy
            self.hitbox_rect.y = int(self.position_y)

    def take_damage(self, amount):
        self.current_hp -= amount

    def _create_sprites(self):
        sprites = {}
        for d in ["up", "down", "left", "right"]:
            raw_surf = pygame.Surface((300, 300), pygame.SRCALPHA)
            for cat in ["linkage", "chassis", "gun"]:
                pd = PARTS_DATA[cat][self.loadout_indices[cat]]
                paths = pd.get("arena_imgs", {}).get(d) or pd.get("img")
                if not paths: continue
                for path in ([paths] if isinstance(paths, str) else paths):
                    if path and (img := load_image_safe(path, (300, 300))):
                        raw_surf.blit(pygame.transform.scale(img, (300, 300)), (0, 0))
            mask = pygame.mask.from_surface(raw_surf, 10)
            bbox_list = mask.get_bounding_rects()
            if bbox_list: sprites[d] = pygame.transform.scale(raw_surf.subsurface(bbox_list[0].unionall(bbox_list[1:])), (100, 100))
            else: sprites[d] = pygame.transform.scale(raw_surf, (100, 100))
        return sprites

class DataTracker:
    def __init__(self):
        self.current_match_id = str(int(time.time()))
        self.match_log = {
            "movement": [], "damage": [], "shots_fired": [], "shots_hit_miss": [],
            "hp_timeline": {"p1": {"time": [], "hp": []}, "p2": {"time": [], "hp": []}},
            "parts": {"p1_weight": 0, "p2_weight": 0, "p1_dmg_dealt": 0, "p2_dmg_dealt": 0}
        }
        self.start_time = 0
        self.cumulative_time = 0

    def get_current_time(self):
        return self.cumulative_time + (pygame.time.get_ticks() - self.start_time) / 1000.0

    def log_event(self, event_type, data):
        t = self.get_current_time()
        if event_type == "movement":
            self.match_log["movement"].append([t, data["p1_x"], data["p1_y"], data["p2_x"], data["p2_y"]])
        elif event_type == "fire":
            self.match_log["shots_fired"].append({"time": t, "weapon": data["weapon"]})
        elif event_type == "shot_result":
            self.match_log["shots_hit_miss"].append({"shooter": data["shooter"], "hit": data["hit"]})
        elif event_type == "damage":
            self.match_log["damage"].append({"time": t, "shooter": data["shooter"], "weapon": data["weapon"], "dmg": data["dmg"]})
            self.match_log["hp_timeline"][data["target"]]["time"].append(t)
            self.match_log["hp_timeline"][data["target"]]["hp"].append(data["new_hp"])
            if data["shooter"] == "p1": self.match_log["parts"]["p1_dmg_dealt"] += data["dmg"]
            elif data["shooter"] == "p2": self.match_log["parts"]["p2_dmg_dealt"] += data["dmg"]

    def export_to_csv(self):
        m_file = "movement_logs.csv"
        m_exists = os.path.exists(m_file)
        try:
            with open(m_file, "a", newline="") as f:
                writer = csv.writer(f)
                if not m_exists: writer.writerow(["Match_ID", "Time(s)", "P1_X", "P1_Y", "P2_X", "P2_Y"])
                for row in self.match_log["movement"]:
                    writer.writerow([self.current_match_id] + list(row))
        except: pass

        ml_file = "match_logs.csv"
        ml_exists = os.path.exists(ml_file)
        try:
            with open(ml_file, "a", newline="") as f:
                writer = csv.writer(f)
                if not ml_exists: writer.writerow(["Match_ID", "Player", "Total_Weight", "Total_Damage"])
                writer.writerow([self.current_match_id, "P1", self.match_log["parts"]["p1_weight"], self.match_log["parts"]["p1_dmg_dealt"]])
                writer.writerow([self.current_match_id, "P2", self.match_log["parts"]["p2_weight"], self.match_log["parts"]["p2_dmg_dealt"]])
        except: pass

class GameManager:
    def __init__(self):
        self.current_state = "START"
        self.player_list = []
        self.tracker = DataTracker()
        self.obstacles = []
        self.projectiles = []
        self.game_over_timer = 0
        self.show_end_menu = False
        self.winner_text = ""
        self.current_building_player = 1
        self.p1_loadout = None
        self.current_parts = {cat: 0 for cat in CATEGORIES}
        self.selected_tab_index = 0
        self.is_overweight = False
        self.is_overpower = False

    def switch_state(self, new_state):
        self.current_state = new_state

    def initialize_match(self, p1_loadout, p2_loadout):
        self.player_list = [
            Robot(p1_loadout, 100, SCREEN_HEIGHT//2 - 50, BLUE, "p1"),
            Robot(p2_loadout, 824, SCREEN_HEIGHT//2 - 50, GREEN, "p2")
        ]
        self.projectiles.clear()
        self.game_over_timer = 0
        self.show_end_menu = False
        self._generate_battle_arena()
        
        self.tracker.start_time = pygame.time.get_ticks()
        
        self.tracker.match_log["hp_timeline"]["p1"]["hp"].append(self.player_list[0].max_hp)
        self.tracker.match_log["hp_timeline"]["p1"]["time"].append(self.tracker.cumulative_time)
        self.tracker.match_log["hp_timeline"]["p2"]["hp"].append(self.player_list[1].max_hp)
        self.tracker.match_log["hp_timeline"]["p2"]["time"].append(self.tracker.cumulative_time)
        
        self.tracker.match_log["parts"]["p1_weight"] = self.player_list[0].total_weight
        self.tracker.match_log["parts"]["p2_weight"] = self.player_list[1].total_weight

    def _generate_battle_arena(self):
        self.obstacles.clear()
        
        block_bl = pygame.Rect(0, SCREEN_HEIGHT - 280, 260, 280)
        block_br = pygame.Rect(SCREEN_WIDTH - 320, SCREEN_HEIGHT - 150, 320, 150)
        
        self.obstacles.append({"img": None, "rect": block_bl})
        self.obstacles.append({"img": None, "rect": block_br})
        
        p1_safe_zone = pygame.Rect(0, SCREEN_HEIGHT//2 - 150, 280, 300)
        p2_safe_zone = pygame.Rect(SCREEN_WIDTH - 280, SCREEN_HEIGHT//2 - 150, 280, 300)
        
        for _ in range(random.randint(5, 9)):
            if not obstacle_images: break
            obs_img = random.choice(obstacle_images)
            img_w, img_h = obs_img.get_size()
            valid, attempts = False, 0
            
            while not valid and attempts < 100:
                rect = pygame.Rect(random.randint(80, SCREEN_WIDTH - 80 - img_w), 
                                   random.randint(150, SCREEN_HEIGHT - 80 - img_h), img_w, img_h)
                padded = rect.inflate(110, 110)
                if not (padded.colliderect(self.player_list[0].hitbox_rect) or padded.colliderect(self.player_list[1].hitbox_rect) or \
                        rect.colliderect(p1_safe_zone) or rect.colliderect(p2_safe_zone) or \
                        any(padded.colliderect(o["rect"]) for o in self.obstacles)):
                    valid = True
                    self.obstacles.append({"img": obs_img, "rect": rect})
                attempts += 1

    def end_game(self):
        self.tracker.cumulative_time += (pygame.time.get_ticks() - self.tracker.start_time) / 1000.0
        self.show_end_menu = True

manager = GameManager()

# UI Setup
tab_rects = [pygame.Rect(24, 122 + (i * 140), 121, 129) for i in range(len(CATEGORIES))]
arrow_left_rect, arrow_right_rect = pygame.Rect(300, 550, 40, 40), pygame.Rect(880, 550, 40, 40)
next_btn_rect = pygame.Rect(850, 913, 140, 50) 
main_start_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 350, 300, 80)
rematch_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 20, 160, 60)
exit_btn_rect = pygame.Rect(SCREEN_WIDTH // 2 + 20, SCREEN_HEIGHT // 2 + 20, 160, 60)

def draw_arrows():
    pygame.draw.polygon(screen, YELLOW, [(340, 550), (340, 590), (300, 570)])
    pygame.draw.polygon(screen, YELLOW, [(880, 550), (880, 590), (920, 570)])

def draw_stats():
    screen.blit(bar_img, (0, 0))
    t_dps, t_weight, t_power = 0, 0, 0
    for cat in CATEGORIES:
        pd = PARTS_DATA[cat][manager.current_parts[cat]]
        t_dps += pd["dps"]; t_weight += pd["weight"]
        if cat != "power": t_power += pd["power"]
        
    max_w = PARTS_DATA["linkage"][manager.current_parts["linkage"]]["weight_cap"]
    max_p = PARTS_DATA["power"][manager.current_parts["power"]]["power_cap"]
    
    manager.is_overweight, manager.is_overpower = t_weight > max_w, t_power > max_p
    
    start_x, block_w, block_h, gap = 726, 10, 18, 4
    for i in range(int(min(t_dps / 300.0, 1.0) * 10)): pygame.draw.rect(screen, YELLOW, (start_x + (i * (block_w + gap)), 191, block_w, block_h))
    for i in range(int(min(t_weight / max_w, 1.0) * 10)): pygame.draw.rect(screen, RED if manager.is_overweight else BLUE, (start_x + (i * (block_w + gap)), 256, block_w, block_h))
    for i in range(int(min(t_power / max_p, 1.0) * 10)): pygame.draw.rect(screen, RED if manager.is_overpower else GREEN, (start_x + (i * (block_w + gap)), 321, block_w, block_h))

    screen.blit(font.render(str(t_dps), True, YELLOW), (902, 187))
    screen.blit(font.render(f"{t_weight}/{max_w}kg", True, RED if manager.is_overweight else BLUE), (902, 254))
    screen.blit(font.render(f"{t_power}/{max_p}W", True, RED if manager.is_overpower else GREEN), (902, 319))

def draw_part_description():
    desc = PARTS_DATA[CATEGORIES[manager.selected_tab_index]][manager.current_parts[CATEGORIES[manager.selected_tab_index]]]["desc"].replace('\\n', '\n')
    lines = [font_small.render(l, True, WHITE) for l in desc.split('\n')]
    bg_rect = pygame.Rect(0, 0, max([s.get_width() for s in lines]) + 40, (font_small.get_linesize() * len(lines)) + 30)
    bg_rect.center = (SCREEN_WIDTH // 2 + 85, SCREEN_HEIGHT - 155)
    pygame.draw.rect(screen, BLACK, bg_rect); pygame.draw.rect(screen, YELLOW, bg_rect, 2)
    
    y = bg_rect.top + 15
    for s in lines: screen.blit(s, s.get_rect(centerx=bg_rect.centerx, top=y)); y += font_small.get_linesize()
    ctrl = font_large.render("WASD / SPACE BAR" if manager.current_building_player == 1 else "ARROW KEYS / ENTER", True, "white")
    screen.blit(ctrl, ctrl.get_rect(centerx=bg_rect.centerx-30, top=bg_rect.bottom + 35))

# DASHBOARD
def show_statistics_dashboard():
    manager.tracker.export_to_csv()
    
    plt.style.use('dark_background')
    ui_bg, panel_bg, highlight, p1_color, p2_color = "#1e222e", "#2a303c", "#fadb26", "#3399FF", "#33CC33"
    
    font_path = "asset/determination.ttf"
    if os.path.exists(font_path): 
        pixel_font = fm.FontProperties(fname=font_path)
        title_font = fm.FontProperties(fname=font_path, size=28)
    else: 
        pixel_font = fm.FontProperties(family='monospace')
        title_font = fm.FontProperties(family='monospace', size=28)
        
    root = tk.Tk()
    root.title("Match Analytics Dashboard")
    root.geometry("1400x800")
    root.configure(bg=ui_bg)
    
    border_frame = tk.Frame(root, bg=highlight, bd=0)
    border_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    inner_frame = tk.Frame(border_frame, bg=ui_bg, bd=0)
    inner_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
    
    fig, axs = plt.subplots(2, 3, figsize=(14, 7))
    fig.patch.set_facecolor(ui_bg)
    
    fig.suptitle("MATCH ANALYTICS REPORT", color=p1_color, fontproperties=title_font)
    fig.tight_layout(pad=4.0, rect=[0, 0, 1, 0.94])

    for ax in axs.flat:
        ax.set_facecolor(panel_bg)
        ax.tick_params(colors="white", length=0, labelsize=8)
        for label in ax.get_xticklabels() + ax.get_yticklabels(): label.set_fontproperties(pixel_font)
        for spine in ax.spines.values(): spine.set_color(highlight); spine.set_linewidth(2)
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]): 
            item.set_color(highlight); item.set_fontproperties(pixel_font)

    # PIE CHART
    axs[0, 0].set_title("ACCURACY RATIO", fontproperties=pixel_font)
    p1_hits = sum(1 for s in manager.tracker.match_log["shots_hit_miss"] if s["shooter"] == "p1" and s["hit"])
    p1_miss = sum(1 for s in manager.tracker.match_log["shots_hit_miss"] if s["shooter"] == "p1" and not s["hit"])
    p2_hits = sum(1 for s in manager.tracker.match_log["shots_hit_miss"] if s["shooter"] == "p2" and s["hit"])
    p2_miss = sum(1 for s in manager.tracker.match_log["shots_hit_miss"] if s["shooter"] == "p2" and not s["hit"])
    if (p1_hits + p1_miss + p2_hits + p2_miss) > 0:
        _, texts, autotexts = axs[0, 0].pie(
            [p1_hits, p1_miss, p2_hits, p2_miss], labels=['P1 Hit', 'P1 Miss', 'P2 Hit', 'P2 Miss'], 
            colors=[p1_color, '#1a4c80', p2_color, '#1a661a'], autopct='%1.1f%%', 
            wedgeprops={'edgecolor': ui_bg, 'linewidth': 3}, textprops={'color': "white"}
        )
        for t in texts + autotexts: t.set_fontproperties(pixel_font)
    else: axs[0, 0].text(0.5, 0.5, "NO SHOTS", ha='center', va='center', color=highlight, fontproperties=pixel_font)

    # LINE GRAPH
    axs[0, 1].set_title("HP REDUCTION OVER TIME", fontproperties=pixel_font)
    axs[0, 1].plot(manager.tracker.match_log["hp_timeline"]["p1"]["time"], manager.tracker.match_log["hp_timeline"]["p1"]["hp"], label="P1 HP", color=p1_color, linewidth=3)
    axs[0, 1].plot(manager.tracker.match_log["hp_timeline"]["p2"]["time"], manager.tracker.match_log["hp_timeline"]["p2"]["hp"], label="P2 HP", color=p2_color, linewidth=3)
    axs[0, 1].set_xlabel("Time (s)", fontproperties=pixel_font)
    legend = axs[0, 1].legend(prop=pixel_font); legend.get_frame().set_edgecolor(highlight)

    # HEATMAP
    axs[0, 2].set_title("MAP CONTROL (HEATMAP)", fontproperties=pixel_font)
    x_coords = [m[1] for m in manager.tracker.match_log["movement"]] + [m[3] for m in manager.tracker.match_log["movement"]]
    y_coords = [m[2] for m in manager.tracker.match_log["movement"]] + [m[4] for m in manager.tracker.match_log["movement"]]
    if x_coords: axs[0, 2].hist2d(x_coords, y_coords, bins=20, cmap='plasma', range=[[0, SCREEN_WIDTH], [0, SCREEN_HEIGHT]])
    axs[0, 2].invert_yaxis()

    # BAR CHART
    axs[1, 0].set_title("DAMAGE BY WEAPON TYPE", fontproperties=pixel_font)
    weapon_dmg = {}
    for d in manager.tracker.match_log["damage"]: weapon_dmg[d["weapon"]] = weapon_dmg.get(d["weapon"], 0) + d["dmg"]
    if weapon_dmg:
        keys, values = list(weapon_dmg.keys()), list(weapon_dmg.values())
        bars = axs[1, 0].bar(keys, values, color=highlight, edgecolor=ui_bg, linewidth=4)
        axs[1, 0].set_xticks(range(len(keys))); axs[1, 0].set_xticklabels(keys, fontproperties=pixel_font)
        for bar in bars: axs[1, 0].text(bar.get_x() + bar.get_width()/2, bar.get_height()*1.02, str(int(bar.get_height())), ha='center', color=highlight, fontproperties=pixel_font)

    # SCATTER PLOT
    axs[1, 1].set_title("WEIGHT VS DAMAGE (ALL MATCHES)", fontproperties=pixel_font)
    all_weights, all_dmgs = [], []
    try:
        with open("match_logs.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_weights.append(float(row["Total_Weight"]))
                all_dmgs.append(float(row["Total_Damage"]))
    except: pass
    if all_weights:
        axs[1, 1].scatter(all_weights, all_dmgs, color=p1_color, alpha=0.8, edgecolor=ui_bg, s=100)
        axs[1, 1].set_xlabel("Total Weight", fontproperties=pixel_font)
        axs[1, 1].set_ylabel("Total Damage Dealt", fontproperties=pixel_font)
    else: axs[1, 1].text(0.5, 0.5, "NO DATA YET", ha='center', va='center', color=highlight, fontproperties=pixel_font)

    # STATISTICS TABLE
    axs[1, 2].axis('tight'); axs[1, 2].axis('off')
    axs[1, 2].set_title("SHOOTING FREQUENCY", fontproperties=pixel_font, pad=20)
    
    fire_data = {}
    for s in manager.tracker.match_log["shots_fired"]:
        w = s["weapon"]
        if w not in fire_data: fire_data[w] = []
        fire_data[w].append(s["time"])
        
    table_data = []
    for w, times in fire_data.items():
        total = len(times)
        intervals = [times[i] - times[i-1] for i in range(1, total)]
        mean_val = round(statistics.mean(intervals), 2) if intervals else 0.0
        med_val = round(statistics.median(intervals), 2) if intervals else 0.0
        table_data.append([w, total, mean_val, med_val])
        
    if not table_data: table_data = [["None", 0, 0, 0]]
    
    cols = ["Weapon", "Total", "Mean\nInterval", "Median\nInterval"]
    tbl = axs[1, 2].table(cellText=table_data, colLabels=cols, loc='center', cellLoc='center')
    tbl.scale(1, 3.0) 
    tbl.auto_set_font_size(False); tbl.set_fontsize(11)
    for (r, c), cell in tbl.get_celld().items():
        cell.set_text_props(fontproperties=pixel_font, color="white")
        cell.set_facecolor(panel_bg); cell.set_edgecolor(highlight)

    canvas = FigureCanvasTkAgg(fig, master=inner_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    tk.Button(inner_frame, text="EXIT DASHBOARD", font=("Determination", 14), command=lambda: [plt.close('all'), root.quit(), root.destroy()], 
              bg="#ff4d4d", fg="white", relief="flat", padx=20, pady=5).pack(pady=10)
    root.mainloop()

# MAIN
clock = pygame.time.Clock()
running, run_dashboard, last_log_time = True, False, 0

while running:
    cw, ch = real_screen.get_size()
    aspect_ratio = SCREEN_WIDTH / SCREEN_HEIGHT
    win_aspect = cw / ch
    if win_aspect > aspect_ratio:
        scale_h = ch
        scale_w = int(scale_h * aspect_ratio)
        off_x = (cw - scale_w) // 2
        off_y = 0
    else:
        scale_w = cw
        scale_h = int(scale_w / aspect_ratio)
        off_x = 0
        off_y = (ch - scale_h) // 2

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            logic_x = int((mx - off_x) * (SCREEN_WIDTH / scale_w)) if scale_w > 0 else 0
            logic_y = int((my - off_y) * (SCREEN_HEIGHT / scale_h)) if scale_h > 0 else 0
            pos = (logic_x, logic_y)
            
            if manager.current_state == "START" and main_start_btn_rect.collidepoint(pos):
                manager.switch_state("GARAGE")
            elif manager.current_state == "GARAGE":
                for i, r in enumerate(tab_rects):
                    if r.collidepoint(pos): manager.selected_tab_index = i
                cat = CATEGORIES[manager.selected_tab_index]
                if arrow_left_rect.collidepoint(pos): 
                    manager.current_parts[cat] = (manager.current_parts[cat] - 1) % 3
                    iron_bang_snd.play()
                if arrow_right_rect.collidepoint(pos): 
                    manager.current_parts[cat] = (manager.current_parts[cat] + 1) % 3
                    iron_bang_snd.play()
                
                if next_btn_rect.collidepoint(pos) and not manager.is_overweight and not manager.is_overpower:
                    if manager.current_building_player == 1:
                        manager.p1_loadout = manager.current_parts.copy()
                        manager.current_building_player, manager.current_parts = 2, {c: 0 for c in CATEGORIES}
                    else:
                        manager.initialize_match(manager.p1_loadout, manager.current_parts.copy())
                        manager.switch_state("BATTLE")
                        
                        try:
                            if os.path.exists(bgm_file):
                                pygame.mixer.music.load(bgm_file)
                                pygame.mixer.music.set_volume(0.2)
                                pygame.mixer.music.play(-1)
                            else:
                                print(f"AUDIO WARNING: BGM '{bgm_file}' not found.")
                        except Exception as e:
                            print(f"AUDIO ERROR: BGM failed to load. {e}")

            elif manager.current_state == "BATTLE" and manager.show_end_menu:
                if rematch_btn_rect.collidepoint(pos): 
                    pygame.mixer.music.stop()
                    
                    saved_tracker = manager.tracker
                    manager.__init__() 
                    manager.tracker = saved_tracker
                    
                elif exit_btn_rect.collidepoint(pos): 
                    pygame.mixer.music.stop()
                    run_dashboard, running = True, False

    if manager.current_state == "START":
        screen.blit(bg_img, (0, 0))
        for offset, color in [((5, 5), BLACK), ((0, 0), YELLOW)]:
            surf = font_title.render("ROBOBASH", True, color)
            screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH//2 + offset[0], SCREEN_HEIGHT//3 + offset[1])))
        
        desc = [font_large.render(l, True, "white") for l in "2 players required\ndesign your robot and FIGHT!".split('\n')]
        bg_desc_rect = pygame.Rect(0, 0, max(s.get_width() for s in desc), font_large.get_linesize() * len(desc)).inflate(40, 20)
        bg_desc_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(screen, BLACK, bg_desc_rect); pygame.draw.rect(screen, YELLOW, bg_desc_rect, 2)
        y = bg_desc_rect.top + 10
        for s in desc: screen.blit(s, s.get_rect(centerx=bg_desc_rect.centerx, top=y)); y += font_large.get_linesize()
        
        pygame.draw.rect(screen, YELLOW, main_start_btn_rect); pygame.draw.rect(screen, WHITE, main_start_btn_rect, 4)
        btn_text = font_large.render("START GAME", True, BLACK)
        screen.blit(btn_text, btn_text.get_rect(center=main_start_btn_rect.center))

    elif manager.current_state == "GARAGE":
        screen.blit(bg_img, (75, 0)); screen.blit(tab_img, (0, 0))
        pygame.draw.rect(screen, YELLOW, tab_rects[manager.selected_tab_index], 2)
        
        cx, cy = 340, 365
        for part in [PARTS_DATA["linkage"][manager.current_parts["linkage"]]["img"][0], 
                     PARTS_DATA["chassis"][manager.current_parts["chassis"]]["img"], 
                     PARTS_DATA["gun"][manager.current_parts["gun"]]["img"], 
                     PARTS_DATA["linkage"][manager.current_parts["linkage"]]["img"][1]]:
            if part: screen.blit(load_image_safe(part, (300, 300)), (cx, cy))
            
        draw_arrows(); draw_stats(); draw_part_description()
        screen.blit(font_large.render(f"PLAYER {manager.current_building_player}", True, BLUE if manager.current_building_player==1 else GREEN), (31, 23))
        pygame.draw.rect(screen, YELLOW if not (manager.is_overweight or manager.is_overpower) else DARK_GRAY, next_btn_rect)
        pygame.draw.rect(screen, WHITE, next_btn_rect, 2)
        btn = font.render("NEXT" if manager.current_building_player == 1 else "FIGHT!", True, BLACK if not (manager.is_overweight or manager.is_overpower) else WHITE)
        screen.blit(btn, btn.get_rect(center=next_btn_rect.center))

    elif manager.current_state == "BATTLE":
        screen.blit(battle_bg, (0, 0))
        p1, p2 = manager.player_list[0], manager.player_list[1]
        
        if pygame.time.get_ticks() - last_log_time >= 1000 and manager.game_over_timer == 0:
            manager.tracker.log_event("movement", {"p1_x": p1.position_x, "p1_y": p1.position_y, "p2_x": p2.position_x, "p2_y": p2.position_y})
            last_log_time = pygame.time.get_ticks()

        if manager.game_over_timer == 0:
            keys = pygame.key.get_pressed()
            if p1.current_hp > 0:
                dx, dy = 0, 0
                if keys[pygame.K_w]: dy = -p1.speed; p1.facing, p1.current_dir = (0, -1), "up"
                if keys[pygame.K_s]: dy = p1.speed; p1.facing, p1.current_dir = (0, 1), "down"
                if keys[pygame.K_a]: dx = -p1.speed; p1.facing, p1.current_dir = (-1, 0), "left"
                if keys[pygame.K_d]: dx = p1.speed; p1.facing, p1.current_dir = (1, 0), "right"
                p1.move(dx, dy, manager.obstacles, p2)
                
                if keys[pygame.K_SPACE] and p1.current_cooldown <= 0:
                    base_vx, base_vy = p1.facing[0]*15, p1.facing[1]*15

                    if p1.weapon_name == "Machine Gun":
                        spread = 4 
                        velocities = [
                            (base_vx, base_vy),
                            (base_vx - p1.facing[1]*spread, base_vy + p1.facing[0]*spread),
                            (base_vx + p1.facing[1]*spread, base_vy - p1.facing[0]*spread)
                        ]
                        for vx, vy in velocities:
                            proj = Projectile(p1.hitbox_rect.centerx, p1.hitbox_rect.centery, vx, vy, p1.base_dmg, p1.player_id, p1.weapon_name, manager.tracker.get_current_time())
                            manager.projectiles.append(proj)
                        gunfire_snd.play()
                        
                    else:
                        proj = Projectile(p1.hitbox_rect.centerx, p1.hitbox_rect.centery, base_vx, base_vy, p1.base_dmg, p1.player_id, p1.weapon_name, manager.tracker.get_current_time())
                        manager.projectiles.append(proj)
                        if p1.weapon_name == "Light Gun": gunshot_snd.play()
                        elif p1.weapon_name == "Laser Cannon": laser_snd.play()
                        
                    manager.tracker.log_event("fire", {"weapon": p1.weapon_name})
                    p1.current_cooldown = p1.cooldown_max
                    
                if p1.current_cooldown > 0: p1.current_cooldown -= 1

            if p2.current_hp > 0:
                dx, dy = 0, 0
                if keys[pygame.K_UP]: dy = -p2.speed; p2.facing, p2.current_dir = (0, -1), "up"
                if keys[pygame.K_DOWN]: dy = p2.speed; p2.facing, p2.current_dir = (0, 1), "down"
                if keys[pygame.K_LEFT]: dx = -p2.speed; p2.facing, p2.current_dir = (-1, 0), "left"
                if keys[pygame.K_RIGHT]: dx = p2.speed; p2.facing, p2.current_dir = (1, 0), "right"
                p2.move(dx, dy, manager.obstacles, p1)
                
                if keys[pygame.K_RETURN] and p2.current_cooldown <= 0:
                    base_vx, base_vy = p2.facing[0]*15, p2.facing[1]*15
                    
                    if p2.weapon_name == "Machine Gun":
                        spread = 4 
                        velocities = [
                            (base_vx, base_vy),
                            (base_vx - p2.facing[1]*spread, base_vy + p2.facing[0]*spread),
                            (base_vx + p2.facing[1]*spread, base_vy - p2.facing[0]*spread)
                        ]
                        for vx, vy in velocities:
                            proj = Projectile(p2.hitbox_rect.centerx, p2.hitbox_rect.centery, vx, vy, p2.base_dmg, p2.player_id, p2.weapon_name, manager.tracker.get_current_time())
                            manager.projectiles.append(proj)
                        gunfire_snd.play()
                        
                    else:
                        proj = Projectile(p2.hitbox_rect.centerx, p2.hitbox_rect.centery, base_vx, base_vy, p2.base_dmg, p2.player_id, p2.weapon_name, manager.tracker.get_current_time())
                        manager.projectiles.append(proj)
                        if p2.weapon_name == "Light Gun": gunshot_snd.play()
                        elif p2.weapon_name == "Laser Cannon": laser_snd.play()
                        
                    manager.tracker.log_event("fire", {"weapon": p2.weapon_name})
                    p2.current_cooldown = p2.cooldown_max
                    
                if p2.current_cooldown > 0: p2.current_cooldown -= 1

        for proj in manager.projectiles[:]:
            proj.update_position()
            enemy = p2 if proj.owner == "p1" else p1
            col_result = proj.check_collision(manager.obstacles, enemy)
            
            if col_result == False:
                manager.tracker.log_event("shot_result", {"shooter": proj.owner, "hit": False})
                manager.projectiles.remove(proj)
            elif col_result == True:
                enemy.take_damage(proj.damage_value)
                manager.tracker.log_event("shot_result", {"shooter": proj.owner, "hit": True})
                manager.tracker.log_event("damage", {"shooter": proj.owner, "target": enemy.player_id, "weapon": proj.weapon_name, "dmg": proj.damage_value, "new_hp": max(0, enemy.current_hp)})
                manager.projectiles.remove(proj)
            else: pygame.draw.rect(screen, BLUE if proj.owner == "p1" else GREEN, proj.hitbox_rect)

        if (p1.current_hp <= 0 or p2.current_hp <= 0) and manager.game_over_timer == 0:
            manager.winner_text = "PLAYER 2" if p1.current_hp <= 0 else "PLAYER 1"
            manager.game_over_timer = pygame.time.get_ticks()
            pygame.mixer.stop()
            
        if manager.game_over_timer > 0 and pygame.time.get_ticks() - manager.game_over_timer > 2000 and not manager.show_end_menu:
            manager.end_game()

        for obs in manager.obstacles: 
            if obs.get("img"): 
                screen.blit(obs["img"], obs["rect"].topleft)

        for p, name in [(p1, "P1"), (p2, "P2")]:
            if p.current_hp > 0:
                if p.images and p.current_dir in p.images: screen.blit(p.images[p.current_dir], p.hitbox_rect.topleft)
                else: pygame.draw.rect(screen, p.color, p.hitbox_rect)
                text = font_small.render(name, True, WHITE)
                screen.blit(text, (p.hitbox_rect.centerx - text.get_width()//2, p.hitbox_rect.top - 30))
                pygame.draw.rect(screen, RED, (p.hitbox_rect.x, p.hitbox_rect.top - 12, 100, 8))
                pygame.draw.rect(screen, GREEN, (p.hitbox_rect.x, p.hitbox_rect.top - 12, int(100 * (p.current_hp / p.max_hp)), 8))
            else:
                text = font.render(f"{name} DESTROYED", True, RED)
                screen.blit(text, (p.hitbox_rect.centerx - text.get_width()//2, p.hitbox_rect.centery))

        if manager.show_end_menu:
            pygame.draw.rect(screen, DARK_GRAY, (SCREEN_WIDTH//2-250, SCREEN_HEIGHT//2-125, 500, 250))
            pygame.draw.rect(screen, YELLOW, (SCREEN_WIDTH//2-250, SCREEN_HEIGHT//2-125, 500, 250), 4)
            win_surf = font_large.render(f"{manager.winner_text} WINS", True, WHITE)
            screen.blit(win_surf, win_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2-50)))
            
            pygame.draw.rect(screen, BLUE, rematch_btn_rect); pygame.draw.rect(screen, WHITE, rematch_btn_rect, 2)
            rt = font.render("REMATCH", True, WHITE)
            screen.blit(rt, rt.get_rect(center=rematch_btn_rect.center))
            
            pygame.draw.rect(screen, RED, exit_btn_rect); pygame.draw.rect(screen, WHITE, exit_btn_rect, 2)
            et = font.render("EXIT", True, WHITE)
            screen.blit(et, et.get_rect(center=exit_btn_rect.center))


    real_screen.fill(BLACK)
    if scale_w > 0 and scale_h > 0:
        scaled_screen = pygame.transform.scale(screen, (scale_w, scale_h))
        real_screen.blit(scaled_screen, (off_x, off_y))
        
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
if run_dashboard: show_statistics_dashboard()
sys.exit()