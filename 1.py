import pygame
import sys
import random
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import csv
import os
import time


# เริ่มต้นการทำงานของ Pygame
pygame.init()

# ตั้งค่าหน้าจอ 1024 x 986
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 986
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RoboBash")

# กำหนดสี
WHITE = (255, 255, 255)
YELLOW = (255, 204, 0)
BLUE = (51, 153, 255)
GREEN = (51, 204, 51)
DARK_GRAY = (40, 40, 40)
BLACK = (0, 0, 0)
RED = (255, 50, 50) 
ORANGE = (255, 165, 0)

# ฟอนต์
try:
    font = pygame.font.Font("asset/determination.ttf", 20)
    font_small = pygame.font.Font("asset/dogicapixel.ttf", 16)
    font_large = pygame.font.Font("asset/determination.ttf", 44) 
except:
    font = pygame.font.SysFont("arial", 20, bold=True)
    font_small = pygame.font.SysFont("arial", 16, bold=True)
    font_large = pygame.font.SysFont("arial", 44, bold=True)

# ==========================================
# 1. โหลดภาพหลัก
# ==========================================
def load_image_safe(filename, default_size):
    if filename is None:
        return None
    try:
        return pygame.image.load(filename).convert_alpha()
    except:
        surf = pygame.Surface(default_size, pygame.SRCALPHA)
        surf.fill((255, 0, 0, 100)) 
        return surf

try:
    raw_bg = pygame.image.load("asset/bg.png").convert_alpha()
    bg_img = pygame.transform.scale(raw_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    bg_img.fill((40, 40, 40))

tab_img = load_image_safe("asset/tab.png", (150, SCREEN_HEIGHT)) 
bar_img = load_image_safe("asset/bar.png", (250, 120)) 

try:
    raw_battle_bg = pygame.image.load("asset/battle.png").convert_alpha()
    battle_bg = pygame.transform.scale(raw_battle_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    battle_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    battle_bg.fill((80, 60, 40))

obstacle_filenames = ["parcel.png", "barrel.png", "wire.png", "tool.png", "barrier1.png", "barrier2.png", "side_barrier.png"]
obstacle_images = []
for fname in obstacle_filenames:
    img = load_image_safe(f"asset/{fname}", (80, 80)) 
    if img:
        bbox = img.get_bounding_rect()
        if bbox.width > 0 and bbox.height > 0:
            img = img.subsurface(bbox).copy() 
            obstacle_images.append(img)

# ==========================================
# 2. Parts Database
# ==========================================
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
        {"name": "Machine Gun", "img": "asset/machine.png", "arena_imgs": {"up": "asset/machine_back.png", "down": "asset/machine_front.png", "left": "asset/machine_left.png", "right": "asset/machine_right.png"}, "dps": 80, "weight": 25, "power": 20, "desc": "MACHINE GUN\n\n\nPROS: Balanced\n\nCONS: Moderate dmg"},
        {"name": "Light Gun", "img": "asset/light.png", "arena_imgs": {"up": "asset/light_back.png", "down": "asset/light_front.png", "left": "asset/light_left.png", "right": "asset/light_right.png"}, "dps": 40, "weight": 10, "power": 10, "desc": "LIGHT GUN\n\n\nPROS: Lightweight\n\nCONS: -DPS"},
        {"name": "Laser Cannon", "img": "asset/lazer.png", "arena_imgs": {"up": "asset/lazer_back.png", "down": "asset/lazer_front.png", "left": "asset/lazer_left.png", "right": "asset/lazer_right.png"}, "dps": 150, "weight": 60, "power": 50, "desc": "LASER CANNON\n\n\nPROS: +DPS\n\nCONS: Heavy drain"}
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

# ==========================================
# Game State Variables
# ==========================================
game_state = "GARAGE" 
current_building_player = 1
player1_loadout = None
player2_loadout = None
current_parts = {cat: 0 for cat in CATEGORIES}
selected_tab_index = 0 
is_overweight = False
is_overpower = False

# ==========================================
# DATA TRACKER SYSTEM (สถิติวิเคราะห์)
# ==========================================
class DataTracker:
    def __init__(self):
        self.start_time = 0
        self.movements = [] # บันทึกพิกัด X, Y
        self.accuracy = {"p1": {"hit": 0, "miss": 0}, "p2": {"hit": 0, "miss": 0}} # แม่นยำ
        self.damage_events = [] # บันทึกเวลากับดาเมจ
        self.hp_history = {"p1": {"time": [], "hp": []}, "p2": {"time": [], "hp": []}} # HP ลดลงตามเวลา
        self.weapons = {"p1": "Unknown", "p2": "Unknown"} # เก็บชื่ออาวุธ
        self.weights = {"p1": 0, "p2": 0} # เก็บนํ้าหนัก
        
    def start_match(self, p1_hp, p2_hp, p1_load, p2_load):
        self.start_time = pygame.time.get_ticks()
        self.hp_history["p1"]["time"].append(0)
        self.hp_history["p1"]["hp"].append(p1_hp)
        self.hp_history["p2"]["time"].append(0)
        self.hp_history["p2"]["hp"].append(p2_hp)
        
        # เก็บชื่ออาวุธและน้ำหนัก
        self.weapons["p1"] = PARTS_DATA["gun"][p1_load["gun"]]["name"]
        self.weapons["p2"] = PARTS_DATA["gun"][p2_load["gun"]]["name"]
        self.weights["p1"] = sum([PARTS_DATA[cat][p1_load[cat]]["weight"] for cat in CATEGORIES])
        self.weights["p2"] = sum([PARTS_DATA[cat][p2_load[cat]]["weight"] for cat in CATEGORIES])

    def log_movement(self, p1_x, p1_y, p2_x, p2_y):
        t = (pygame.time.get_ticks() - self.start_time) / 1000.0
        self.movements.append([t, p1_x, p1_y, p2_x, p2_y])

    def log_shot(self, player_id, is_hit):
        if is_hit:
            self.accuracy[player_id]["hit"] += 1
        else:
            self.accuracy[player_id]["miss"] += 1

    def log_damage(self, shooter_id, target_id, dmg, new_hp):
        t = (pygame.time.get_ticks() - self.start_time) / 1000.0
        self.damage_events.append([t, shooter_id, target_id, dmg])
        self.hp_history[target_id]["time"].append(t)
        self.hp_history[target_id]["hp"].append(new_hp)

    def export_csv(self):
        match_id = str(int(time.time()))
        
        # Export Movement
        with open(f"movement_logs_{match_id}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time(s)", "P1_X", "P1_Y", "P2_X", "P2_Y"])
            writer.writerows(self.movements)
            
        # Export Damage Logs
        with open(f"damage_logs_{match_id}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Time(s)", "Shooter", "Target", "Damage"])
            writer.writerows(self.damage_events)

