import pygame
import threading
import serial
import queue
import time

# ----------------------------
# CONFIG
# ----------------------------
SERIAL_PORT = "/dev/cu.SLAB_USBtoUART"
BAUD_RATE = 115200

event_queue = queue.Queue()

# ----------------------------
# SERIAL THREAD
# ----------------------------
def serial_thread():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    except:
        print("Serial failed. Running without input.")
        return

    while True:
        try:
            line = ser.readline().decode(errors="ignore").strip()
            if line:
                event_queue.put(line)
        except:
            pass


# ----------------------------
# PYGAME SETUP
# ----------------------------
pygame.init()
screen = pygame.display.set_mode((700, 520))
pygame.display.set_caption("Reconfigurable UI Improved")
clock = pygame.time.Clock()

font_big = pygame.font.SysFont("Arial", 40, bold=True)
font_med = pygame.font.SysFont("Arial", 26, bold=True)

WHITE = (255, 255, 255)
PASTEL_YELLOW = (255, 255, 210)
PASTEL_BLUE   = (210, 235, 255)

BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (230, 230, 230)

FLASH_DURATION = 0.25

mode = "unknown"
flash_timers = {}

# Stick figure (scaled-up)
character_pos = [350, 420]


def flash(key):
    flash_timers[key] = time.time() + FLASH_DURATION


def flashing(key):
    return flash_timers.get(key, 0) > time.time()


# ----------------------------
# COLOR SET
# ----------------------------
COLORS = {
    "W": (140, 220, 255),
    "A": (200, 160, 255),
    "S": (160, 240, 160),
    "D": (255, 160, 200),
    "LEFT": (180, 220, 255),
    "RIGHT": (255, 180, 220),
}


# ----------------------------
# BIG CUTE ORIGINAL STICK FIGURE
# ----------------------------
def draw_stick_figure_big():
    x, y = character_pos
    SCALE = 1.7

    head_r = int(10 * SCALE)
    pygame.draw.circle(screen, BLACK, (x, y - int(25 * SCALE)), head_r)

    # body
    pygame.draw.line(screen, BLACK,
                     (x, y - int(15 * SCALE)),
                     (x, y + int(20 * SCALE)),
                     int(3 * SCALE))

    # legs
    pygame.draw.line(screen, BLACK,
                     (x, y + int(20 * SCALE)),
                     (x - int(10 * SCALE), y + int(40 * SCALE)),
                     int(3 * SCALE))

    pygame.draw.line(screen, BLACK,
                     (x, y + int(20 * SCALE)),
                     (x + int(10 * SCALE), y + int(40 * SCALE)),
                     int(3 * SCALE))

    # arms
    pygame.draw.line(screen, BLACK,
                     (x, y - int(10 * SCALE)),
                     (x - int(15 * SCALE), y + int(5 * SCALE)),
                     int(3 * SCALE))

    pygame.draw.line(screen, BLACK,
                     (x, y - int(10 * SCALE)),
                     (x + int(15 * SCALE), y + int(5 * SCALE)),
                     int(3 * SCALE))


# ----------------------------
# TEXT HELPER
# ----------------------------
def draw_text_center(text, cx, cy, font, color=BLACK):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(cx, cy))
    screen.blit(surf, rect)


# ----------------------------
# CLEAN MOUSE (scroll wheel fixed)
# ----------------------------
def draw_mouse_ui():
    draw_text_center("MOUSE MODE", 350, 40, font_big)

    mx, my = 350, 280

    # Mouse outline
    body = [
        (mx - 80, my - 140),
        (mx + 80, my - 140),
        (mx + 95, my + 70),
        (mx,     my + 150),
        (mx - 95, my + 70)
    ]

    pygame.draw.polygon(screen, LIGHT_GRAY, body)
    pygame.draw.polygon(screen, BLACK, body, 4)

    # Buttons
    left_color  = COLORS["LEFT"] if flashing("LEFT") else WHITE
    right_color = COLORS["RIGHT"] if flashing("RIGHT") else WHITE

    left_btn = pygame.Rect(mx - 70, my - 120, 60, 95)
    right_btn = pygame.Rect(mx + 10, my - 120, 60, 95)

    pygame.draw.rect(screen, left_color, left_btn,  border_radius=20)
    pygame.draw.rect(screen, BLACK,      left_btn, 3, border_radius=20)

    pygame.draw.rect(screen, right_color, right_btn, border_radius=20)
    pygame.draw.rect(screen, BLACK,       right_btn, 3, border_radius=20)

    # SCROLL WHEEL (thicker + between L/R buttons)
    pygame.draw.rect(screen, BLACK, (mx - 12, my - 105, 24, 70), border_radius=8)


# ----------------------------
# WASD BUTTONS
# ----------------------------
def draw_button(x, y, label):
    color = COLORS[label] if flashing(label) else GRAY

    pygame.draw.rect(screen, color, (x, y, 70, 70), border_radius=16)
    pygame.draw.rect(screen, BLACK, (x, y, 70, 70), 3, border_radius=16)

    draw_text_center(label, x + 35, y + 35, font_med)


def draw_controller_ui():
    draw_text_center("CONTROLLER MODE", 350, 40, font_big)

    draw_button(290, 110, "W")
    draw_button(200, 200, "A")
    draw_button(290, 200, "S")
    draw_button(380, 200, "D")

    draw_stick_figure_big()


# ----------------------------
# START SERIAL THREAD
# ----------------------------
threading.Thread(target=serial_thread, daemon=True).start()


# ----------------------------
# MAIN LOOP
# ----------------------------
running = True
while running:
    # MODE-DEPENDENT BACKGROUNDS
    if mode == "mouse":
        screen.fill(PASTEL_YELLOW)
    elif mode == "controller":
        screen.fill(PASTEL_BLUE)
    else:
        screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # HANDLE SERIAL INPUT
    while not event_queue.empty():
        msg = event_queue.get().strip()

        # Handle special state
        if msg == "transitioning...":
            mode = "unknown"
            continue

        # -------------------------
        # MOUSE EVENTS
        # -------------------------
        if msg == "LEFT CLICK":
            mode = "mouse"
            flash("LEFT")
            continue

        if msg == "RIGHT CLICK":
            mode = "mouse"
            flash("RIGHT")
            continue

        # -------------------------
        # CONTROLLER EVENTS
        # -------------------------
        step = 30

        if msg.startswith("W"):
            mode = "controller"
            character_pos[1] -= step
            flash("W")
        elif msg.startswith("A"):
            mode = "controller"
            character_pos[0] -= step
            flash("A")
        elif msg.startswith("S"):
            mode = "controller"
            character_pos[1] += step
            flash("S")
        elif msg.startswith("D"):
            mode = "controller"
            character_pos[0] += step
            flash("D")

        # Clamp so the little guy doesn’t climb into the WASD buttons
        if mode == "controller" and character_pos[1] < 300:
            character_pos[1] = 300

    # DRAW UI CONTENT
    if mode == "mouse":
        draw_mouse_ui()
    elif mode == "controller":
        draw_controller_ui()
    else:
        draw_text_center("Waiting for mode...", 350, 260, font_big)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
