


""" v1.0.0 WhatsFlow Campaign Suite"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pywhatkit as kit
import pyautogui
import random
import time
import os
import csv
from PIL import Image, ImageTk
import json

# ====================== CONFIGURATION ======================
class AppConfig:
    PRIMARY_COLOR = "#2E3B4E"
    SECONDARY_COLOR = "#1ABC9C"
    ACCENT_COLOR = "#3498DB"
    BG_COLOR = "#F8F9FA"
    FONT_NAME = "Segoe UI"
    ICON_SIZE = (64, 64)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSET_PATH = os.path.join(BASE_DIR, "assets")
    BTN_STYLE = {
        'font': (FONT_NAME, 10, 'bold'),
        'borderwidth': 1,
        'relief': 'flat',
        'padding': 6
    }

# ====================== APPLICATION DATA ======================
class AppData:
    MESSAGES = {}
    CATEGORY_ASSETS = {}

    @classmethod
    def load_data(cls):
        try:
            with open('app_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls.MESSAGES = data['MESSAGES']
                cls.CATEGORY_ASSETS = data['MESSAGES_ASSETS']
        except FileNotFoundError:
            messagebox.showerror("Config Error", "app_data.json file not found!")
            exit(1)
        except Exception as e:
            messagebox.showerror("Config Error", f"Error loading config: {str(e)}")
            exit(1)

# ====================== MAIN APPLICATION ======================
class WhatsFlowCampaignSuite:
    def __init__(self, master):
        self.master = master
        self.master.title("WhatsFlow Campaign Suite")
        self.master.geometry("1280x800")
        self.master.configure(bg=AppConfig.BG_COLOR)
        
        self.setup_styles()
        self.setup_ui()
        self.load_assets()
        self.setup_bindings()
        
        self.sent_count = 0
        self.failed_count = 0

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('TFrame', background=AppConfig.BG_COLOR)
        style.configure('TLabel', background=AppConfig.BG_COLOR, font=(AppConfig.FONT_NAME, 9))
        style.configure('TButton', **AppConfig.BTN_STYLE)
        style.configure('Primary.TButton', foreground='white', background=AppConfig.SECONDARY_COLOR)
        style.configure('Secondary.TButton', foreground='white', background=AppConfig.PRIMARY_COLOR)
        style.configure('Success.TButton', foreground='white', background=AppConfig.ACCENT_COLOR)
        style.configure('TCombobox', fieldbackground='white', padding=5)
        style.configure('TEntry', fieldbackground='white', padding=5)
        style.configure('TProgressbar', thickness=20, background=AppConfig.SECONDARY_COLOR)
        style.configure('Card.TFrame', background='white', borderwidth=1, relief='solid')

    def setup_ui(self):
        self.create_header()
        self.create_input_section()
        self.create_preview_section()
        self.create_progress_bar()
        self.create_footer()

    def load_assets(self):
        self.images = {}
        for category, filename in AppData.CATEGORY_ASSETS.items():
            try:
                img_path = os.path.join(AppConfig.ASSET_PATH, filename)
                img = Image.open(img_path)
                img = img.resize(AppConfig.ICON_SIZE)
                self.images[category] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
                self.images[category] = None

    def create_header(self):
        header_frame = ttk.Frame(self.master)
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Logo and Title
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side=tk.LEFT)
        try:
            logo_img = Image.open(os.path.join(AppConfig.ASSET_PATH, "logo.png"))
            logo_img = logo_img.resize((60, 60))
            self.logo = ImageTk.PhotoImage(logo_img)
            ttk.Label(left_frame, image=self.logo).pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"Logo error: {str(e)}")

        title_frame = ttk.Frame(left_frame)
        title_frame.pack(side=tk.LEFT)
        ttk.Label(title_frame, text="WhatsFlow Campaign Suite", 
                 font=(AppConfig.FONT_NAME, 20, "bold"), 
                 foreground=AppConfig.PRIMARY_COLOR).pack(anchor=tk.W)
        ttk.Label(title_frame, text="Streamline Your WhatsApp Outreach with Precision", 
                 font=(AppConfig.FONT_NAME, 12), 
                 foreground="#95A5A6").pack(anchor=tk.W)
        
        # Stats Panel
        stats_frame = ttk.Frame(header_frame, style='Card.TFrame')
        stats_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Label(stats_frame, text="Campaign Stats", 
                 font=(AppConfig.FONT_NAME, 12, 'bold'),
                 foreground=AppConfig.PRIMARY_COLOR).grid(row=0, column=0, columnspan=2, pady=5)
        
        ttk.Label(stats_frame, text="Sent:", foreground="#7F8C8D").grid(row=1, column=0, sticky=tk.W)
        self.sent_label = ttk.Label(stats_frame, text="0", foreground=AppConfig.SECONDARY_COLOR)
        self.sent_label.grid(row=1, column=1, padx=10)
        
        ttk.Label(stats_frame, text="Failed:", foreground="#7F8C8D").grid(row=2, column=0, sticky=tk.W)
        self.failed_label = ttk.Label(stats_frame, text="0", foreground="#E74C3C")
        self.failed_label.grid(row=2, column=1, padx=10)

    def create_input_section(self):
        input_frame = ttk.Frame(self.master, style='Card.TFrame')
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Phone Input Section
        ttk.Label(input_frame, text="Recipient Numbers", font=(AppConfig.FONT_NAME, 12, 'bold'),
                 foreground=AppConfig.PRIMARY_COLOR).pack(anchor=tk.W, pady=5)
        
        input_row = ttk.Frame(input_frame)
        input_row.pack(fill=tk.X, pady=10)
        
        ttk.Button(input_row, text="📁 Upload CSV", 
                  command=self.load_csv, style="Primary.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Label(input_row, text="or", foreground="#7F8C8D").pack(side=tk.LEFT, padx=5)
        self.phone_entry = ttk.Entry(input_row)
        self.phone_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Campaign Settings
        settings_frame = ttk.Frame(input_frame)
        settings_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(settings_frame, text="Campaign Type:", font=(AppConfig.FONT_NAME, 10)).grid(row=0, column=0, sticky=tk.W)
        self.category_var = tk.StringVar()
        self.category_menu = ttk.Combobox(settings_frame, textvariable=self.category_var,
                                        values=list(AppData.MESSAGES.keys()),
                                        state='readonly')
        self.category_menu.grid(row=0, column=1, padx=10, sticky=tk.EW)
        
        # Action Buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="🚀 Launch Campaign", 
                 command=self.start_campaign, style="Success.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Reset Form", 
                 command=self.reset_form, style="Secondary.TButton").pack(side=tk.LEFT, padx=5)

    def create_preview_section(self):
        preview_frame = ttk.Frame(self.master, style='Card.TFrame')
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        ttk.Label(preview_frame, text="Message Preview", 
                 font=(AppConfig.FONT_NAME, 12, 'bold'),
                 foreground=AppConfig.PRIMARY_COLOR).pack(anchor=tk.W, pady=5)
        
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=8,
                                  font=(AppConfig.FONT_NAME, 10),
                                  bg='white', padx=10, pady=10)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.image_preview = ttk.Label(preview_frame)
        self.image_preview.pack(pady=10)

    def create_progress_bar(self):
        self.progress = ttk.Progressbar(self.master, orient=tk.HORIZONTAL,
                                       mode='determinate', style='TProgressbar')
        self.progress.pack(fill=tk.X, padx=20, pady=10)

    def create_footer(self):
        footer_frame = ttk.Frame(self.master)
        footer_frame.pack(fill=tk.X, padx=20, pady=10)
        ttk.Label(footer_frame, 
                 text="© 2025 Ramesh Kumar Sah | Contact: +9779862981898 | www.rameshkumarsah.com.np",
                 font=(AppConfig.FONT_NAME, 8), 
                 foreground="#95A5A6").pack()

    def setup_bindings(self):
        self.category_var.trace_add('write', self.update_category)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                start = file.read(1)
                if start != '\ufeff':
                    file.seek(0)
                
                reader = csv.DictReader(file)
                numbers = []
                
                for row in reader:
                    phone = row.get('Phone') or row.get('phone') or row.get('PHONE') or row.get('phone_number')
                    if phone and str(phone).strip():
                        numbers.append(str(phone).strip())
                
                if numbers:
                    self.phone_entry.delete(0, tk.END)
                    self.phone_entry.insert(0, ', '.join(numbers))
                    messagebox.showinfo("CSV Import", f"Imported {len(numbers)} numbers")
                else:
                    messagebox.showwarning("Empty CSV", "No valid phone numbers found")
        except Exception as e:
            messagebox.showerror("Import Error", f"CSV Error: {str(e)}")

    def update_category(self, *args):
        self.update_preview()

    def update_preview(self):
        self.preview_text.delete(1.0, tk.END)
        category = self.category_var.get()
        preview = random.choice(AppData.MESSAGES.get(category, [""]))
        self.preview_text.insert(tk.END, preview)
        
        img = self.images.get(category)
        if img:
            self.image_preview.config(image=img)
            self.image_preview.image = img

    def start_campaign(self):
        numbers = self.process_numbers()
        if not numbers:
            messagebox.showwarning("Input Error", "Please enter phone numbers!")
            return
        
        message = self.generate_message()
        self.progress["value"] = 0
        total = len(numbers)
        
        try:
            for i, number in enumerate(numbers):
                try:
                    self.send_immediately(number, message)
                    self.sent_count += 1
                except Exception as e:
                    self.failed_count += 1
                    self.log_error(number, str(e))
                
                self.progress["value"] = (i+1)/total*100
                self.master.update_idletasks()
                self.update_stats()
            
            messagebox.showinfo("Complete", 
                f"Success: {self.sent_count}\nFailed: {self.failed_count}")
        except Exception as e:
            messagebox.showerror("Campaign Error", str(e))
        finally:
            self.progress.stop()
            self.reset_form()

    def process_numbers(self):
        raw = self.phone_entry.get().replace(" ", "")
        return [n.strip() for n in raw.split(',') if n.strip()]

    def generate_message(self):
        category = self.category_var.get()
        return random.choice(AppData.MESSAGES.get(category, ["Message not found"]))

    def send_immediately(self, number, message):
        category = self.category_var.get()
        filename = AppData.CATEGORY_ASSETS.get(category)
        image_path = os.path.join(AppConfig.ASSET_PATH, filename) if filename else ""
        
        try:
            if filename and os.path.exists(image_path):
                kit.sendwhats_image(number, image_path, caption=message, wait_time=15)
            else:
                kit.sendwhatmsg_instantly(number, message, wait_time=15)
            
            time.sleep(2)
            pyautogui.press('enter')
        except Exception as e:
            raise Exception(f"Send failed: {str(e)}")

    def log_error(self, number, error):
        with open("error_log.txt", "a") as f:
            f.write(f"[{time.ctime()}] {number}: {error}\n")

    def update_stats(self):
        self.sent_label.config(text=f"{self.sent_count}")
        self.failed_label.config(text=f"{self.failed_count}")

    def reset_form(self):
        self.phone_entry.delete(0, tk.END)
        self.category_var.set('')
        self.preview_text.delete(1.0, tk.END)
        self.image_preview.config(image='')
        self.sent_count = 0
        self.failed_count = 0
        self.update_stats()

if __name__ == "__main__":
    AppData.load_data()
    root = tk.Tk()
    app = WhatsFlowCampaignSuite(root)
    root.mainloop()