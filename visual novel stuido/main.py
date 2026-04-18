import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import os, shutil, subprocess, time

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
            with open(f"{path}/script.txt", "w") as f:
                # Updated starter script with better instructions
                f.write("// --- BASIC SCRIPT FORMATTING ---\n")
                f.write("// [BG: name] -> Changes background (must be in backgrounds folder)\n")
                f.write("// Name: Dialogue -> Shows character sprite and text\n\n")
                f.write("[BG: room]\nTeto: 🍜 Welcome to your new game!\n")
                f.write("Teto: Click the '?' button in the sidebar to see the full tutorial.")
            self.open_project(name)

    def open_project(self, name):
        self.current_project_path = os.path.abspath(f"projects/{name}")
        self.show_studio()

    def show_help(self):
        help_win = ctk.CTkToplevel(self)
        help_win.title("Scripting Tutorial")
        help_win.geometry("500x550")
        help_win.attributes("-topmost", True)

        help_text = (
            "📜 SCRIPT FORMATTING GUIDE\n"
            "---------------------------\n\n"
            "1. BACKGROUNDS\n"
            "Syntax: [BG: filename]\n"
            "Example: [BG: forest]\n"
            "Note: Do NOT include .png. The file must be in the 'backgrounds' folder.\n\n"
            "2. DIALOGUE & CHARACTERS\n"
            "Syntax: CharacterName: Your text here\n"
            "Example: Teto: Hello, traveler!\n"
            "Note: The engine looks for a folder named 'CharacterName.chr' in 'characters'.\n\n"
            "3. COMMENTS\n"
            "Syntax: // your note\n"
            "Note: Lines starting with // are ignored by the game engine.\n\n"
            "4. ASSET TIPS\n"
            "• Characters: Best as transparent PNGs (approx. 450x650).\n"
            "• Backgrounds: Best as 1280x720 PNG or JPG.\n"
            "• Icons: Must be .ico format for the build."
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
        ctk.CTkButton(sidebar, text="+ EXE Icon (.ico)", command=self.add_icon).pack(pady=5, padx=10)
        
        ctk.CTkLabel(sidebar, text="FONT SETTINGS", font=("Arial", 14)).pack(pady=(20, 5))
        self.font_menu = ctk.CTkOptionMenu(sidebar, values=["Arial", "Comic Sans MS", "Cursive", "IMPORT CUSTOM"], command=self.change_font)
        self.font_menu.pack(pady=5, padx=10)

        # Bottom Buttons
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
            with open(f"{self.current_project_path}/script.txt", "r") as f:
                self.script_box.insert("1.0", f.read())
        self.update_line_numbers()

    # ... [Rest of the methods: update_line_numbers, change_font, add_icon, add_char, add_bg, save_script, build_exe, preview_game, get_engine_code remain the same] ...

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

    def save_script(self):
        with open(f"{self.current_project_path}/script.txt", "w") as f:
            f.write(self.script_box.get("1.0", "end"))

    def build_exe(self):
        self.save_script()
        project_name = os.path.basename(self.current_project_path)
        project_dir = self.current_project_path 
        
        icon_arg = []
        if os.path.exists(f"{project_dir}/icon.ico"):
            icon_arg = ["--icon", f"{project_dir}/icon.ico"]

        with open("temp_engine.py", "w") as f:
            f.write(self.get_engine_code(is_preview=False))

        cmd = ["python", "-m", "PyInstaller", "--onefile", "--noconsole", "--distpath", project_dir, "--name", project_name] + icon_arg + ["temp_engine.py"]
        subprocess.run(cmd)

        cleanup_cmd = (
            'timeout /t 5 /nobreak > NUL && '
            'del /f /q "temp_engine.py" "preview_launcher.py" "*.spec" && '
            'rmdir /s /q "build" "__pycache__" "dist"'
        )
        subprocess.Popen(cleanup_cmd, shell=True)
        messagebox.showinfo("Success", f"Build complete! EXE is in the project folder.")

    def preview_game(self):
        self.save_script()
        with open("preview_launcher.py", "w") as f:
            f.write(self.get_engine_code(is_preview=True))
        subprocess.Popen(["python", "preview_launcher.py"])

    def get_engine_code(self, is_preview):
        p = self.current_project_path.replace("\\", "/")
        game_title = os.path.basename(p)
        script = f"{p}/script.txt" if is_preview else "script.txt"
        bgs = f"{p}/backgrounds" if is_preview else "backgrounds"
        chars = f"{p}/characters" if is_preview else "characters"
        font_folder = f"{p}/fonts" if is_preview else "fonts"
        
        return f"""
import pygame, os, sys
pygame.init()
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
    lines = []
    if not os.path.exists(r"{script}"): return
    with open(r"{script}", "r") as f:
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
            draw_rounded_rect(screen, (20,20,20), box_rect, 15)
            pygame.draw.rect(screen, (255,255,255), box_rect, 2, border_radius=15)
            
            screen.blit(font_name.render(name.strip(), True, (255, 215, 0)), (75, cur_h-190))
            screen.blit(font_main.render(text.strip(), True, (255, 255, 255)), (75, cur_h-140))
            
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