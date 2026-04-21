import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import os, shutil, subprocess, time, json

class StoryGameStudio(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Story Game Studio - Polish Edition")
        self.geometry("1100x850")
        self.current_project_path = ""
        self.selected_font = "Arial"
        
        if not os.path.exists("projects"): 
            os.makedirs("projects")
        self.show_project_manager() 

    def clear_screen(self):
        for widget in self.winfo_children(): widget.destroy()

    def show_project_manager(self):
        self.clear_screen()
        ctk.CTkLabel(self, text="Story Game Studio", font=("Helvetica", 36, "bold")).pack(pady=40)
        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=20, fill="both", expand=True)
        ctk.CTkButton(frame, text="+ New Project", height=40, command=self.new_project).pack(pady=15)
        
        list_frame = ctk.CTkScrollableFrame(frame, width=500, height=350)
        list_frame.pack(pady=10)
        for p in os.listdir("projects"):
            if os.path.isdir(f"projects/{p}"):
                ctk.CTkButton(list_frame, text=f"📂 {p}", fg_color="transparent", border_width=1,
                              anchor="w", command=lambda name=p: self.open_project(name)).pack(pady=5, fill="x")

    def new_project(self):
        name = simpledialog.askstring("New Project", "Project Name:")
        if name:
            path = f"projects/{name}"
            os.makedirs(f"{path}/characters", exist_ok=True)
            os.makedirs(f"{path}/backgrounds", exist_ok=True)
            os.makedirs(f"{path}/fonts", exist_ok=True)
            os.makedirs(f"{path}/json", exist_ok=True)
            with open(f"{path}/script.txt", "w", encoding="utf-8") as f:
                f.write("// --- BASIC SCRIPT FORMATTING ---\n")
                f.write("// [BG: name] -> Changes background\n")
                f.write("// [JSON: filename] -> Triggers a JSON file\n")
                f.write("// Name: Dialogue -> Shows character and text\n\n")
                f.write("[BG: room]\nTeto: 🍜 Welcome to your new game!\n")
                f.write("[JSON: example]\nTeto: This dialogue triggered a JSON change!")
            
            example_json = {
                "box_color": [50, 0, 50],
                "text_color": [200, 255, 200],
                "sound": "none",
                "volume": 1.0
            }
            with open(f"{path}/json/example.json", "w", encoding="utf-8") as jf:
                json.dump(example_json, jf, indent=4)
                
            self.open_project(name)

    def open_project(self, name):
        self.current_project_path = os.path.abspath(f"projects/{name}")
        self.show_studio()

    def show_help(self):
        help_win = ctk.CTkToplevel(self)
        help_win.title("Scripting Tutorial")
        help_win.geometry("500x600")
        help_win.attributes("-topmost", True)

        help_text = (
            "📜 SCRIPT FORMATTING GUIDE\n"
            "---------------------------\n\n"
            "1. BACKGROUNDS\n"
            "Syntax: [BG: filename]\n\n"
            "2. JSON FILES\n"
            "Syntax: [JSON: filename]\n"
            "Note: Loads a .json from the 'json' folder. Use for UI colors or audio.\n"
            "Note: Place audio files (.wav/.mp3) inside the 'json' folder too.\n"
            "Example JSON: {\"box_color\": [255,0,0], \"sound\": \"beep.wav\"}\n\n"
            "3. DIALOGUE & CHARACTERS\n"
            "Syntax: CharacterName: Your text here\n\n"
            "4. COMMENTS\n"
            "Syntax: // your note\n\n"
            "5. ASSET TIPS\n"
            "• Characters: Transparent PNGs in CharacterName.chr folders.\n"
            "• Backgrounds: 1280x720 PNG/JPG.\n"
            "• JSON: Put .json and audio files in the 'json' folder."
        )
        
        textbox = ctk.CTkTextbox(help_win, font=("Arial", 13), wrap="word")
        textbox.pack(padx=20, pady=20, fill="both", expand=True)
        textbox.insert("1.0", help_text)
        textbox.configure(state="disabled")

    def show_studio(self):
        self.clear_screen()
        sidebar = ctk.CTkFrame(self, width=220)
        sidebar.pack(side="left", fill="y", padx=5, pady=5)
        
        ctk.CTkLabel(sidebar, text="ASSETS", font=("Arial", 16, "bold")).pack(pady=15)
        ctk.CTkButton(sidebar, text="+ Character", command=self.add_char).pack(pady=5, padx=10)
        ctk.CTkButton(sidebar, text="+ Background", command=self.add_bg).pack(pady=5, padx=10)
        ctk.CTkButton(sidebar, text="+ JSON File", command=self.add_json_file).pack(pady=5, padx=10)
        ctk.CTkButton(sidebar, text="+ EXE Icon (.ico)", command=self.add_icon).pack(pady=5, padx=10)
        
        ctk.CTkLabel(sidebar, text="FONT SETTINGS", font=("Arial", 14)).pack(pady=(20, 5))
        self.font_menu = ctk.CTkOptionMenu(sidebar, values=["Arial", "Comic Sans MS", "Cursive", "IMPORT CUSTOM"], command=self.change_font)
        self.font_menu.pack(pady=5, padx=10)

        ctk.CTkButton(sidebar, text="❓ HOW TO USE", fg_color="#3498db", command=self.show_help).pack(side="bottom", pady=5, padx=10)
        ctk.CTkButton(sidebar, text="👁 PREVIEW", fg_color="#e67e22", command=self.preview_game).pack(side="bottom", pady=5, padx=10)
        ctk.CTkButton(sidebar, text="📦 BUILD EXE", fg_color="#27ae60", command=self.build_exe).pack(side="bottom", pady=10, padx=10)
        ctk.CTkButton(sidebar, text="🏠 Home", fg_color="gray30", command=self.show_project_manager).pack(side="bottom", pady=5, padx=10)

        editor_container = ctk.CTkFrame(self)
        editor_container.pack(side="right", expand=True, fill="both", padx=5, pady=5)
        text_frame = ctk.CTkFrame(editor_container)
        text_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        self.line_nums = tk.Text(text_frame, width=4, padx=5, pady=10, takefocus=0, border=0, background="#1d1d1d", foreground="#666666", state='disabled', font=("Courier New", 14))
        self.line_nums.pack(side="left", fill="y")
        
        self.script_box = ctk.CTkTextbox(text_frame, font=("Courier New", 14), wrap="none")
        self.script_box.pack(side="right", expand=True, fill="both")
        self.script_box.bind("<KeyRelease>", self.update_line_numbers)
        
        if os.path.exists(f"{self.current_project_path}/script.txt"):
            with open(f"{self.current_project_path}/script.txt", "r", encoding="utf-8") as f:
                self.script_box.insert("1.0", f.read())
        self.update_line_numbers()

    def update_line_numbers(self, event=None):
        line_count = self.script_box.get("1.0", "end").count('\n')
        self.line_nums.configure(state='normal')
        self.line_nums.delete("1.0", "end")
        self.line_nums.insert("1.0", "\n".join(str(i) for i in range(1, line_count + 1)))
        self.line_nums.configure(state='disabled')
        self.line_nums.yview_moveto(self.script_box.yview()[0])

    def change_font(self, choice):
        if choice == "IMPORT CUSTOM":
            file = filedialog.askopenfilename(filetypes=[("Font File", "*.ttf")])
            if file:
                dest = f"{self.current_project_path}/fonts/custom.ttf"
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy(file, dest)
                self.selected_font = "custom.ttf"
                messagebox.showinfo("Font", "Custom font imported!")
        else:
            self.selected_font = choice

    def add_icon(self):
        file = filedialog.askopenfilename(filetypes=[("Icon", "*.ico")])
        if file:
            shutil.copy(file, f"{self.current_project_path}/icon.ico")
            messagebox.showinfo("Icon", "Icon added!")

    def add_char(self):
        name = simpledialog.askstring("Character", "Name:")
        if name:
            file = filedialog.askopenfilename(filetypes=[("PNG", "*.png")])
            if file:
                dest = f"{self.current_project_path}/characters/{name}.chr"
                os.makedirs(dest, exist_ok=True)
                shutil.copy(file, f"{dest}/sprite.png")

    def add_bg(self):
        name = simpledialog.askstring("Background", "Name:")
        if name:
            file = filedialog.askopenfilename(filetypes=[("Image", "*.jpg *.png *.jpeg")])
            if file:
                dest = f"{self.current_project_path}/backgrounds"
                os.makedirs(dest, exist_ok=True)
                shutil.copy(file, f"{dest}/{name}.png")

    def add_json_file(self):
        name = simpledialog.askstring("JSON File", "File Name (without .json):")
        if name:
            file = filedialog.askopenfilename(filetypes=[("JSON/Audio", "*.json *.wav *.mp3")])
            if file:
                dest = f"{self.current_project_path}/json"
                os.makedirs(dest, exist_ok=True)
                shutil.copy(file, f"{dest}/{os.path.basename(file)}")
                messagebox.showinfo("JSON", f"Added to json folder!")

    def save_script(self):
        with open(f"{self.current_project_path}/script.txt", "w", encoding="utf-8") as f:
            f.write(self.script_box.get("1.0", "end"))

    def build_exe(self):
        self.save_script()
        project_name = os.path.basename(self.current_project_path)
        project_dir = self.current_project_path 
        icon_arg = ["--icon", f"{project_dir}/icon.ico"] if os.path.exists(f"{project_dir}/icon.ico") else []

        with open("temp_engine.py", "w", encoding="utf-8") as f:
            f.write(self.get_engine_code(is_preview=False))

        cmd = ["python", "-m", "PyInstaller", "--onefile", "--noconsole", "--distpath", project_dir, "--name", project_name] + icon_arg + ["temp_engine.py"]
        subprocess.run(cmd)

        cleanup_cmd = 'timeout /t 5 /nobreak > NUL && del /f /q "temp_engine.py" "preview_launcher.py" "*.spec" && rmdir /s /q "build" "__pycache__" "dist"'
        subprocess.Popen(cleanup_cmd, shell=True)
        messagebox.showinfo("Success", f"Build complete!")

    def preview_game(self):
        self.save_script()
        with open("preview_launcher.py", "w", encoding="utf-8") as f:
            f.write(self.get_engine_code(is_preview=True))
        subprocess.Popen(["python", "preview_launcher.py"])

    def get_engine_code(self, is_preview):
        p = self.current_project_path.replace("\\", "/")
        game_title = os.path.basename(p)
        script = f"{p}/script.txt" if is_preview else "script.txt"
        bgs = f"{p}/backgrounds" if is_preview else "backgrounds"
        chars = f"{p}/characters" if is_preview else "characters"
        font_folder = f"{p}/fonts" if is_preview else "fonts"
        json_folder = f"{p}/json" if is_preview else "json"
        
        return f"""
import pygame, os, sys, json
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
pygame.display.set_caption("{game_title}")

def get_font(size):
    f_name = "{self.selected_font}"
    if f_name == "custom.ttf":
        path = os.path.join(r"{font_folder}", "custom.ttf")
        return pygame.font.Font(path, size) if os.path.exists(path) else pygame.font.SysFont("Arial", size)
    return pygame.font.SysFont(f_name, size)

def draw_rounded_rect(surface, color, rect, radius=20):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def run():
    global screen
    font_main = get_font(32)
    font_name = get_font(28)
    
    box_color = (20, 20, 20)
    text_color = (255, 255, 255)
    name_color = (255, 215, 0)
    
    lines = []
    if not os.path.exists(r"{script}"): return
    with open(r"{script}", "r", encoding="utf-8") as f:
        for l in f:
            l = l.strip()
            if l.startswith("//") or not l: continue
            lines.append(l)
    
    idx, bg_img = 0, None
    while idx < len(lines):
        line = lines[idx]
        
        if line.startswith("[BG:"):
            bg_name = line.split(":")[1].replace("]", "").strip()
            path = os.path.join(r"{bgs}", bg_name + ".png")
            if os.path.exists(path): bg_img = pygame.image.load(path)
            idx += 1; continue
            
        if line.startswith("[JSON:"):
            json_name = line.split(":")[1].replace("]", "").strip()
            j_path = os.path.join(r"{json_folder}", json_name + ".json")
            if os.path.exists(j_path):
                try:
                    with open(j_path, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                        if "box_color" in data: box_color = tuple(data["box_color"])
                        if "text_color" in data: text_color = tuple(data["text_color"])
                        if "sound" in data and data["sound"] != "none":
                            s_path = os.path.join(r"{json_folder}", data["sound"])
                            if os.path.exists(s_path):
                                snd = pygame.mixer.Sound(s_path)
                                snd.set_volume(data.get("volume", 1.0))
                                snd.play()
                except Exception as e: print(f"JSON Error: {{e}}")
            idx += 1; continue

        screen.fill((0,0,0))
        cur_w, cur_h = screen.get_size()
        if bg_img: screen.blit(pygame.transform.scale(bg_img, (cur_w, cur_h)), (0,0))
        
        if ":" in line:
            name, text = line.split(":", 1)
            s_path = os.path.join(r"{chars}", name.strip() + ".chr", "sprite.png")
            if os.path.exists(s_path):
                s_img = pygame.image.load(s_path)
                screen.blit(pygame.transform.scale(s_img, (450, 650)), (cur_w//2 - 225, 30))
            
            box_rect = (50, cur_h-200, cur_w-100, 160)
            draw_rounded_rect(screen, box_color, box_rect, 15)
            pygame.draw.rect(screen, (255,255,255), box_rect, 2, border_radius=15)
            
            screen.blit(font_name.render(name.strip(), True, name_color), (75, cur_h-190))
            screen.blit(font_main.render(text.strip(), True, text_color), (75, cur_h-140))
            
        pygame.display.flip()
        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type == pygame.MOUSEBUTTONDOWN: idx += 1; waiting = False
                if e.type == pygame.VIDEORESIZE:
                    screen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                    waiting = False 
    pygame.quit()
if __name__ == "__main__": run()
"""

if __name__ == "__main__":
    app = StoryGameStudio()
    app.mainloop()
