"""
Project Name: Cyber Security Aura - Sci-Fi Shield Shield & Orbiting Ring
Description: Menggabungkan MediaPipe dan PyOpenGL. 
             - Gestur 1 Jari -> Emoji Tersenyum (Cyan)
             - Gestur Terbuka -> Perisai & Lingkaran Berputar (Hijau) + "SYSTEM SAFE"
             - Gestur Mengepal -> Gembok & Teks "ALERT" (Merah)
             - Tidak Ada Tangan -> Kabut Abstrak (Biru)
"""

import cv2
import mediapipe as mp
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import threading
import time
import random

# ==========================================
# 1. SHARED DATA (Jembatan Antar Thread)
# ==========================================
lock = threading.Lock()
shared_data = {
    "status": "NO_HANDS",  
    "running": True,
    "hud_frame": None  
}

# ==========================================
# 2. GENERASI GEOMETRI DATA BENTUK (NumPy)
# ==========================================
NUM_PARTICLES = 2500  

# --- SHAPE 1: KABUT ABSTRAK TANPA BENTUK (No Hands - Biru) ---
pos_no_hands = np.random.uniform(-3.0, 3.0, (NUM_PARTICLES, 3))

# --- SHAPE 2: EMOJI TERSENYUM (1 Jari - Cyan) ---
pos_emoji = np.zeros((NUM_PARTICLES, 3))
part_face = int(NUM_PARTICLES * 0.6)       
part_eyes = int(NUM_PARTICLES * 0.15)      
part_smile = NUM_PARTICLES - part_face - part_eyes 

for i in range(part_face):
    angle = np.random.uniform(0, 2 * np.pi)
    radius = np.random.uniform(2.0, 2.2) 
    pos_emoji[i, 0] = radius * np.cos(angle)
    pos_emoji[i, 1] = radius * np.sin(angle)
    pos_emoji[i, 2] = np.random.uniform(-0.1, 0.1)

for i in range(part_face, part_face + part_eyes):
    if random.random() < 0.5:
        pos_emoji[i, 0] = np.random.uniform(-0.7, -0.5)
    else:
        pos_emoji[i, 0] = np.random.uniform(0.5, 0.7)
    pos_emoji[i, 1] = np.random.uniform(0.6, 0.9)
    pos_emoji[i, 2] = np.random.uniform(-0.1, 0.1)

for i in range(part_face + part_eyes, NUM_PARTICLES):
    angle = np.random.uniform(np.pi + 0.3, 2 * np.pi - 0.3) 
    radius = np.random.uniform(1.0, 1.2)
    pos_emoji[i, 0] = radius * np.cos(angle)
    pos_emoji[i, 1] = radius * np.sin(angle) + 0.2 
    pos_emoji[i, 2] = np.random.uniform(-0.1, 0.1)


# --- SHAPE 3: PERISAI PADAT & DUAL-RING TERURAI (Tangan Terbuka - Hijau) ---
pos_perisai = np.zeros((NUM_PARTICLES, 3))

# Pembagian partikel agar terurai dan muat untuk 2 lingkaran
num_shield_body = 1200 
num_shield_top = 100   
num_shield = num_shield_body + num_shield_top

num_ring_in = 600   # Lingkaran dalam (Terurai)
num_ring_out = 600  # Lingkaran luar (Terurai)

# --- BAGIAN A.1: Badan Perisai Padat Tengah ---
for i in range(num_shield_body):
    y = np.random.uniform(-0.5, 2.0)
    if y > 1.2:
        base_w = 1.05
        width = base_w - 0.2 * (2.0 - y) - 0.1 * np.sin(np.pi * (y - 1.2) / 0.8)
    else:
        factor = (y + 0.5) / 1.7
        width = 1.05 * np.sin(factor * np.pi / 2)
    width = max(0.02, width)
    z_curve = 0.1 * np.cos(np.random.uniform(-np.pi/2, np.pi/2))
    
    pos_perisai[i, 0] = np.random.uniform(-width, width)
    pos_perisai[i, 1] = y
    pos_perisai[i, 2] = z_curve - 0.1

# --- BAGIAN A.2: Garis Penutup Mahkota Atas ---
x_top = np.linspace(-0.85, 0.85, num_shield_top)
for i in range(num_shield_top):
    idx = num_shield_body + i
    pos_perisai[idx, 0] = x_top[i]
    pos_perisai[idx, 1] = 2.0 - 0.12 * (1.0 - np.abs(x_top[i] / 0.85))
    pos_perisai[idx, 2] = -0.1