# ==========================================
# Battle Arena & Combat System Variables
# ==========================================
battle_obstacles_list = []
bullets_list = []
game_over_timer = 0
winner_text = ""
tracker = DataTracker()
last_movement_log_time = 0

p1 = {"rect": pygame.Rect(100, SCREEN_HEIGHT//2 - 50, 100, 100), "color": BLUE, "facing": (1, 0), "current_dir": "right", "images": None, "hp": 0, "max_hp": 0, "speed": 0, "dmg": 0, "cooldown": 0}
p2 = {"rect": pygame.Rect(824, SCREEN_HEIGHT//2 - 50, 100, 100), "color": GREEN, "facing": (-1, 0), "current_dir": "left", "images": None, "hp": 0, "max_hp": 0, "speed": 0, "dmg": 0, "cooldown": 0}

def calculate_player_stats(loadout):
    chassis_weight = PARTS_DATA["chassis"][loadout["chassis"]]["weight"]
    max_hp = 100 + (chassis_weight * 8) 
    motor_pow = PARTS_DATA["motor"][loadout["motor"]]["power"]
    link_weight = PARTS_DATA["linkage"][loadout["linkage"]]["weight"]
    speed = 4 + (motor_pow / 10) - (link_weight / 20)
    speed = max(2.0, min(speed, 9.0)) 
    gun_idx = loadout["gun"]
    cpu_idx = loadout["controller"]
    base_cooldowns = [8, 15, 40]
    base_dmgs = [4, 8, 35]
    cooldown = base_cooldowns[gun_idx]
    bullet_dmg = base_dmgs[gun_idx]
    
    if cpu_idx == 1:
        cooldown += 15
        bullet_dmg += 15
    elif cpu_idx == 2:
        cooldown = max(4, cooldown - 5)
        bullet_dmg = max(1, bullet_dmg - 2)
    
    return {"max_hp": int(max_hp), "hp": int(max_hp), "speed": speed, "dmg": int(bullet_dmg), "base_cooldown": cooldown, "cooldown": 0}

def create_4_directional_sprites(loadout):
    sprites = {}
    directions = ["up", "down", "left", "right"]
    
    for d in directions:
        raw_surf = pygame.Surface((300, 300), pygame.SRCALPHA)
        def draw_part(cat):
            part_data = PARTS_DATA[cat][loadout[cat]]
            paths = part_data.get("arena_imgs", {}).get(d)
            if not paths: paths = part_data.get("img")
            if not paths: return
            if isinstance(paths, str): paths = [paths]
            for path in paths:
                if path:
                    img = load_image_safe(path, (300, 300))
                    if img:
                        img = pygame.transform.scale(img, (300, 300))
                        raw_surf.blit(img, (0, 0))

        draw_part("linkage")
        draw_part("chassis")
        draw_part("gun")
        
        mask = pygame.mask.from_surface(raw_surf, 10) 
        bbox_list = mask.get_bounding_rects()
        
        if bbox_list:
            real_bbox = bbox_list[0].unionall(bbox_list[1:])
            cropped_surf = raw_surf.subsurface(real_bbox)
            scale_surf = pygame.transform.scale(cropped_surf, (100, 100))
            sprites[d] = scale_surf
        else:
            sprites[d] = pygame.transform.scale(raw_surf, (100, 100))
            
    return sprites

def init_battle():
    global p1, p2, bullets_list, game_over_timer, tracker
    bullets_list.clear()
    game_over_timer = 0
    
    p1_stats = calculate_player_stats(player1_loadout)
    p2_stats = calculate_player_stats(player2_loadout)
    p1.update(p1_stats)
    p2.update(p2_stats)
    
    p1["rect"].topleft = (100, SCREEN_HEIGHT//2 - 50)
    p2["rect"].topleft = (824, SCREEN_HEIGHT//2 - 50)
    
    p1["facing"] = (1, 0)
    p1["current_dir"] = "right"
    p2["facing"] = (-1, 0) 
    p2["current_dir"] = "left"
    
    p1["images"] = create_4_directional_sprites(player1_loadout)
    p2["images"] = create_4_directional_sprites(player2_loadout)
    
    generate_battle_arena()
    tracker.start_match(p1["hp"], p2["hp"], player1_loadout, player2_loadout)

def generate_battle_arena():
    global battle_obstacles_list
    battle_obstacles_list.clear()
    bottom_left_zone = pygame.Rect(0, SCREEN_HEIGHT - 280, 280, 280)
    bottom_right_zone = pygame.Rect(SCREEN_WIDTH - 280, SCREEN_HEIGHT - 250, 280, 250)
    num_obstacles = random.randint(5, 9) 
    min_x, max_x = 80, SCREEN_WIDTH - 80
    min_y, max_y = 150, SCREEN_HEIGHT - 80
    
    for _ in range(num_obstacles):
        if not obstacle_images: break
        obs_img = random.choice(obstacle_images)
        img_w, img_h = obs_img.get_size()
        valid_position = False
        attempts = 0
        
        while not valid_position and attempts < 100:
            rand_x = random.randint(min_x, max_x - img_w)
            rand_y = random.randint(min_y, max_y - img_h)
            new_obs_rect = pygame.Rect(rand_x, rand_y, img_w, img_h)
            padded_rect = new_obs_rect.inflate(110, 110)
            
            if padded_rect.colliderect(p1["rect"]) or padded_rect.colliderect(p2["rect"]) or new_obs_rect.colliderect(bottom_left_zone) or new_obs_rect.colliderect(bottom_right_zone):
                attempts += 1
                continue
                
            overlap = False
            for placed_obs in battle_obstacles_list:
                if padded_rect.colliderect(placed_obs["rect"]):
                    overlap = True
                    break
                    
            if not overlap:
                valid_position = True
                battle_obstacles_list.append({"img": obs_img, "rect": new_obs_rect})
            else:
                attempts += 1

def move_player(player, enemy, dx, dy):
    player["rect"].x += dx
    if player["rect"].left < 40 or player["rect"].right > SCREEN_WIDTH - 40: player["rect"].x -= dx 
    for obs in battle_obstacles_list:
        if player["rect"].colliderect(obs["rect"]): player["rect"].x -= dx; break
    if enemy["hp"] > 0 and player["rect"].colliderect(enemy["rect"]): player["rect"].x -= dx
            
    player["rect"].y += dy
    if player["rect"].top < 110 or player["rect"].bottom > SCREEN_HEIGHT - 40: player["rect"].y -= dy
    for obs in battle_obstacles_list:
        if player["rect"].colliderect(obs["rect"]): player["rect"].y -= dy; break
    if enemy["hp"] > 0 and player["rect"].colliderect(enemy["rect"]): player["rect"].y -= dy

def shoot(player, owner_id):
    if player["cooldown"] <= 0:
        bullet_rect = pygame.Rect(player["rect"].centerx, player["rect"].centery, 10, 10)
        bullets_list.append({
            "rect": bullet_rect, "vel_x": player["facing"][0] * 15, "vel_y": player["facing"][1] * 15, "dmg": player["dmg"], "owner": owner_id
        })
        player["cooldown"] = player.get("base_cooldown", 20) 

# ==========================================
# 3. Hitboxes สำหรับ UI
# ==========================================
tab_rects = []
tab_y_start = 122
tab_height = 140
for i in range(len(CATEGORIES)):
    tab_rects.append(pygame.Rect(24, tab_y_start + (i * tab_height), 121, 129))

arrow_left_rect = pygame.Rect(300, 550, 40, 40)
arrow_right_rect = pygame.Rect(880, 550, 40, 40)
next_btn_rect = pygame.Rect(850, 913, 140, 50) 

def draw_arrows():
    pygame.draw.polygon(screen, YELLOW, [(340, 550), (340, 590), (300, 570)])
    pygame.draw.polygon(screen, YELLOW, [(880, 550), (880, 590), (920, 570)])

def draw_stats():
    global is_overweight, is_overpower 
    screen.blit(bar_img, (0, 0))
    total_dps, total_weight, total_power_drain = 0, 0, 0
    for cat in CATEGORIES:
        part_data = PARTS_DATA[cat][current_parts[cat]]
        total_dps += part_data["dps"]
        total_weight += part_data["weight"]
        if cat != "power": total_power_drain += part_data["power"]
        
    max_weight = PARTS_DATA["linkage"][current_parts["linkage"]]["weight_cap"]
    max_power = PARTS_DATA["power"][current_parts["power"]]["power_cap"]
    
    dps_blocks = int(min(total_dps / 300.0, 1.0) * 10)
    weight_blocks = int(min(total_weight / max_weight, 1.0) * 10) 
    power_blocks = int(min(total_power_drain / max_power, 1.0) * 10)

    start_x = 726
    dps_y, weight_y, power_y = 191, 256, 321
    block_w, block_h, gap = 10, 18, 4

    is_overweight = total_weight > max_weight
    is_overpower = total_power_drain > max_power

    for i in range(dps_blocks): pygame.draw.rect(screen, YELLOW, (start_x + (i * (block_w + gap)), dps_y, block_w, block_h))
    for i in range(weight_blocks): pygame.draw.rect(screen, RED if is_overweight else BLUE, (start_x + (i * (block_w + gap)), weight_y, block_w, block_h))
    for i in range(power_blocks): pygame.draw.rect(screen, RED if is_overpower else GREEN, (start_x + (i * (block_w + gap)), power_y, block_w, block_h))

    screen.blit(font.render(str(total_dps), True, YELLOW), (902, dps_y-4))
    screen.blit(font.render(f"{total_weight}/{max_weight}kg", True, RED if is_overweight else BLUE), (902, weight_y-2))
    screen.blit(font.render(f"{total_power_drain}/{max_power}W", True, RED if is_overpower else GREEN), (902, power_y-2))

def draw_part_description():
    current_cat = CATEGORIES[selected_tab_index]
    desc_raw = PARTS_DATA[current_cat][current_parts[current_cat]]["desc"]
    
    desc_fixed = desc_raw.replace('\\n', '\n')
    lines = desc_fixed.split('\n')
    
    rendered_lines = [font_small.render(line, True, WHITE) for line in lines]
    text_width = max([surf.get_width() for surf in rendered_lines])
    line_height = font_small.get_linesize() 
    
    bg_rect = pygame.Rect(0, 0, text_width + 40, (line_height * len(rendered_lines)) + 30)
    bg_rect.center = (SCREEN_WIDTH // 2 + 85, SCREEN_HEIGHT - 155)
    
    pygame.draw.rect(screen, BLACK, bg_rect)
    pygame.draw.rect(screen, YELLOW, bg_rect, 2)
    
    current_y = bg_rect.top + 15
    for surf in rendered_lines:
        screen.blit(surf, surf.get_rect(centerx=bg_rect.centerx, top=current_y))
        current_y += line_height 

    if current_building_player == 1:
        control_text = "WASD / SPACE BAR"
    else:
        control_text = "ARROW KEYS / ENTER"
        
    control_surf = font_large.render(control_text, True, "white")
    control_rect = control_surf.get_rect(centerx=bg_rect.centerx-30, top=bg_rect.bottom + 35)
    screen.blit(control_surf, control_rect)

def draw_player_ui():
    screen.blit(font_large.render(f"PLAYER {current_building_player}", True, BLUE if current_building_player == 1 else GREEN), (31, 23)) 
    can_proceed = not is_overweight and not is_overpower
    pygame.draw.rect(screen, YELLOW if can_proceed else DARK_GRAY, next_btn_rect)
    pygame.draw.rect(screen, WHITE, next_btn_rect, 2)
    btn_surf = font.render("NEXT" if current_building_player == 1 else "FIGHT!", True, BLACK if can_proceed else WHITE)
    screen.blit(btn_surf, btn_surf.get_rect(center=next_btn_rect.center))

# ==========================================
# TKINTER DATA ANALYTICS DASHBOARD
# ==========================================
def show_statistics_dashboard():
    # บันทึกไฟล์ CSV
    import pyglet
    tracker.export_csv()
    font_path = "asset/dogicapixel.ttf"
    pyglet.font.add_file(font_path)
    tk_font_family = "dogica pixel"
    fm.fontManager.addfont(font_path)
    dogica_prop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = dogica_prop.get_name()
    # --- GAME UI STYLING VARIABLES ---
    # Colors picked directly from your screenshot
    ui_bg = "#1e222e"          # Dark slate blue (Side panel background)
    panel_bg = "#2a303c"       # Lighter slate (Inner panels)
    highlight = "#fadb26"      # The bright yellow for borders/text
    p1_color = "#3399FF"       # Blue (from the Weight bar)
    p2_color = "#33CC33"       # Green (from the Power bar)
    text_color = "#ffffff"     # White text
    
    # Standard fonts that mimic the blocky look. 
    # (Pro-tip: If you have a custom .ttf like "Press Start 2P" loaded in your OS, use that here!)
    ui_font = (tk_font_family, 14)
    title_font = (tk_font_family, 24)
    
    plt.style.use('dark_background')
    
    root = tk.Tk()
    root.title("Match Analytics Dashboard")
    root.geometry("1024x986")
    root.configure(bg=ui_bg)
    
    # Outer frame
    border_frame = tk.Frame(root, bg=highlight, bd=0)
    border_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Inner frame
    inner_frame = tk.Frame(border_frame, bg=ui_bg, bd=0)
    inner_frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
    
    title_label = tk.Label(inner_frame, text=f"MATCH RESULTS - {winner_text} WINS", 
                           font=title_font, bg=ui_bg, fg=p1_color)
    title_label.pack(pady=15)
    
    fig, axs = plt.subplots(2, 2, figsize=(10, 7))
    fig.patch.set_facecolor(ui_bg)
    fig.tight_layout(pad=4.0)

    # Apply styling to all Matplotlib axes
    for ax in axs.flat:
        ax.set_facecolor(panel_bg)
        ax.tick_params(colors=text_color, length=0, labelsize=8) # Smaller labels for Dogica
        
        ax.spines['bottom'].set_color(highlight)
        ax.spines['left'].set_color(highlight)
        ax.spines['top'].set_color(highlight)
        ax.spines['right'].set_color(highlight)
        ax.spines['bottom'].set_linewidth(2)
        ax.spines['left'].set_linewidth(2)
        ax.spines['top'].set_linewidth(2)
        ax.spines['right'].set_linewidth(2)
        
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label]):
            item.set_color(highlight)
            # No need to set fontfamily here, plt.rcParams handled it!

    # 1. Accuracy Ratio
    axs[0, 0].set_title("ACCURACY RATIO")
    p1_hits, p1_miss = tracker.accuracy["p1"]["hit"], tracker.accuracy["p1"]["miss"]
    p2_hits, p2_miss = tracker.accuracy["p2"]["hit"], tracker.accuracy["p2"]["miss"]
    
    if (p1_hits + p1_miss + p2_hits + p2_miss) > 0:
        labels = ['P1 Hit', 'P1 Miss', 'P2 Hit', 'P2 Miss']
        sizes = [p1_hits, p1_miss, p2_hits, p2_miss]
        colors = [p1_color, '#1a4c80', p2_color, '#1a661a'] 
        wedges, texts, autotexts = axs[0, 0].pie(sizes, labels=labels, colors=colors, 
                                                 autopct='%1.1f%%', startangle=90, 
                                                 wedgeprops={'edgecolor': ui_bg, 'linewidth': 3},
                                                 textprops={'color': text_color, 'fontsize': 8})
    else:
        axs[0, 0].text(0.5, 0.5, "NO SHOTS", ha='center', va='center', 
                       color=highlight)

    # 2. HP Reduction Trend
    axs[0, 1].set_title("HP REDUCTION")
    axs[0, 1].step(tracker.hp_history["p1"]["time"], tracker.hp_history["p1"]["hp"], 
                   label="P1 HP", color=p1_color, linewidth=3, where='post')
    axs[0, 1].step(tracker.hp_history["p2"]["time"], tracker.hp_history["p2"]["hp"], 
                   label="P2 HP", color=p2_color, linewidth=3, where='post')
    axs[0, 1].set_xlabel("Time (s)")
    axs[0, 1].set_ylabel("HP")
    legend1 = axs[0, 1].legend(prop={'size': 8})
    legend1.get_frame().set_facecolor(panel_bg)
    legend1.get_frame().set_edgecolor(highlight)

    # 3. Movement Heatmap
    axs[1, 0].set_title("MAP CONTROL")
    if tracker.movements:
        p1_x = [m[1] for m in tracker.movements]
        p1_y = [m[2] for m in tracker.movements]
        p2_x = [m[3] for m in tracker.movements]
        p2_y = [m[4] for m in tracker.movements]
        axs[1, 0].scatter(p1_x, p1_y, c=p1_color, s=50, label="P1", marker='s')
        axs[1, 0].scatter(p2_x, p2_y, c=p2_color, s=50, label="P2", marker='s')
    axs[1, 0].set_xlim(0, SCREEN_WIDTH)
    axs[1, 0].set_ylim(SCREEN_HEIGHT, 0)
    legend2 = axs[1, 0].legend(prop={'size': 8})
    legend2.get_frame().set_facecolor(panel_bg)
    legend2.get_frame().set_edgecolor(highlight)

    # 4. Total Damage Dealt
    axs[1, 1].set_title("TOTAL DAMAGE")
    p1_total_dmg = sum([d[3] for d in tracker.damage_events if d[1] == "p1"])
    p2_total_dmg = sum([d[3] for d in tracker.damage_events if d[1] == "p2"])
    
    bars = axs[1, 1].bar([f"P1", f"P2"], [p1_total_dmg, p2_total_dmg], 
                         color=[p1_color, p2_color], edgecolor=ui_bg, linewidth=4)
    axs[1, 1].set_ylabel("DMG")
    
    for bar in bars:
        yval = bar.get_height()
        axs[1, 1].text(bar.get_x() + bar.get_width()/2, yval + (yval*0.02), 
                       f"{int(yval)}", ha='center', va='bottom', 
                       color=highlight, fontsize=10)

    # Add to Tkinter
    canvas = FigureCanvasTkAgg(fig, master=inner_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Retro EXIT button
    close_btn = tk.Button(inner_frame, text="EXIT DASHBOARD", command=root.destroy, 
                          bg=highlight, fg="black", font=ui_font, 
                          activebackground="white", activeforeground="black",
                          relief="flat", bd=0, padx=20, pady=5)
    close_btn.pack(pady=15)
    
    root.mainloop()
# ==========================================
# Main Game Loop
# ==========================================
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and game_state == "GARAGE": 
            mouse_pos = event.pos
            for i, rect in enumerate(tab_rects):
                if rect.collidepoint(mouse_pos): selected_tab_index = i
            
            current_cat = CATEGORIES[selected_tab_index]
            if arrow_left_rect.collidepoint(mouse_pos): current_parts[current_cat] = (current_parts[current_cat] - 1) % 3
            if arrow_right_rect.collidepoint(mouse_pos): current_parts[current_cat] = (current_parts[current_cat] + 1) % 3

            if next_btn_rect.collidepoint(mouse_pos) and not is_overweight and not is_overpower:
                if current_building_player == 1:
                    player1_loadout = current_parts.copy()
                    current_building_player = 2
                    current_parts = {cat: 0 for cat in CATEGORIES} 
                elif current_building_player == 2:
                    player2_loadout = current_parts.copy()
                    init_battle()
                    game_state = "BATTLE"

    # ==========================================
    # Render: GARAGE STATE
    # ==========================================
    if game_state == "GARAGE":
        screen.blit(bg_img, (75, 0)) 
        screen.blit(tab_img, (0, 0))
        pygame.draw.rect(screen, YELLOW, tab_rects[selected_tab_index], 2)

        center_x, center_y = 340, 365
        link_data = PARTS_DATA["linkage"][current_parts["linkage"]]["img"]
        if link_data[0]: screen.blit(load_image_safe(link_data[0], (300, 300)), (center_x, center_y))
        for cat in ["chassis", "gun"]:
            img_path = PARTS_DATA[cat][current_parts[cat]]["img"]
            if img_path: screen.blit(load_image_safe(img_path, (300, 300)), (center_x, center_y))
        if link_data[1]: screen.blit(load_image_safe(link_data[1], (300, 300)), (center_x, center_y))

        draw_arrows()
        draw_stats() 
        draw_part_description()
        draw_player_ui()

    # ==========================================
    # Logic & Render: BATTLE STATE
    # ==========================================
    elif game_state == "BATTLE":
        screen.blit(battle_bg, (0, 0))
        
        # --- ระบบบันทึกการเคลื่อนที่ (ทุกๆ 1 วินาที) ---
        current_time = pygame.time.get_ticks()
        if current_time - last_movement_log_time >= 1000 and game_over_timer == 0:
            tracker.log_movement(p1["rect"].centerx, p1["rect"].centery, p2["rect"].centerx, p2["rect"].centery)
            last_movement_log_time = current_time

        # --- ระบบเดิน Player 1 (W A S D) ---
        if p1["hp"] > 0 and game_over_timer == 0:
            keys = pygame.key.get_pressed()
            dx1, dy1 = 0, 0
            if keys[pygame.K_w]: dy1 = -p1["speed"]; p1["facing"] = (0, -1); p1["current_dir"] = "up"
            if keys[pygame.K_s]: dy1 = p1["speed"]; p1["facing"] = (0, 1); p1["current_dir"] = "down"
            if keys[pygame.K_a]: dx1 = -p1["speed"]; p1["facing"] = (-1, 0); p1["current_dir"] = "left"
            if keys[pygame.K_d]: dx1 = p1["speed"]; p1["facing"] = (1, 0); p1["current_dir"] = "right"
            
            move_player(p1, p2, dx1, dy1)
            if keys[pygame.K_SPACE]: shoot(p1, "p1")
            if p1["cooldown"] > 0: p1["cooldown"] -= 1

        # --- ระบบเดิน Player 2 (Arrows) ---
        if p2["hp"] > 0 and game_over_timer == 0:
            keys = pygame.key.get_pressed()
            dx2, dy2 = 0, 0
            if keys[pygame.K_UP]: dy2 = -p2["speed"]; p2["facing"] = (0, -1); p2["current_dir"] = "up"
            if keys[pygame.K_DOWN]: dy2 = p2["speed"]; p2["facing"] = (0, 1); p2["current_dir"] = "down"
            if keys[pygame.K_LEFT]: dx2 = -p2["speed"]; p2["facing"] = (-1, 0); p2["current_dir"] = "left"
            if keys[pygame.K_RIGHT]: dx2 = p2["speed"]; p2["facing"] = (1, 0); p2["current_dir"] = "right"
            
            if keys[pygame.K_RETURN]: shoot(p2, "p2")
            move_player(p2, p1, dx2, dy2)
            if p2["cooldown"] > 0: p2["cooldown"] -= 1

        # --- ระบบกระสุน & การเก็บบันทึกข้อมูล (Update & Draw) ---
        for b in bullets_list[:]:
            b["rect"].x += b["vel_x"]
            b["rect"].y += b["vel_y"]
            
            bullet_color = BLUE if b["owner"] == "p1" else GREEN
            pygame.draw.rect(screen, bullet_color, b["rect"])
            
            # ชนนอกจอ (Miss)
            if b["rect"].left < 40 or b["rect"].right > SCREEN_WIDTH-40 or b["rect"].top < 110 or b["rect"].bottom > SCREEN_HEIGHT-40:
                tracker.log_shot(b["owner"], is_hit=False)
                bullets_list.remove(b)
                continue
                
            # ชนอุปสรรค (Miss)
            hit_obs = False
            for obs in battle_obstacles_list:
                if b["rect"].colliderect(obs["rect"]):
                    hit_obs = True
                    break
            if hit_obs:
                tracker.log_shot(b["owner"], is_hit=False)
                bullets_list.remove(b)
                continue
                
            # ชนศัตรู (Hit & Damage Event)
            if b["owner"] == "p1" and b["rect"].colliderect(p2["rect"]) and p2["hp"] > 0:
                p2["hp"] -= b["dmg"]
                tracker.log_shot("p1", is_hit=True)
                tracker.log_damage("p1", "p2", b["dmg"], max(0, p2["hp"]))
                bullets_list.remove(b)
            elif b["owner"] == "p2" and b["rect"].colliderect(p1["rect"]) and p1["hp"] > 0:
                p1["hp"] -= b["dmg"]
                tracker.log_shot("p2", is_hit=True)
                tracker.log_damage("p2", "p1", b["dmg"], max(0, p1["hp"]))
                bullets_list.remove(b)

        # --- ตรวจสอบการจบเกม (ทิ้งระยะ 2 วิ ก่อนโชว์กราฟ) ---
        if (p1["hp"] <= 0 or p2["hp"] <= 0) and game_over_timer == 0:
            winner_text = "PLAYER 2" if p1["hp"] <= 0 else "PLAYER 1"
            game_over_timer = pygame.time.get_ticks()
            
        if game_over_timer > 0:
            if pygame.time.get_ticks() - game_over_timer > 2000:
                pygame.quit() # ปิดหน้าจอ Pygame ชั่วคราว
                show_statistics_dashboard() # โชว์หน้าต่าง Tkinter
                sys.exit()

        # --- วาดอุปสรรค ---
        for obs_data in battle_obstacles_list:
            screen.blit(obs_data["img"], obs_data["rect"].topleft)
            
        # --- วาดผู้เล่นและหลอดเลือด (HP Bar) ---
        for p, name in [(p1, "P1"), (p2, "P2")]:
            if p["hp"] > 0:
                if p["images"] and p["current_dir"] in p["images"]:
                    current_sprite = p["images"][p["current_dir"]]
                    screen.blit(current_sprite, p["rect"].topleft)
                else:
                    pygame.draw.rect(screen, p["color"], p["rect"]) 
                
                text = font_small.render(name, True, WHITE)
                screen.blit(text, (p["rect"].centerx - text.get_width()//2, p["rect"].top - 30))
                
                hp_ratio = p["hp"] / p["max_hp"]
                pygame.draw.rect(screen, RED, (p["rect"].x, p["rect"].top - 12, 100, 8))
                pygame.draw.rect(screen, GREEN, (p["rect"].x, p["rect"].top - 12, int(100 * hp_ratio), 8))
            else:
                text = font.render(f"{name} DESTROYED", True, RED)
                screen.blit(text, (p["rect"].centerx - text.get_width()//2, p["rect"].centery))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()