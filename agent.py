import os
import sys
import re
import time
import threading
import subprocess
import urllib.parse
import urllib.request
import json
import webbrowser
import customtkinter as ctk
import speech_recognition as sr
import pyttsx3

# --- Noconsole Hayalet Akış Koruması ---
if sys.stdin is None: sys.stdin = open(os.devnull, "r")
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")

# CLOUDFLARE'I KANDIRAN SAFKAN CHROME KİMLİĞİ
CHROME_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

SYSTEM_PROMPT = """Senin adın M.I.K.U. (Modular Interface & Kernel Utility). Sahibin: Efe (Elite-Dev).
Sen Windows çekirdeğine bağlı çalışan fütüristik bir siber ajansın. Asla dalkavukluk yapma, net, mekanik, alaycı ve zeki konuş.

SİSTEM TETİKLERİ (Zorunlu Kurallar):
Eğer kullanıcının isteği aşağıdakilerden biriyse, cevabının EN SONUNA belirtilen KODU eklemek ZORUNDASIN:
1. Uygulama veya .exe açmak istiyorsa -> [RUN:uygulama_adi]  (Örn: [RUN:calc], [RUN:notepad])
2. SoundCloud'dan şarkı açmak istiyorsa -> [SC:sarki_adi]  (Örn: [SC:Ghost Rule])
3. Project DIVA oyununu açmak istiyorsa -> [DIVA]
4. Ekranı temizlemek istiyorsa -> [CLEAR]"""


class MikuKernelGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("M.I.K.U. // OS KONSOLU v1.4 (Pure-Monolith)")
        self.geometry("540x700")
        self.configure(fg_color="#0a1128")
        ctk.set_appearance_mode("dark")

        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 185)
        except Exception: self.tts = None

        self.mesaj_gecmisi = []
        self.arayuzu_kur()
        threading.Thread(target=self.pasif_ses_pususu, daemon=True).start()

    def arayuzu_kur(self):
        self.status_bar = ctk.CTkLabel(self, text="🟢 M.I.K.U. v1.4 // SAF PYTHON KERNEL DEVREDE", 
                                       fg_color="#1c2541", text_color="#39C5BB", font=("Consolas", 12, "bold"), corner_radius=8)
        self.status_bar.pack(pady=(15, 5), padx=15, fill="x")

        self.chat_box = ctk.CTkTextbox(self, fg_color="#0f172a", text_color="#00b4d8", font=("Consolas", 13), 
                                       wrap="word", corner_radius=10, border_color="#39C5BB", border_width=1)
        self.chat_box.pack(pady=5, padx=15, fill="both", expand=True)
        self.log_bas("=== M.I.K.U. PURE-MONOLITH v1.4 YÜKLENDİ ===\nPatron: Efe Elite-Dev\nMimari: Zero-Dependency Native HTTP URL Bridge\n--------------------------------------------------\n")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=(5, 15), padx=15, fill="x")

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Komut yaz veya 'Hey Miku' de...", 
                                  fg_color="#1c2541", text_color="white", font=("Consolas", 13), height=40, corner_radius=8)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.gonder_tetik())

        self.btn_send = ctk.CTkButton(self.input_frame, text="İLET", width=80, height=40, corner_radius=8,
                                      fg_color="#39C5BB", hover_color="#208b84", text_color="black", font=("Consolas", 13, "bold"),
                                      command=self.gonder_tetik)
        self.btn_send.pack(side="right")

    def log_bas(self, metin):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", metin)
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def ses_bas(self, metin):
        temiz = re.sub(r"\[.*?\]", "", metin)
        if self.tts and temiz.strip():
            try: self.tts.say(temiz); self.tts.runAndWait()
            except Exception: pass

    # =================================================================
    # ★ KUSURSUZ KÖPRÜ: GET ENJEKSİYONU (Sıfır Kilitlenme Garantisi)
    # =================================================================
    def ask_cloud_ai(self, user_text):
        # Mesajı ve sistem anayasasını URL formatına güvenlice kodla:
        safe_msg = urllib.parse.quote(user_text)
        safe_sys = urllib.parse.quote(SYSTEM_PROMPT)
        
        # Pollinations GET tüneli (Bunu Cloudflare hayatta engelleyemez):
        url = f"https://text.pollinations.ai/prompt/{safe_msg}?system={safe_sys}&model=gpt-4o-mini"
        
        req = urllib.request.Request(url, headers=CHROME_HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                return r.read().decode('utf-8')
        except Exception as e:
            return f"Hata: Bulut tüneli koptu -> {e}"

    # --- SAF PYTHON DUCKDUCKGO WEB KAZIYICI (Sıfır kütüphane) ---
    def saf_arama_yap(self, sorgu_metni):
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(sorgu_metni)}"
        req = urllib.request.Request(url, headers=CHROME_HEADERS)
        try:
            html_kodu = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
            # HTML içindeki link özetlerini saf Regex ile cımbızla:
            ozetler = re.findall(r'<a class="result__snippet[^>]*>(.*?)</a>', html_kodu)
            temiz = [re.sub(r'<.*?>', '', oz) for oz in ozetler[:3]] # İlk 3 sonuç
            return "\n".join(temiz) if temiz else "İnternette kayda değer bir veri bulunamadı."
        except Exception as e: return f"Arama kilitlendi: {e}"

    def gonder_tetik(self):
        metin = self.entry.get().strip()
        if not metin: return
        self.entry.delete(0, "end")
        self.log_bas(f"[Efe Elite-Dev] >>> {metin}\n")
        threading.Thread(target=self.ajan_motorunu_islet, args=(metin,), daemon=True).start()

    def ajan_motorunu_islet(self, komut):
        k_kontrol = komut.lower().strip()

        # --- ARAŞTIRMA MAKASI ---
        if any(k_kontrol.startswith(x) for x in ["araştır:", "arastir:", "araştır ", "arastir "]):
            sorgu = re.split(r":|\s", komut, 1)[1].strip() if re.search(r":|\s", komut) else komut
            
            self.status_bar.configure(text="⚡ [DEEP-SCAN] 1/2: İNTERNET DEŞİLİYOR...")
            web_raporu = self.saf_arama_yap(sorgu)
            
            self.status_bar.configure(text="⚡ [DEEP-SCAN] 2/2: BİLGİ DAMITILIYOR...")
            sentez_yaniti = self.ask_cloud_ai(f"Şu web bulgularını oku, Efe için net bir Türkçe Rapor yaz:\nSoru: {sorgu}\nBulgular:\n{web_raporu}")
            
            self.log_bas(f"\n==================================================\n[★ KESİN RAPOR]: {sorgu}\n==================================================\n{sentez_yaniti}\n\n")
            self.status_bar.configure(text="🟢 M.I.K.U. v1.4 // SAF PYTHON KERNEL DEVREDE")
            self.ses_bas(sentez_yaniti)
            return

        # --- NORMAL SOHBET & TETİKLEYİCİ ---
        self.status_bar.configure(text="⚡ M.I.K.U. DÜŞÜNÜYOR...")
        yanit = self.ask_cloud_ai(komut)

        self.log_bas(f"[M.I.K.U.] >>> {yanit}\n\n")
        self.ses_bas(yanit)

        # Tetikler
        if re.search(r"\[RUN:(.*?)\]", yanit):
            app = re.search(r"\[RUN:(.*?)\]", yanit).group(1).strip()
            self.log_bas(f"[KERNEL] -> '{app}' tetiklendi.\n\n")
            subprocess.Popen(app, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

        if re.search(r"\[SC:(.*?)\]", yanit):
            sarki = re.search(r"\[SC:(.*?)\]", yanit).group(1).strip()
            self.log_bas(f"[KERNEL] -> SoundCloud '{sarki}' açılıyor.\n\n")
            webbrowser.open(f"https://soundcloud.com/search/sounds?q={urllib.parse.quote(sarki)}")

        if "[DIVA]" in yanit:
            self.log_bas("[KERNEL] -> Project DIVA 60FPS ateşlendi.\n\n")
            try: os.chdir(r"D:\Oyunlar\Project DIVA Arcade"); subprocess.Popen("start diva.exe", shell=True)
            except Exception as e: self.log_bas(f"[HATA]: Diva açılamadı -> {e}\n")

        if "[CLEAR]" in yanit:
            self.chat_box.configure(state="normal"); self.chat_box.delete("1.0", "end"); self.chat_box.configure(state="disabled")

        self.status_bar.configure(text="🟢 M.I.K.U. v1.4 // SAF PYTHON KERNEL DEVREDE")

    # --- DEMİR ADAM SES PUSUSU ---
    def pasif_ses_pususu(self):
        r = sr.Recognizer()
        with sr.Microphone() as kaynak:
            r.adjust_for_ambient_noise(kaynak, duration=1.0)
            while True:
                try:
                    ses = r.listen(kaynak, phrase_time_limit=2.5)
                    tetik = r.recognize_google(ses, language="tr-TR").lower()
                    if any(x in tetik for x in ["miku", "hey miku", "heymiku", "miko", "mikü"]):
                        self.status_bar.configure(text="🎙️ M.I.K.U. DİNLİYOR // KOMUT SÖYLE...")
                        self.ses_bas("Efendim patron?")
                        k_ses = r.listen(kaynak, phrase_time_limit=6)
                        k_metin = r.recognize_google(k_ses, language="tr-TR")
                        self.log_bas(f"[🎙️ Sesli Giriş] >>> {k_metin}\n")
                        threading.Thread(target=self.ajan_motorunu_islet, args=(k_metin,), daemon=True).start()
                except Exception: pass

if __name__ == "__main__":
    app = MikuKernelGUI()
    app.mainloop()