# --- BAGIAN B.1: Lingkaran DALAM (Radius Lebih Kecil: 1.45) ---
start_ring_in = num_shield
for i in range(start_ring_in, start_ring_in + num_ring_in):
    angle = np.random.uniform(0, 2 * np.pi)
    radius = np.random.uniform(1.4, 1.5) # Rapat tipis memutari perisai dekat
    pos_perisai[i, 0] = radius * np.cos(angle)
    pos_perisai[i, 1] = radius * np.sin(angle) + 0.75
    pos_perisai[i, 2] = np.random.uniform(-0.02, 0.02)

# --- BAGIAN B.2: Lingkaran LUAR (Radius Lebih Besar: 1.9) ---
start_ring_out = start_ring_in + num_ring_in
for i in range(start_ring_out, NUM_PARTICLES):
    angle = np.random.uniform(0, 2 * np.pi)
    radius = np.random.uniform(1.85, 1.95) # Berada di luar lingkaran pertama
    pos_perisai[i, 0] = radius * np.cos(angle)
    pos_perisai[i, 1] = radius * np.sin(angle) + 0.75
    pos_perisai[i, 2] = np.random.uniform(-0.02, 0.02)

# --- SHAPE 4: GEMBOK CYBER (Tangan Mengepal - Merah) ---
pos_gembok = np.zeros((NUM_PARTICLES, 3))
half = NUM_PARTICLES // 2
for i in range(half):
    pos_gembok[i, 0] = np.random.uniform(-1.2, 1.2)
    pos_gembok[i, 1] = np.random.uniform(-1.8, -0.2)
    pos_gembok[i, 2] = np.random.uniform(-0.5, 0.5)
for i in range(half, NUM_PARTICLES):
    angle = np.random.uniform(0, np.pi)
    radius = np.random.uniform(0.7, 0.9)
    pos_gembok[i, 0] = radius * np.cos(angle)
    pos_gembok[i, 1] = radius * np.sin(angle) - 0.2
    pos_gembok[i, 2] = np.random.uniform(-0.1, 0.1)

current_pos = np.copy(pos_no_hands)

# ==========================================
# 3. KONFIGURASI MATRIX & HUD TEXT
# ==========================================
WIDTH, HEIGHT = 1000, 700
FONT_SIZE = 16
NUM_COLUMNS = int(WIDTH / FONT_SIZE)

matrix_drops = [random.randint(-HEIGHT, 0) for _ in range(NUM_COLUMNS)]
matrix_chars = [str(random.randint(0, 1)) for _ in range(NUM_COLUMNS)]

pygame.font.init()
font_matrix = pygame.font.SysFont("consolas", FONT_SIZE, bold=True)
font_hud = pygame.font.SysFont("arial", 14, bold=True)
font_status_big = pygame.font.SysFont("impact", 72) 

# ==========================================
# 4. AI DETEKSI GESTUR (OpenCV & MediaPipe)
# ==========================================
def analisa_4_gestur(hand_landmarks):
    tips = [8, 12, 16, 20]  
    pips = [6, 10, 14, 18]
    jari_terbuka = [hand_landmarks.landmark[t].y < hand_landmarks.landmark[p].y for t, p in zip(tips, pips)]
    
    telunjuk_berdiri = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
    tengah_turun = hand_landmarks.landmark[12].y > hand_landmarks.landmark[10].y
    manis_turun = hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y
    kelingking_turun = hand_landmarks.landmark[20].y > hand_landmarks.landmark[18].y

    if telunjuk_berdiri and tengah_turun and manis_turun and kelingking_turun:
        return "ABSTRAK" 
    elif sum(jari_terbuka) == 0:
        return "GEMBOK"
    elif sum(jari_terbuka) >= 3:
        return "PERISAI"
    return None

def camera_cyber_thread():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)   
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7)
    
    print("\n[INFO] AI Kamera Aktif. Sistem Pemantau Siap Jalan...")

    while shared_data["running"]:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.01)
            continue
        
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        
        current_detected_status = None
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                current_detected_status = analisa_4_gestur(hand_landmarks)
                mp.solutions.drawing_utils.draw_landmarks(
                    frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp.solutions.drawing_utils.DrawingSpec(color=(0, 150, 255), thickness=2, circle_radius=2),
                    mp.solutions.drawing_utils.DrawingSpec(color=(255, 255, 255), thickness=1, circle_radius=1)
                )
        else:
            current_detected_status = "NO_HANDS"
        
        with lock:
            if current_detected_status:
                shared_data["status"] = current_detected_status
            shared_data["hud_frame"] = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
        time.sleep(0.01)
        
    cap.release()

