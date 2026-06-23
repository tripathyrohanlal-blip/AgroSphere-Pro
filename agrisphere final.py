"""
AGROSPHERE 1.0.0
A Brand New Agricultural Intelligence System
Powered by Tripathy Agrotech Startup Pvt. Ltd.
Founder: Rohan Lal Tripathy
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import math
import random
import json
import os
import hashlib
from datetime import datetime
import threading
import time

# --- CONSTANTS ---
VERSION = "1.0.0"
STARTUP_NAME = "Tripathy Agrotech Startup Pvt. Ltd."
FOUNDER = "Rohan Lal Tripathy"
LOCATION = "Bhubaneswar, Odisha, India"
COORDINATES = {"lat": 20.2961, "lon": 85.8245}

# --- THEME ---
BG_COLOR = "#0a0e1a"
STAR_COLOR = "#ffffff"
GLOBE_COLOR = "#00ff88"
LAND_COLOR = "#1a4f2a"
TEXT_COLOR = "#00ff88"
ACCENT_COLOR = "#ffaa44"
FONT_FAMILY = "Times New Roman"

# --- DATA FILES ---
USER_FILE = "agrosphere_users.json"
HISTORY_FILE = "agrosphere_history.json"

def load_json(file, default):
    if os.path.exists(file):
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except:
            return default
    return default

def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- ANIMATION: STAR FIELD ---
class StarField:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.stars = []
        for _ in range(250):
            x = random.randint(0, width)
            y = random.randint(0, height)
            size = random.randint(1, 3)
            brightness = random.randint(100, 255)
            color = f"#{brightness:02x}{brightness:02x}{brightness:02x}"
            star = canvas.create_oval(x, y, x + size, y + size, fill=color, outline=color)
            self.stars.append({
                'id': star,
                'x': x,
                'y': y,
                'size': size,
                'speed': random.uniform(0.1, 0.6)
            })
        self.animate()
    
    def animate(self):
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > self.height:
                star['y'] = 0
                star['x'] = random.randint(0, self.width)
            self.canvas.coords(star['id'], star['x'], star['y'], 
                               star['x'] + star['size'], star['y'] + star['size'])
        self.canvas.after(50, self.animate)

# --- ANIMATION: ROTATING GLOBE WITH INDIA ---
class RotatingGlobe:
    def __init__(self, canvas, x, y, radius=90):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = radius
        self.angle = 0
        self.rotation_speed = 0.02
        
        # Globe base (ocean)
        self.globe = canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                                        outline=GLOBE_COLOR, width=2, fill="#0a2a1a")
        
        # India outline (simplified)
        self.india_points = []
        india_shape = [
            (-15, -40), (-5, -45), (10, -35), (20, -20), (25, -5),
            (20, 10), (15, 20), (5, 25), (-5, 30), (-15, 25),
            (-25, 15), (-30, 0), (-25, -15), (-20, -30)
        ]
        for px, py in india_shape:
            self.india_points.append(x + px)
            self.india_points.append(y + py)
        self.india = canvas.create_polygon(self.india_points, fill=LAND_COLOR, outline=LAND_COLOR)
        
        # Small neighboring landmasses
        self.lands = []
        land_shapes = [
            [(-40, -30), (-35, -25), (-40, -20), (-45, -25)],
            [(30, -10), (40, -15), (45, -5), (35, 0)],
            [(-30, 30), (-20, 35), (-25, 40), (-35, 35)],
            [(30, 20), (40, 25), (45, 35), (35, 30)]
        ]
        for shape in land_shapes:
            points = []
            for px, py in shape:
                points.append(x + px)
                points.append(y + py)
            land = canvas.create_polygon(points, fill="#2a5a2a", outline="#2a5a2a")
            self.lands.append(land)
        
        # India label
        self.label = canvas.create_text(x, y + radius + 30, text="🇮🇳 INDIA", 
                                        fill=ACCENT_COLOR, font=(FONT_FAMILY, 12, "bold"))
        
        # Founder location marker (pulsing red dot at Bhubaneswar)
        self.marker = canvas.create_oval(x - 8, y - 8, x + 8, y + 8, fill="#ff4444", outline="#ff4444")
        self.marker_pulse = 0
        
        # Location label
        self.location_label = canvas.create_text(x + 35, y - 10, text="📍 Bhubaneswar", 
                                                  fill="#ffaa44", font=(FONT_FAMILY, 9))
        
        # Animate rotation
        self.animate()
    
    def animate(self):
        # Rotate India points
        self.angle += self.rotation_speed
        cos_a = math.cos(self.angle)
        sin_a = math.sin(self.angle)
        
        new_points = []
        for i in range(0, len(self.india_points), 2):
            px = self.india_points[i] - self.x
            py = self.india_points[i+1] - self.y
            rx = px * cos_a - py * sin_a
            ry = px * sin_a + py * cos_a
            new_points.append(self.x + rx)
            new_points.append(self.y + ry)
        self.canvas.coords(self.india, *new_points)
        
        # Rotate land patches
        for land in self.lands:
            pts = self.canvas.coords(land)
            new_pts = []
            for i in range(0, len(pts), 2):
                px = pts[i] - self.x
                py = pts[i+1] - self.y
                rx = px * cos_a - py * sin_a
                ry = px * sin_a + py * cos_a
                new_pts.append(self.x + rx)
                new_pts.append(self.y + ry)
            self.canvas.coords(land, *new_pts)
        
        # Pulse marker
        self.marker_pulse += 0.05
        pulse = 8 + 3 * math.sin(self.marker_pulse)
        self.canvas.coords(self.marker, self.x - pulse, self.y - pulse,
                           self.x + pulse, self.y + pulse)
        
        self.canvas.after(30, self.animate)

# --- MAIN APPLICATION ---
class AgroSphere:
    def __init__(self, root):
        self.root = root
        self.root.title("AGROSPHERE 1.0.0 — Tripathy Agrotech")
        self.root.geometry("1400x850")
        self.root.configure(bg=BG_COLOR)
        
        self.users = load_json(USER_FILE, {})
        self.history = load_json(HISTORY_FILE, {})
        self.current_user = None
        self.is_admin = False
        self.farm_data = {'ph': 7.0, 'moisture': 50, 'temp': 25, 'nitrogen': 20, 'phosphorus': 15, 'potassium': 20}
        
        self.show_splash()
    
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def show_splash(self):
        self.clear_screen()
        
        canvas = tk.Canvas(self.root, bg=BG_COLOR, highlightthickness=0)
        canvas.pack(expand=True, fill='both')
        
        # Stars
        star_field = StarField(canvas, 1400, 850)
        
        # Rotating Globe with India
        globe = RotatingGlobe(canvas, 380, 380, 100)
        
        # Founder Location
        canvas.create_text(750, 180, text="🏠 FOUNDER LOCATION", fill=ACCENT_COLOR,
                           font=(FONT_FAMILY, 14, "bold"))
        canvas.create_text(750, 210, text=f"{LOCATION}", fill=TEXT_COLOR,
                           font=(FONT_FAMILY, 12))
        canvas.create_text(750, 240, text=f"🌍 {COORDINATES['lat']}°N, {COORDINATES['lon']}°E",
                           fill="#888888", font=(FONT_FAMILY, 10))
        
        # Startup Name
        canvas.create_text(750, 300, text=STARTUP_NAME, fill=ACCENT_COLOR,
                           font=(FONT_FAMILY, 18, "bold"))
        canvas.create_text(750, 330, text=f"Founder: {FOUNDER}", fill=TEXT_COLOR,
                           font=(FONT_FAMILY, 12))
        
        # Title
        canvas.create_text(750, 400, text="AGROSPHERE", fill=TEXT_COLOR,
                           font=(FONT_FAMILY, 40, "bold"))
        canvas.create_text(750, 440, text="The World's Agricultural Intelligence System",
                           fill="#888888", font=(FONT_FAMILY, 14))
        canvas.create_text(750, 470, text=f"Version {VERSION}", fill="#666666",
                           font=(FONT_FAMILY, 10))
        
        # Animated tagline
        self.tagline_text = canvas.create_text(750, 520, text="", fill=ACCENT_COLOR,
                                                font=(FONT_FAMILY, 12, "italic"))
        self.tagline_index = 0
        self.taglines = [
            "🌾 Serving farmers across the globe",
            "🌱 Innovation rooted in tradition",
            "🚀 Powered by Tripathy Agrotech",
            "🌍 One mission. One family. One future.",
            "🧅 From Odisha to the world",
            "🇮🇳 Made in India. For the world."
        ]
        self.animate_tagline(canvas)
        
        # Buttons
        btn_frame = tk.Frame(canvas, bg=BG_COLOR)
        btn_frame.place(relx=0.5, rely=0.72, anchor='center')
        
        tk.Button(btn_frame, text="🚀 Enter AgroSphere", command=self.show_login,
                  bg='#1a4f2a', fg='white', font=(FONT_FAMILY, 14, "bold"),
                  padx=30, pady=12, bd=0, relief='flat',
                  cursor='hand2').pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="📖 About Startup", 
                  command=lambda: self.show_about(canvas),
                  bg='#2a2a2a', fg=TEXT_COLOR, font=(FONT_FAMILY, 12),
                  padx=20, pady=10, bd=0, relief='flat',
                  cursor='hand2').pack(side=tk.LEFT, padx=10)
        
        # Footer
        canvas.create_text(750, 800, text=f"© 2026 {STARTUP_NAME}",
                           fill="#333333", font=(FONT_FAMILY, 9))
        
        # Store references
        self.canvas = canvas
        self.globe = globe
    
    def animate_tagline(self, canvas):
        tagline = self.taglines[self.tagline_index % len(self.taglines)]
        canvas.itemconfig(self.tagline_text, text=tagline)
        self.tagline_index += 1
        canvas.after(3000, lambda: self.animate_tagline(canvas))
    
    def show_about(self, canvas):
        about_text = f"""
        🌾 AGROSPHERE 1.0.0
        
        {STARTUP_NAME}
        
        Founder: {FOUNDER}
        Location: {LOCATION}
        
        Mission: To serve farmers with intelligent,
        accessible, and affordable agricultural technology.
        
        Vision: A world where every farmer has the
        tools to thrive, regardless of their resources.
        
        Core Values:
        • Innovation
        • Integrity
        • Service
        • Sustainability
        
        This app is a gift to farmers everywhere.
        Free. Forever.
        """
        
        popup = tk.Toplevel(self.root)
        popup.title("About AgroSphere")
        popup.geometry("500x500")
        popup.configure(bg=BG_COLOR)
        popup.transient(self.root)
        popup.grab_set()
        
        text = scrolledtext.ScrolledText(popup, bg=BG_COLOR, fg=TEXT_COLOR,
                                          font=(FONT_FAMILY, 12), wrap=tk.WORD,
                                          bd=0, highlightthickness=0)
        text.pack(expand=True, fill='both', padx=20, pady=20)
        text.insert('1.0', about_text)
        text.config(state='disabled')
        
        tk.Button(popup, text="Close", command=popup.destroy,
                  bg='#1a4f2a', fg='white', font=(FONT_FAMILY, 12),
                  padx=20, pady=8).pack(pady=10)
    
    # --- LOGIN SYSTEM ---
    def show_login(self):
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(expand=True, fill='both')
        
        canvas = tk.Canvas(main_frame, bg=BG_COLOR, highlightthickness=0)
        canvas.pack(expand=True, fill='both')
        
        # Stars
        star_field = StarField(canvas, 1400, 850)
        
        # Title
        canvas.create_text(700, 80, text="🌍 AGROSPHERE", fill=TEXT_COLOR,
                           font=(FONT_FAMILY, 34, "bold"))
        canvas.create_text(700, 120, text="Login to access the agricultural intelligence system",
                           fill="#888888", font=(FONT_FAMILY, 14))
        
        # Login Frame
        login_frame = tk.Frame(canvas, bg='#111522', bd=2, relief=tk.GROOVE)
        login_frame.place(relx=0.5, rely=0.45, anchor='center')
        
        tk.Label(login_frame, text="🔐 LOGIN", font=(FONT_FAMILY, 18, "bold"),
                 bg='#111522', fg=TEXT_COLOR).pack(pady=15)
        
        tk.Label(login_frame, text="Username", bg='#111522', fg='#888888',
                 font=(FONT_FAMILY, 12)).pack(pady=5)
        self.username_entry = tk.Entry(login_frame, width=30, bg='#1a1e2a',
                                        fg=TEXT_COLOR, font=(FONT_FAMILY, 14),
                                        insertbackground=TEXT_COLOR)
        self.username_entry.pack(pady=5)
        
        tk.Label(login_frame, text="Password", bg='#111522', fg='#888888',
                 font=(FONT_FAMILY, 12)).pack(pady=5)
        self.password_entry = tk.Entry(login_frame, width=30, bg='#1a1e2a',
                                        fg=TEXT_COLOR, font=(FONT_FAMILY, 14),
                                        show="*", insertbackground=TEXT_COLOR)
        self.password_entry.pack(pady=5)
        
        btn_frame = tk.Frame(login_frame, bg='#111522')
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Login", command=self.login,
                  bg='#1a4f2a', fg='white', width=12, height=2,
                  font=(FONT_FAMILY, 12)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Register", command=self.show_register,
                  bg='#2a2a2a', fg=TEXT_COLOR, width=12, height=2,
                  font=(FONT_FAMILY, 12)).pack(side=tk.LEFT, padx=5)
        
        self.status_label = canvas.create_text(700, 500, text="", fill='red',
                                                font=(FONT_FAMILY, 12))
        
        # Footer
        canvas.create_text(700, 800, text=f"© 2026 {STARTUP_NAME}",
                           fill="#333333", font=(FONT_FAMILY, 9))
        
        self.canvas = canvas
    
    def show_register(self):
        self.clear_screen()
        
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(expand=True, fill='both')
        
        canvas = tk.Canvas(main_frame, bg=BG_COLOR, highlightthickness=0)
        canvas.pack(expand=True, fill='both')
        
        star_field = StarField(canvas, 1400, 850)
        
        canvas.create_text(700, 60, text="🌱 CREATE ACCOUNT", fill=TEXT_COLOR,
                           font=(FONT_FAMILY, 28, "bold"))
        canvas.create_text(700, 100, text="Join the Tripathy Agrotech family",
                           fill="#888888", font=(FONT_FAMILY, 14))
        
        reg_frame = tk.Frame(canvas, bg='#111522', bd=2, relief=tk.GROOVE)
        reg_frame.place(relx=0.5, rely=0.45, anchor='center')
        
        tk.Label(reg_frame, text="📝 REGISTER", font=(FONT_FAMILY, 16, "bold"),
                 bg='#111522', fg=TEXT_COLOR).pack(pady=10)
        
        fields = [("👤 Username", "reg_username"), ("🔒 Password", "reg_password"),
                  ("🔑 Confirm", "reg_confirm"), ("📞 Phone", "reg_phone"),
                  ("📍 Village", "reg_village")]
        self.reg_entries = {}
        for label, key in fields:
            tk.Label(reg_frame, text=label, bg='#111522', fg='#888888',
                     font=(FONT_FAMILY, 12)).pack(pady=3)
            entry = tk.Entry(reg_frame, width=30, bg='#1a1e2a',
                              fg=TEXT_COLOR, font=(FONT_FAMILY, 12),
                              insertbackground=TEXT_COLOR)
            if 'password' in key or key == 'reg_confirm':
                entry.config(show="*")
            entry.pack(pady=3)
            self.reg_entries[key] = entry
        
        btn_frame = tk.Frame(reg_frame, bg='#111522')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Register", command=self.register,
                  bg='#1a4f2a', fg='white', width=12, height=2,
                  font=(FONT_FAMILY, 12)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Back", command=self.show_login,
                  bg='#2a2a2a', fg=TEXT_COLOR, width=12, height=2,
                  font=(FONT_FAMILY, 12)).pack(side=tk.LEFT, padx=5)
        
        self.reg_status = canvas.create_text(700, 550, text="", fill='green',
                                              font=(FONT_FAMILY, 12))
        
        canvas.create_text(700, 800, text=f"© 2026 {STARTUP_NAME}",
                           fill="#333333", font=(FONT_FAMILY, 9))
    
    def register(self):
        username = self.reg_entries['reg_username'].get().strip()
        password = self.reg_entries['reg_password'].get().strip()
        confirm = self.reg_entries['reg_confirm'].get().strip()
        phone = self.reg_entries['reg_phone'].get().strip()
        village = self.reg_entries['reg_village'].get().strip()
        
        if not all([username, password, confirm, phone]):
            self.canvas.itemconfig(self.reg_status, text="❌ Fill all fields", fill='red')
            return
        if username in self.users:
            self.canvas.itemconfig(self.reg_status, text="❌ Username exists", fill='red')
            return
        if password != confirm:
            self.canvas.itemconfig(self.reg_status, text="❌ Passwords don't match", fill='red')
            return
        if len(password) < 4:
            self.canvas.itemconfig(self.reg_status, text="❌ Password too short", fill='red')
            return
        if len(phone) < 10:
            self.canvas.itemconfig(self.reg_status, text="❌ Valid phone required", fill='red')
            return
        
        self.users[username] = {
            'password': hash_password(password),
            'phone': phone,
            'village': village,
            'plan': 'free',
            'tenure': 0,
            'created': datetime.now().isoformat(),
            'loan_approved': False,
            'loan_amount': 0,
            'points': 0,
            'soil_checks': 0
        }
        save_json(USER_FILE, self.users)
        self.canvas.itemconfig(self.reg_status, text="✅ Account created! Welcome to AgroSphere.", fill='green')
        self.root.after(1500, self.show_login)
    
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            self.canvas.itemconfig(self.status_label, text="❌ Fill all fields", fill='red')
            return
        
        if username == 'rohan' and password == '1234':
            self.current_user = 'rohan'
            self.is_admin = True
            self.show_admin_dashboard()
            return
        
        if username in self.users and self.users[username]['password'] == hash_password(password):
            self.current_user = username
            self.is_admin = False
            self.show_user_dashboard()
            return
        
        self.canvas.itemconfig(self.status_label, text="❌ Invalid credentials", fill='red')
    
    # --- ADMIN DASHBOARD ---
    def show_admin_dashboard(self):
        self.clear_screen()
        
        top_frame = tk.Frame(self.root, bg='#1a4f2a', height=70)
        top_frame.pack(fill='x', side='top')
        top_frame.pack_propagate(False)
        
        tk.Label(top_frame, text="🌍 AGROSPHERE — ADMIN", font=(FONT_FAMILY, 22, "bold"),
                 bg='#1a4f2a', fg='#ffaa44').pack(side='left', padx=20)
        tk.Label(top_frame, text="Logged in as: ROHAN", font=(FONT_FAMILY, 14),
                 bg='#1a4f2a', fg='#c8e6c9').pack(side='left', padx=20)
        tk.Button(top_frame, text="Logout", command=self.logout,
                  bg='#a33', fg='white', width=12, font=(FONT_FAMILY, 10)).pack(side='right', padx=20)
        
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill='both')
        
        tabs = [
            ("👥 Farmers", self.build_admin_users),
            ("📋 Requests", self.build_admin_requests),
            ("📜 Activity", self.build_admin_activity),
            ("📊 Stats", self.build_admin_stats)
        ]
        
        for tab_name, build_func in tabs:
            tab = tk.Frame(notebook, bg='#111522')
            notebook.add(tab, text=tab_name)
            build_func(tab)
        
        tk.Label(self.root, text=f"© 2026 {STARTUP_NAME}", bg=BG_COLOR, fg='#333',
                 font=(FONT_FAMILY, 8)).pack(side=tk.BOTTOM, pady=5)
    
    def build_admin_users(self, parent):
        tk.Label(parent, text="ALL REGISTERED FARMERS", font=(FONT_FAMILY, 16, "bold"),
                 bg='#111522', fg=TEXT_COLOR).pack(pady=10)
        
        cols = ('Username', 'Village', 'Phone', 'Plan', 'Tenure', 'Loan', 'Checks')
        tree = ttk.Treeview(parent, columns=cols, show='headings', height=15)
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120)
        
        scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        for username, data in self.users.items():
            tree.insert('', tk.END, values=(
                username,
                data.get('village', 'N/A'),
                data.get('phone', 'N/A'),
                data.get('plan', 'free').upper(),
                f"{data.get('tenure', 0)}y",
                "✅" if data.get('loan_approved') else "❌",
                data.get('soil_checks', 0)
            ))
    
    def build_admin_requests(self, parent):
        tk.Label(parent, text="PENDING REQUESTS", font=(FONT_FAMILY, 16, "bold"),
                 bg='#111522', fg=ACCENT_COLOR).pack(pady=10)
        tk.Label(parent, text="No pending requests at this time.", bg='#111522', fg='#888888',
                 font=(FONT_FAMILY, 14)).pack(pady=50)
    
    def build_admin_activity(self, parent):
        tk.Label(parent, text="FARMER ACTIVITY LOG", font=(FONT_FAMILY, 16, "bold"),
                 bg='#111522', fg=TEXT_COLOR).pack(pady=10)
        
        log = scrolledtext.ScrolledText(parent, height=20, bg='#111522', fg=TEXT_COLOR,
                                         font=(FONT_FAMILY, 10))
        log.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        log.insert(tk.END, "=== FARMER ACTIVITY LOG ===\n\n")
        for username, acts in self.history.items():
            log.insert(tk.END, f"👤 {username}\n")
            for act in acts[-15:]:
                log.insert(tk.END, f"  • {act}\n")
            log.insert(tk.END, "\n")
        log.config(state='disabled')
    
    def build_admin_stats(self, parent):
        tk.Label(parent, text="SYSTEM STATISTICS", font=(FONT_FAMILY, 16, "bold"),
                 bg='#111522', fg=TEXT_COLOR).pack(pady=10)
        
        frame = tk.Frame(parent, bg='#111522')
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        total = len(self.users)
        paid = sum(1 for u in self.users.values() if u.get('plan') != 'free')
        loans = sum(1 for u in self.users.values() if u.get('loan_approved'))
        checks = sum(u.get('soil_checks', 0) for u in self.users.values())
        
        stats = [
            f"🌾 Total Farmers: {total}",
            f"📈 Paid Plan Farmers: {paid}",
            f"💰 Loans Approved: {loans}",
            f"🔬 Soil Checks Done: {checks}",
            f"🌍 Powered by: {STARTUP_NAME}",
            f"🧑‍🌾 Founder: {FOUNDER}",
            f"📦 Version: {VERSION}"
        ]
        
        for stat in stats:
            tk.Label(frame, text=stat, bg='#111522', fg=TEXT_COLOR,
                     font=(FONT_FAMILY, 16)).pack(pady=8)
    
    # --- USER DASHBOARD ---
    def show_user_dashboard(self):
        self.clear_screen()
        
        user_data = self.users.get(self.current_user, {})
        plan = user_data.get('plan', 'free').upper()
        tenure = user_data.get('tenure', 0)
        points = user_data.get('points', 0)
        loan_status = "✅ Approved" if user_data.get('loan_approved') else "❌ Not Applied"
        soil_checks = user_data.get('soil_checks', 0)
        village = user_data.get('village', 'N/A')
        
        top_frame = tk.Frame(self.root, bg='#1a4f2a', height=70)
        top_frame.pack(fill='x', side='top')
        top_frame.pack_propagate(False)
        
        tk.Label(top_frame, text="🌍 AGROSPHERE", font=(FONT_FAMILY, 20, "bold"),
                 bg='#1a4f2a', fg='white').pack(side='left', padx=20)
        tk.Label(top_frame, text=f"👤 {self.current_user}", font=(FONT_FAMILY, 12),
                 bg='#1a4f2a', fg='#c8e6c9').pack(side='left', padx=20)
        tk.Label(top_frame, text=f"📍 {village}", font=(FONT_FAMILY, 12),
                 bg='#1a4f2a', fg=ACCENT_COLOR).pack(side='left', padx=20)
        tk.Label(top_frame, text=f"📋 {plan}", font=(FONT_FAMILY, 12),
                 bg='#1a4f2a', fg=ACCENT_COLOR).pack(side='left', padx=20)
        tk.Label(top_frame, text=f"🔬 {soil_checks} checks", font=(FONT_FAMILY, 12),
                 bg='#1a4f2a', fg='#44ffff').pack(side='left', padx=20)
        tk.Button(top_frame, text="Logout", command=self.logout,
                  bg='#a33', fg='white', width=10, font=(FONT_FAMILY, 10)).pack(side='right', padx=10)
        
        main_frame = tk.Frame(self.root, bg=BG_COLOR)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(expand=True, fill='both')
        
        tabs = [
            ("🌱 Farm", self.build_farmer_farm),
            ("👤 My Account", self.build_farmer_account),
            ("📊 Analytics", self.build_farmer_analytics)
        ]
        
        for tab_name, build_func in tabs:
            tab = tk.Frame(notebook, bg='#111522')
            notebook.add(tab, text=tab_name)
            build_func(tab)
        
        tk.Label(self.root, text=f"© 2026 {STARTUP_NAME} | Every farmer matters.",
                 bg=BG_COLOR, fg='#333', font=(FONT_FAMILY, 8)).pack(side=tk.BOTTOM, pady=5)
    
    def build_farmer_farm(self, parent):
        left = tk.Frame(parent, bg='#111522', bd=2, relief=tk.GROOVE)
        left.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        
        tk.Label(left, text="🌾 FARM DATA", font=(FONT_FAMILY, 14, "bold"),
                 bg='#111522', fg=TEXT_COLOR).pack(pady=10)
        tk.Label(left, text="Enter your soil data. Get instant advice.",
                 bg='#111522', fg='#888888', font=(FONT_FAMILY, 10)).pack(pady=5)
        
        fields = [("pH", "ph"), ("Moisture %", "moisture"), ("Temp °C", "temp"),
                  ("Nitrogen", "nitrogen"), ("Phosphorus", "phosphorus"), ("Potassium", "potassium")]
        self.entries = {}
        for label, key in fields:
            tk.Label(left, text=label, bg='#111522', fg='#888888',
                     font=(FONT_FAMILY, 12)).pack(pady=2)
            entry = tk.Entry(left, width=25, bg='#1a1e2a', fg=TEXT_COLOR,
                              font=(FONT_FAMILY, 12), insertbackground=TEXT_COLOR)
            entry.insert(0, str(self.farm_data.get(key, '')))
            entry.pack(pady=2)
            self.entries[key] = entry
        
        btn_frame = tk.Frame(left, bg='#111522')
        btn_frame.pack(pady=10)
        
        btn_commands = [
            ("🔬 Analyze Soil", self.analyze_soil),
            ("🌾 Recommend Crops", self.recommend_crops),
            ("🔮 Quantum Predict", self.quantum_predict),
            ("🧬 Soil DNA", self.soil_dna),
            ("🦠 Disease Predict", self.disease_predict),
            ("📊 Yield Predict", self.yield_predict)
        ]
        
        for text, cmd in btn_commands:
            tk.Button(btn_frame, text=text, command=cmd,
                      bg='#1a4f2a', fg='white', width=18,
                      font=(FONT_FAMILY, 10)).pack(pady=2)
        
        self.result_text = scrolledtext.ScrolledText(left, height=12, width=30,
                                                      bg='#111522', fg=TEXT_COLOR,
                                                      font=(FONT_FAMILY, 10))
        self.result_text.pack(padx=10, pady=10, fill='both', expand=True)
        self.result_text.config(state='disabled')
        
        right = tk.Frame(parent, bg='#111522', bd=2, relief=tk.GROOVE)
        right.pack(side=tk.LEFT, fill='both', expand=True, padx=5, pady=5)
        
        tk.Label(right, text="⚡ QUICK ACTIONS", font=(FONT_FAMILY, 14, "bold"),
                 bg='#111522', fg=ACCENT_COLOR).pack(pady=10)
        
        quick_actions = [
            ("☁️ Weather Forecast", self.weather_forecast),
            ("🏪 Market Prices", self.market_prices),
            ("🏛️ Government Schemes", self.show_schemes),
            ("💧 Irrigation Guide", self.irrigation_guide),
            ("🌿 Soil Health", self.soil_health),
            ("🔄 Crop Rotation", self.crop_rotation),
            ("🐛 Pest Control", self.pest_control),
            ("💰 Profit Calculator", self.profit_calculator),
            ("📋 Loan Eligibility", self.loan_eligibility),
            ("📦 Subscription Plans", self.show_plans)
        ]
        
        for text, cmd in quick_actions:
            tk.Button(right, text=text, command=cmd,
                      bg='#2a6f2a', fg='white', width=25, height=2,
                      font=(FONT_FAMILY, 10)).pack(pady=3)
        
        self.quick_result = scrolledtext.ScrolledText(right, height=12, width=30,
                                                       bg='#111522', fg=TEXT_COLOR,
                                                       font=(FONT_FAMILY, 10))
        self.quick_result.pack(padx=10, pady=10, fill='both', expand=True)
        self.quick_result.config(state='disabled')
    
    def build_farmer_account(self, parent):
        user_data = self.users.get(self.current_user, {})
        
        frame = tk.Frame(parent, bg='#111522')
        frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(frame, text="👤 MY ACCOUNT", font=(FONT_FAMILY, 18, "bold"),
                 bg='#111522', fg=TEXT_COLOR).pack(pady=10)
        
        fields = [
            f"👤 Username: {self.current_user}",
            f"📞 Phone: {user_data.get('phone', 'N/A')}",
            f"📍 Village: {user_data.get('village', 'N/A')}",
            f"📋 Plan: {user_data.get('plan', 'free').upper()}",
            f"⏳ Tenure: {user_data.get('tenure', 0)} years",
            f"⭐ Points: {user_data.get('points', 0)}",
            f"💰 Loan: {'✅ Approved' if user_data.get('loan_approved') else '❌ Not Applied'}",
            f"🏦 Loan Amount: ₹{user_data.get('loan_amount', 0):,}",
            f"🔬 Soil Checks: {user_data.get('soil_checks', 0)}",
            f"📅 Joined: {user_data.get('created', 'N/A')[:10]}"
        ]
        
        for field in fields:
            tk.Label(frame, text=field, bg='#111522', fg=ACCENT_COLOR,
                     font=(FONT_FAMILY, 14)).pack(pady=5)
        
        tk.Label(frame, text="\n--- ACTIONS ---", bg='#111522', fg='#444',
                 font=(FONT_FAMILY, 12)).pack(pady=10)
        
        action_frame = tk.Frame(frame, bg='#111522')
        action_frame.pack(pady=10)
        
        tk.Label(action_frame, text="Request Plan Upgrade:", bg='#111522', fg='#888888',
                 font=(FONT_FAMILY, 12)).pack()
        self.plan_var = tk.StringVar(value='monthly')
        plan_menu = ttk.Combobox(action_frame, textvariable=self.plan_var,
                                  values=['monthly', 'quarterly', 'annual', '3_year', '5_year', 'lifetime'],
                                  width=15)
        plan_menu.pack(pady=5)
        tk.Button(action_frame, text="📤 Request Upgrade", command=self.request_plan_upgrade,
                  bg='#2a6f2a', fg='white', width=20,
                  font=(FONT_FAMILY, 10)).pack(pady=5)
        
        tk.Label(action_frame, text="Apply for Loan:", bg='#111522', fg='#888888',
                 font=(FONT_FAMILY, 12)).pack(pady=5)
        self.loan_amount_entry = tk.Entry(action_frame, width=20, bg='#1a1e2a',
                                           fg=TEXT_COLOR, font=(FONT_FAMILY, 12),
                                           insertbackground=TEXT_COLOR)
        self.loan_amount_entry.pack(pady=5)
        tk.Button(action_frame, text="💰 Apply for Loan", command=self.request_loan,
                  bg='#1a4f2a', fg='white', width=20,
                  font=(FONT_FAMILY, 10)).pack(pady=5)
        
        self.user_status = tk.Label(frame, text="", bg='#111522', fg='green',
                                    font=(FONT_FAMILY, 10))
        self.user_status.pack(pady=10)
    
    def build_farmer_analytics(self, parent):
        tk.Label(parent, text="📊 FARM ANALYTICS", font=(FONT_FAMILY, 16, "bold"),
                 bg='#111522', fg=TEXT_COLOR).pack(pady=10)
        
        frame = tk.Frame(parent, bg='#111522')
        frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        ph = self.farm_data.get('ph', 7.0)
        moisture = self.farm_data.get('moisture', 50)
        temp = self.farm_data.get('temp', 25)
        nitrogen = self.farm_data.get('nitrogen', 20)
        phosphorus = self.farm_data.get('phosphorus', 15)
        potassium = self.farm_data.get('potassium', 20)
        
        health = 100
        if ph < 5.5 or ph > 7.5:
            health -= 30
        if moisture < 25 or moisture > 80:
            health -= 25
        if temp < 15 or temp > 35:
            health -= 10
        if nitrogen < 10:
            health -= 10
        if phosphorus < 8:
            health -= 10
        if potassium < 10:
            health -= 10
        health = max(0, health)
        
        analytics = [
            f"🌱 Soil Health: {health}/100",
            f"🧪 pH: {ph} ({'Optimal' if 6.0 <= ph <= 7.0 else 'Needs Adjustment'})",
            f"💧 Moisture: {moisture}% ({'Ideal' if 40 <= moisture <= 60 else 'Needs Attention'})",
            f"🌡️ Temp: {temp}°C ({'Ideal' if 20 <= temp <= 30 else 'Needs Attention'})",
            f"🧬 Nitrogen: {nitrogen} ppm ({'Adequate' if nitrogen >= 15 else 'Low'})",
            f"🧬 Phosphorus: {phosphorus} ppm ({'Adequate' if phosphorus >= 12 else 'Low'})",
            f"🧬 Potassium: {potassium} ppm ({'Adequate' if potassium >= 15 else 'Low'})",
            f"🌾 Recommended: {', '.join(['Rice', 'Wheat', 'Maize'][:random.randint(2, 4)])}",
            f"📈 Yield: {random.randint(20, 45)} q/acre",
            f"💰 Profit: ₹{random.randint(25000, 75000):,}/acre"
        ]
        
        for line in analytics:
            tk.Label(frame, text=line, bg='#111522', fg='#44ffff',
                     font=(FONT_FAMILY, 14)).pack(pady=5)
    
    # --- FEATURE FUNCTIONS ---
    def update_result(self, text, target='main'):
        widget = self.result_text if target == 'main' else self.quick_result
        widget.config(state='normal')
        widget.delete('1.0', tk.END)
        widget.insert('1.0', text)
        widget.config(state='disabled')
        
        if self.current_user and not self.is_admin:
            if self.current_user not in self.history:
                self.history[self.current_user] = []
            self.history[self.current_user].append(f"{text[:50]}...")
            save_json(HISTORY_FILE, self.history)
    
    def analyze_soil(self):
        try:
            ph = float(self.entries['ph'].get()) if self.entries['ph'].get() else 7.0
            moisture = float(self.entries['moisture'].get()) if self.entries['moisture'].get() else 50
            temp = float(self.entries['temp'].get()) if self.entries['temp'].get() else 25
            nitrogen = float(self.entries['nitrogen'].get()) if self.entries['nitrogen'].get() else 20
            phosphorus = float(self.entries['phosphorus'].get()) if self.entries['phosphorus'].get() else 15
            potassium = float(self.entries['potassium'].get()) if self.entries['potassium'].get() else 20
            
            self.farm_data = {'ph': ph, 'moisture': moisture, 'temp': temp,
                              'nitrogen': nitrogen, 'phosphorus': phosphorus, 'potassium': potassium}
            
            health = 100
            alerts = []
            if ph < 5.5:
                alerts.append("pH too acidic. Add lime.")
                health -= 30
            elif ph > 7.5:
                alerts.append("pH too alkaline. Add sulfur.")
                health -= 30
            if moisture < 25:
                alerts.append("Moisture too low. Irrigate.")
                health -= 25
            elif moisture > 80:
                alerts.append("Moisture too high. Risk of rot.")
                health -= 20
            if nitrogen < 10:
                alerts.append("Nitrogen low. Add compost.")
                health -= 10
            if phosphorus < 8:
                alerts.append("Phosphorus low. Add bone meal.")
                health -= 10
            if potassium < 10:
                alerts.append("Potassium low. Add wood ash.")
                health -= 10
            
            status = "EXCELLENT" if health >= 80 else "GOOD" if health >= 60 else "FAIR" if health >= 40 else "POOR"
            
            result = f"🔬 SOIL ANALYSIS\n{'='*40}\n"
            result += f"pH: {ph} | Moisture: {moisture}% | Temp: {temp}°C\n"
            result += f"N: {nitrogen} | P: {phosphorus} | K: {potassium}\n\n"
            result += f"Health Score: {health}/100\n"
            result += f"Status: {status}\n\n"
            result += "Alerts:\n"
            for alert in alerts:
                result += f"  • {alert}\n"
            
            self.update_result(result, 'main')
            
            if self.current_user in self.users:
                self.users[self.current_user]['soil_checks'] = self.users[self.current_user].get('soil_checks', 0) + 1
                self.users[self.current_user]['points'] = self.users[self.current_user].get('points', 0) + 5
                save_json(USER_FILE, self.users)
                
        except ValueError:
            self.update_result("ERROR: Enter valid numbers.", 'main')
    
    def recommend_crops(self):
        ph = self.farm_data.get('ph', 7.0)
        moisture = self.farm_data.get('moisture', 50)
        temp = self.farm_data.get('temp', 25)
        
        crops = []
        if 6.0 <= ph <= 7.5:
            if moisture >= 60:
                crops.append("🌾 Rice")
            if moisture >= 40:
                crops.append("🌽 Maize")
        if 6.5 <= ph <= 8.0:
            if moisture >= 30:
                crops.append("🌾 Wheat")
        if 5.5 <= ph <= 6.5:
            crops.append("🥔 Potato")
        if 5.0 <= ph <= 6.5:
            crops.append("🥜 Groundnut")
        if temp >= 25:
            crops.append("🌻 Sunflower")
        
        crops = list(set(crops))[:5]
        
        result = f"🌾 CROP RECOMMENDATIONS\n{'='*40}\n"
        if crops:
            for i, crop in enumerate(crops, 1):
                yield_est = random.randint(20, 45)
                result += f"{i}. {crop} — {yield_est} q/acre\n"
        else:
            result += "No recommendations. Check your inputs.\n"
        
        self.update_result(result, 'main')
    
    def quantum_predict(self):
        ph = self.farm_data.get('ph', 7.0)
        moisture = self.farm_data.get('moisture', 50)
        temp = self.farm_data.get('temp', 25)
        
        result = f"🔮 QUANTUM PREDICTION (90 Days)\n{'='*40}\n"
        for day in [0, 30, 60, 90]:
            q_noise = random.uniform(-0.3, 0.3)
            pred_ph = ph + q_noise
            pred_moisture = moisture + random.uniform(-5, 5)
            pred_temp = temp + random.uniform(-2, 2)
            result += f"Day {day}: pH {pred_ph:.1f} | Moisture {int(pred_moisture)}% | Temp {pred_temp:.1f}°C\n"
        
        self.update_result(result, 'main')
    
    def soil_dna(self):
        ph = self.farm_data.get('ph', 7.0)
        moisture = self.farm_data.get('moisture', 50)
        temp = self.farm_data.get('temp', 25)
        
        raw = f"{ph}|{moisture}|{temp}"
        dna = hashlib.sha256(raw.encode()).hexdigest()[:20]
        seq = ''.join(['ATCG'[int(dna[i:i+2], 16) % 4] for i in range(0, 20, 2)])
        
        result = f"🧬 SOIL DNA FINGERPRINT\n{'='*40}\n"
        result += f"DNA ID: {dna}\n"
        result += f"Sequence: {seq}\n"
        result += "Every soil is unique. This is yours.\n"
        self.update_result(result, 'main')
    
    def disease_predict(self):
        ph = self.farm_data.get('ph', 7.0)
        moisture = self.farm_data.get('moisture', 50)
        temp = self.farm_data.get('temp', 25)
        
        diseases = []
        if ph < 5.5:
            diseases.append("Root Rot (Fusarium)")
        if moisture > 70:
            diseases.append("Leaf Blight")
        if temp > 30:
            diseases.append("Powdery Mildew")
        if ph > 7.0 and moisture < 30:
            diseases.append("Chlorosis")
        
        result = f"🦠 DISEASE PREDICTION\n{'='*40}\n"
        if diseases:
            for d in diseases:
                result += f"Risk: {d}\n"
            result += "\nRecommendation: Monitor closely. Apply organic fungicide if needed.\n"
        else:
            result += "✅ No disease risk detected. Your crop is safe.\n"
        self.update_result(result, 'main')
    
    def yield_predict(self):
        crop = random.choice(['Rice', 'Wheat', 'Maize', 'Soybean', 'Potato'])
        base_yield = {'Rice': 2500, 'Wheat': 3000, 'Maize': 3500, 'Soybean': 2000, 'Potato': 4000}
        base = base_yield.get(crop, 2500)
        
        ph = self.farm_data.get('ph', 7.0)
        moisture = self.farm_data.get('moisture', 50)
        
        factor = 1.0
        if 6.0 <= ph <= 7.0:
            factor *= 1.2
        elif 5.5 <= ph <= 7.5:
            factor *= 1.0
        else:
            factor *= 0.7
        
        if 40 <= moisture <= 60:
            factor *= 1.15
        elif 25 <= moisture <= 75:
            factor *= 1.0
        else:
            factor *= 0.6
        
        predicted = int(base * factor * random.uniform(0.85, 1.15))
        
        result = f"📊 YIELD PREDICTOR\n{'='*40}\n"
        result += f"Crop: {crop}\n"
        result += f"Expected Yield: {predicted} kg/acre\n"
        result += f"Market Value: ₹{predicted * random.randint(20, 40):,}/acre\n"
        self.update_result(result, 'main')
    
    def weather_forecast(self):
        temp = self.farm_data.get('temp', 25)
        result = f"☁️ WEATHER FORECAST (48 Hours)\n{'='*40}\n"
        for hour in range(1, 13):
            temp_var = random.uniform(-2, 2)
            rain = "☀️" if random.random() > 0.3 else "☁️"
            result += f"Hour {hour:2}: {temp + temp_var:.1f}°C | {rain}\n"
        self.update_result(result, 'quick')
    
    def market_prices(self):
        crops = ['Rice', 'Wheat', 'Maize', 'Soybean', 'Potato', 'Sunflower']
        result = f"🏪 MARKET PRICES\n{'='*40}\n"
        for crop in crops:
            price = random.randint(1500, 5000)
            demand = random.randint(60, 95)
            result += f"{crop}: ₹{price}/q | Demand: {demand}%\n"
        self.update_result(result, 'quick')
    
    def show_schemes(self):
        schemes = [
            ("PM Kisan Samman Nidhi", "₹6,000/year"),
            ("PM Fasal Bima Yojana", "Crop insurance up to ₹2L/acre"),
            ("Soil Health Card", "Free soil testing"),
            ("PM Krishi Sinchayee", "50% irrigation subsidy"),
            ("NMSA", "Organic farming subsidy"),
            ("e-NAM", "Online trading platform"),
            ("Kisan Credit Card", "Easy credit"),
            ("NABARD Support", "Rural credit")
        ]
        result = f"🏛️ GOVERNMENT SCHEMES\n{'='*40}\n"
        for name, desc in schemes:
            result += f"• {name}: {desc}\n"
        self.update_result(result, 'quick')
    
    def irrigation_guide(self):
        moisture = self.farm_data.get('moisture', 50)
        result = f"💧 IRRIGATION GUIDE\n{'='*40}\n"
        if moisture < 25:
            result += "🔴 CRITICAL — Irrigate immediately!\n"
            result += "Water Required: 10-15 liters/sq.m\n"
        elif moisture < 40:
            result += "🟡 LOW — Schedule irrigation soon.\n"
            result += "Water Required: 5-8 liters/sq.m\n"
        elif moisture <= 60:
            result += "🟢 OPTIMAL — Maintain current schedule.\n"
            result += "Water Required: 3-5 liters/sq.m\n"
        else:
            result += "🔵 HIGH — Reduce irrigation.\n"
            result += "Water Required: 0-2 liters/sq.m\n"
        self.update_result(result, 'quick')
    
    def soil_health(self):
        ph = self.farm_data.get('ph', 7.0)
        moisture = self.farm_data.get('moisture', 50)
        health = 100
        if ph < 5.5 or ph > 7.5:
            health -= 30
        if moisture < 25 or moisture > 80:
            health -= 25
        
        result = f"🌿 SOIL HEALTH REPORT\n{'='*40}\n"
        result += f"Health: {health}/100\n"
        if health >= 80:
            result += "Status: EXCELLENT 🌟\n"
            result += "Your soil is thriving. Keep up the good work!\n"
        elif health >= 60:
            result += "Status: GOOD 👍\n"
            result += "Minor improvements can make it excellent.\n"
        elif health >= 40:
            result += "Status: FAIR ⚠️\n"
            result += "Add organic matter and monitor regularly.\n"
        else:
            result += "Status: POOR ❌\n"
            result += "Immediate action needed. Add compost and lime.\n"
        self.update_result(result, 'quick')
    
    def crop_rotation(self):
        ph = self.farm_data.get('ph', 7.0)
        result = f"🔄 CROP ROTATION PLAN\n{'='*40}\n"
        if 6.0 <= ph <= 7.0:
            result += "Season 1 (Kharif): 🌾 Rice\n"
            result += "Season 2 (Rabi): 🌾 Wheat\n"
            result += "Season 3 (Summer): 🌱 Green Manure\n"
            result += "\nBenefit: Excellent soil fertility improvement.\n"
        elif ph < 6.0:
            result += "Season 1: 🌱 Soybean (Nitrogen fixer)\n"
            result += "Season 2: 🌻 Mustard\n"
            result += "Season 3: 🌾 Millets\n"
            result += "\nBenefit: Improves acidic soil.\n"
        else:
            result += "Season 1: 🥜 Groundnut\n"
            result += "Season 2: 🌾 Sorghum\n"
            result += "Season 3: 🌻 Sunflower\n"
            result += "\nBenefit: Good for alkaline soil.\n"
        self.update_result(result, 'quick')
    
    def pest_control(self):
        strategies = [
            "🌿 Neem Oil Spray — For aphids and mites",
            "🧄 Garlic-Chili Spray — For caterpillars",
            "🦠 Bacillus Thuringiensis — For leaf-eating pests",
            "🌱 Trap Crops — Attract pests away",
            "🐞 Ladybugs — Natural aphid control"
        ]
        result = f"🐛 PEST CONTROL\n{'='*40}\n"
        for s in strategies:
            result += f"• {s}\n"
        self.update_result(result, 'quick')
    
    def profit_calculator(self):
        crop = random.choice(['Rice', 'Wheat', 'Maize', 'Potato'])
        area = random.randint(1, 5)
        yield_acre = random.randint(20, 45)
        price = random.randint(1500, 3500)
        
        total_yield = yield_acre * area
        revenue = total_yield * price
        cost = total_yield * 500
        profit = revenue - cost
        
        result = f"💰 PROFIT CALCULATOR\n{'='*40}\n"
        result += f"Crop: {crop}\nArea: {area} acres\n"
        result += f"Revenue: ₹{revenue:,}\nCost: ₹{cost:,}\n"
        result += f"Profit: ₹{profit:,}\nProfit/acre: ₹{int(profit/area):,}\n"
        self.update_result(result, 'quick')
    
    def loan_eligibility(self):
        user_data = self.users.get(self.current_user, {})
        tenure = user_data.get('tenure', 0)
        plan = user_data.get('plan', 'free')
        result = f"📋 LOAN ELIGIBILITY\n{'='*40}\n"
        if tenure >= 3 and plan != 'free':
            result += f"✅ ELIGIBLE — You have {tenure} years tenure.\n"
            result += f"Max Loan: ₹{min(50000 * tenure, 200000):,}\n"
            result += f"Interest Rate: {max(1, 5 - (tenure - 3))}%\n"
        elif plan == 'free':
            result += f"⏳ NOT ELIGIBLE — Upgrade to a paid plan for loan access.\n"
        else:
            result += f"⏳ NOT ELIGIBLE — Need 3+ years tenure.\n"
            result += f"Current tenure: {tenure} years.\n"
        self.update_result(result, 'quick')
    
    def show_plans(self):
        plans = [
            ("Free", "₹0", "All core features. Unlimited soil analysis, crop recommendations, weather, market, schemes, pest control, profit calculator."),
            ("Monthly", "₹99", "All Free + Priority support + Advanced analytics"),
            ("Quarterly", "₹249", "All Monthly + AI predictions + History access"),
            ("Annual", "₹799", "All Quarterly + Blockchain tracking + Government scheme alerts"),
            ("3 Year", "₹1,999", "All Annual + Loan eligibility + Premium support"),
            ("5 Year", "₹2,999", "All 3-Year + No-interest loan + Mentorship"),
            ("Lifetime", "₹9,999", "All features forever + Founder access + Lifetime updates")
        ]
        result = f"📦 SUBSCRIPTION PLANS\n{'='*40}\n"
        for name, price, features in plans:
            result += f"{name}: {price} — {features}\n\n"
        self.update_result(result, 'quick')
    
    def request_plan_upgrade(self):
        plan = self.plan_var.get()
        user_data = self.users.get(self.current_user, {})
        
        if user_data.get('plan') == plan:
            self.user_status.config(text=f"You're already on {plan.upper()}.", fg='#ffaa44')
            return
        
        self.user_status.config(text=f"✅ Request for {plan.upper()} sent to admin!", fg='#00ff44')
        
        if self.current_user not in self.history:
            self.history[self.current_user] = []
        self.history[self.current_user].append(f"Requested plan upgrade to {plan}")
        save_json(HISTORY_FILE, self.history)
    
    def request_loan(self):
        try:
            amount = int(self.loan_amount_entry.get())
            if amount <= 0:
                self.user_status.config(text="Enter valid amount.", fg='red')
                return
            
            user_data = self.users.get(self.current_user, {})
            tenure = user_data.get('tenure', 0)
            plan = user_data.get('plan', 'free')
            
            if tenure < 3 or plan == 'free':
                self.user_status.config(text="Need 3+ years tenure on paid plan.", fg='red')
                return
            
            self.user_status.config(text=f"✅ Loan ₹{amount:,} requested! Admin will call.", fg='#00ff44')
            
            if self.current_user not in self.history:
                self.history[self.current_user] = []
            self.history[self.current_user].append(f"Applied for loan ₹{amount:,}")
            save_json(HISTORY_FILE, self.history)
            
        except ValueError:
            self.user_status.config(text="Enter a valid number.", fg='red')
    
    def logout(self):
        self.current_user = None
        self.is_admin = False
        self.show_login()

# --- RUN ---
if __name__ == "__main__":
    root = tk.Tk()
    app = AgroSphere(root)
    root.mainloop()