# ==========================================
# 5. RENDER BACKGROUND MATRIX & SENSOR HUD
# ==========================================
def draw_binary_matrix(status):
    global matrix_drops, matrix_chars
    
    if status == "NO_HANDS": speed, color = 5, (20, 80, 220)   
    elif status == "ABSTRAK": speed, color = 18, (0, 195, 255)  
    elif status == "PERISAI": speed, color = 10, (0, 220, 60)   
    else: speed, color = 18, (240, 15, 30)  
    
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    for i in range(NUM_COLUMNS):
        matrix_drops[i] += speed
        if matrix_drops[i] > HEIGHT or random.random() > 0.975:
            matrix_drops[i] = random.randint(-100, 0)
        if random.random() > 0.8:
            matrix_chars[i] = str(random.randint(0, 1))
            
        x_pos = i * FONT_SIZE
        y_pos = matrix_drops[i]
        
        if 0 < y_pos < HEIGHT:
            glWindowPos2i(x_pos, HEIGHT - y_pos)
            alpha = int(255 * (1.0 - (y_pos / HEIGHT)))
            text_surface = font_matrix.render(matrix_chars[i], True, (*color, alpha))
            text_data = pygame.image.tostring(text_surface, "RGBA", True)
            glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)

def draw_camera_texture_hud(frame_data):
    if frame_data is None:
        return
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    fh, fw, _ = frame_data.shape
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, fw, fh, 0, GL_RGB, GL_UNSIGNED_BYTE, frame_data)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WIDTH, 0, HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 1.0); glVertex2i(740, 500)
    glTexCoord2f(1.0, 1.0); glVertex2i(980, 500)
    glTexCoord2f(1.0, 0.0); glVertex2i(980, 680)
    glTexCoord2f(0.0, 0.0); glVertex2i(740, 680)
    glEnd()
    
    glDisable(GL_TEXTURE_2D)
    glLineWidth(2.0)
    glColor3f(0.0, 0.8, 1.0)
    glBegin(GL_LINE_LOOP)
    glVertex2i(740, 500)
    glVertex2i(980, 500)
    glVertex2i(980, 680)
    glVertex2i(740, 680)
    glEnd()
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)
    glDeleteTextures([tex_id])

def draw_hud_interface(status):
    glDisable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    text_lines = [
        " [•] SYSTEM CORE : MULTI-SHAPE CYPHER ENGINE",
        f" [!] CURRENT SHAPE: {status if status != 'ABSTRAK' else 'EMOJI SMILE'}",
        f" [>] ENGINE STATE: {'SCANNING HANDS...' if status == 'NO_HANDS' else 'TRACKING ACTIVE'}",
        " [•] GESTURES: No Hands (Kabut) | 1-Jari (Emoji) | Terbuka (Perisai) | Mengepal (Gembok)"
    ]
    
    if status == "NO_HANDS": hud_color = (30, 100, 255)
    elif status == "ABSTRAK": hud_color = (0, 200, 255)
    elif status == "PERISAI": hud_color = (0, 255, 100)
    else: hud_color = (255, 30, 50)
    
    start_y = 25
    for i, line in enumerate(text_lines):
        text_surface = font_hud.render(line, True, hud_color)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        glWindowPos2i(20, HEIGHT - (start_y + (i * 22)))
        glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    # Indikator Teks Kondisi di Bawah Tengah Layar Grafik
    if status == "GEMBOK" and (int(time.time() * 4) % 2 == 0):
        alert_surface = font_status_big.render("SYSTEM ALERT", True, (255, 10, 20))
        alert_data = pygame.image.tostring(alert_surface, "RGBA", True)
        glWindowPos2i(int(WIDTH/2 - alert_surface.get_width()/2), 60)
        glDrawPixels(alert_surface.get_width(), alert_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, alert_data)
        
    elif status == "PERISAI":
        safe_surface = font_status_big.render("SYSTEM SAFE", True, (0, 255, 50))
        safe_data = pygame.image.tostring(safe_surface, "RGBA", True)
        glWindowPos2i(int(WIDTH/2 - safe_surface.get_width()/2), 60)
        glDrawPixels(safe_surface.get_width(), safe_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, safe_data)

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glEnable(GL_DEPTH_TEST)

# ==========================================
# 6. MAIN ENGINE & LOOP RENDERING
# ==========================================
if __name__ == "__main__":
    ai_thread = threading.Thread(target=camera_cyber_thread, daemon=True)
    ai_thread.start()
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Cyber Security Aura - Complete Geometry Visualizer")
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (WIDTH / HEIGHT), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    
    clock = pygame.time.Clock()
    rotation_angle = 0.0

    while shared_data["running"]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                shared_data["running"] = False

        with lock:
            current_status = shared_data["status"]
            current_frame = shared_data["hud_frame"]
            
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 1. Background Matrix
        draw_binary_matrix(current_status)
        
        # 2. Render Tab Kamera (Kanan Atas)
        if current_frame is not None:
            draw_camera_texture_hud(current_frame)
        
        # 3. Render Status HUD & Teks Kondisi Atas/Bawah
        draw_hud_interface(current_status)
        
        # 4. Setup Gambar Objek 3D
        glLoadIdentity()
        glTranslatef(0.0, -0.2, -7.5) # Koordinat Y digeser turun sedikit agar objek menggantung seimbang
        
        if current_status == "NO_HANDS":
            target_pos = pos_no_hands
            rotation_angle += 0.2                  
            particle_color = (0.1, 0.4, 1.0, 0.5)  
        elif current_status == "ABSTRAK":
            target_pos = pos_emoji
            rotation_angle += 0.5                  
            particle_color = (0.0, 0.8, 1.0, 0.85) 
        elif current_status == "PERISAI":
            target_pos = pos_perisai
            # Kecepatan rotasi cincin dipercepat agar gerakan memutar ornamen cyber terasa halus
            rotation_angle += 1.2                  
            particle_color = (0.0, 1.0, 0.3, 0.85) 
        else: # GEMBOK
            target_pos = pos_gembok
            rotation_angle += 4.5                  
            particle_color = (1.0, 0.1, 0.2, 0.95) 
            
        current_pos += (target_pos - current_pos) * 0.09
        
        # Render Partikel dengan Pemisahan Khusus Mode Perisai Statis + Lingkaran Dinamis
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glPointSize(4.5)  
        
        if current_status == "PERISAI":
            # [A] RENDER PERISAI TENGAH (Diam Tegak Simetris)
            glPushMatrix()
            glRotatef(0, 0.0, 1.0, 0.0) 
            glBegin(GL_POINTS)
            glColor4f(*particle_color)
            for i in range(num_shield):
                glVertex3f(current_pos[i, 0], current_pos[i, 1], current_pos[i, 2])
            glEnd()
            glPopMatrix()
            
            # [B] RENDER LINGKARAN DALAM (Berputar KANAN / Searah Jarum Jam)
            glPushMatrix()
            glTranslatef(0.0, 0.75, 0.0)
            glRotatef(rotation_angle * 0.6, 0.0, 0.0, 1.0) # 🔄 Nilai Positif = Putar Kanan
            glTranslatef(0.0, -0.75, 0.0)
            glBegin(GL_POINTS)
            glColor4f(*particle_color)
            for i in range(num_shield, num_shield + num_ring_in):
                glVertex3f(current_pos[i, 0], current_pos[i, 1], current_pos[i, 2])
            glEnd()
            glPopMatrix()
            
            # [C] RENDER LINGKARAN LUAR (Berputar KIRI / Berlawanan Jarum Jam)
            glPushMatrix()
            glTranslatef(0.0, 0.75, 0.0)
            glRotatef(-rotation_angle * 0.4, 0.0, 0.0, 1.0) # 🔄 Nilai Negatif (-) = Putar Kiri
            glTranslatef(0.0, -0.75, 0.0)
            glBegin(GL_POINTS)
            glColor4f(*particle_color)
            for i in range(num_shield + num_ring_in, NUM_PARTICLES):
                glVertex3f(current_pos[i, 0], current_pos[i, 1], current_pos[i, 2])
            glEnd()
            glPopMatrix()
            
            # Update sudut animasi universal
            rotation_angle += 1.0
            
        else:
            # Render Normal untuk Mode Lain (No Hands, Emoji, Gembok)
            glPushMatrix()
            if current_status == "ABSTRAK":
                glRotatef(0, 0.0, 1.0, 0.0) 
            else:
                glRotatef(rotation_angle, 0.0, 1.0, 0.0)
                glRotatef(15, 1.0, 0.0, 0.2)
                
            glBegin(GL_POINTS)
            glColor4f(*particle_color)
            for i in range(NUM_PARTICLES):
                glVertex3f(current_pos[i, 0], current_pos[i, 1], current_pos[i, 2])
            glEnd()
            glPopMatrix()
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
