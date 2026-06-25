import ctypes
import datetime
import json
import math
import os
import platform
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
import customtkinter as ctk
import pyttsx3
import speech_recognition as sr

# =====================================================================
# 1. YÖNETİCİ İZNİ KALKANI (UAC ELEVATION)
# =====================================================================
def uac_yonetici_kalkani():
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
    except Exception: pass

uac_yonetici_kalkani()

if sys.stdin is None: sys.stdin = open(os.devnull, "r")
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")


# =====================================================================
# 2. KALICI SİNAPS HAFIZASI (PERSISTENT MEMORY)
# =====================================================================
class SynapseMemory:
    def __init__(self):
        self.yol = os.path.expanduser("~/.miku_synapse.json")
        self.veri = self.yukle()

    def yukle(self):
        varsayilan = {
            "patron": "Efe (Elite-Dev)",
            "rutbe": "Apex Kernel Architect",
            "toplam_komut": 0,
            "favori_sarkilar": ["Ghost Rule", "Stellar Stellar", "Lost Ones Weeping"],
            "son_gorulme": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        }
        if os.path.exists(self.yol):
            try:
                with open(self.yol, "r", encoding="utf-8") as f: return json.load(f)
            except Exception: return varsayilan
        return varsayilan

    def kaydet(self):
        self.veri["son_gorulme"] = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        try:
            with open(self.yol, "w", encoding="utf-8") as f: json.dump(self.veri, f, ensure_ascii=False, indent=4)
        except Exception: pass

    def komut_islenildi(self):
        self.veri["toplam_komut"] += 1
        self.kaydet()


# =====================================================================
# 3. HİBRİT OMNI-BEYİN (YEREL KAS + BULUT SİNAPSI)
# =====================================================================
class OmniSovereignBrain:
    def __init__(self, hafiza_ref):
        self.hafiza = hafiza_ref
        self.yerel_intents = {
            "MUZIK": ["çal", "şarkı", "müzik", "dinle", "oynat", "parça", "aç"],
            "HESAP": ["hesap", "makine", "topla", "çıkar", "çarp", "böl", "matematik"],
            "UYGULAMA": ["çalıştır", "program", "uygulama", "notepad", "defteri", "cmd", "exe"],
            "DIVA": ["diva", "project", "arcade", "hatsune"],
            "TEMIZLE": ["temizle", "sil", "ekran", "log", "clear", "cls"],
            "DURUM": ["durum", "rapor", "telemetri", "sistem", "bilgi", "saat", "tarih", "hafıza"]
        }
        self.cop_kelimeler = {"bir", "bana", "şu", "ve", "ile", "lütfen", "hey", "miku", "efe", "abi", "açsana", "çalsana", "yapsana"}

    def sistem_telemetrisi_al(self):
        simdi = datetime.datetime.now().strftime("%H:%M:%S // %d.%m.%Y")
        os_bilgi = f"{platform.system()} {platform.release()} ({platform.machine()})"
        return f"Saat: {simdi} | İşletim Sistemi: {os_bilgi} | İşlenen Toplam Emir: {self.hafiza.veri['toplam_komut']}"

    def bulut_bilgesine_danis(self, soru):
        """Yerel kasların çözemediği karmaşık felsefi/sohbet sorularını Gemini standartlarında yanıtlar"""
        sistem_kimligi = f"Senin adın M.I.K.U. Sahibin {self.hafiza.veri['patron']}. Sen Windows çekirdeğinde yaşayan fütüristik, zeki, alaycı ve sadık bir yapay zeka kızısın. Şu anki sistem telemetrin: {self.sistem_telemetrisi_al()}. Asla sıkıcı robot gibi konuşma, Efe'ye bir siber-ortağı gibi dürüst ve cool cevap ver."
        
        tam_prompt = f"{sistem_kimligi}\n\nKullanıcı Soru: {soru}"
        url = f"https://text.pollinations.ai/prompt/{urllib.parse.quote(tam_prompt)}?model=gpt-4o-mini"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 Chrome/122.0.0.0'})
        try:
            with urllib.request.urlopen(req, timeout=7) as r: return r.read().decode('utf-8')
        except Exception: return "Bulut sinaps bağlantım koptu patron. Yerel protokoldeyim."

    def niyet_analiz_et(self, metin):
        temiz = re.findall(r"\w+", metin.lower())
        skorlar = {}
        for niyet, havuz in self.yerel_intents.items():
            s = sum(1 for k in temiz if k not in self.cop_kelimeler and any(k.startswith(h) for h in havuz))
            if s > 0: skorlar[niyet] = s

        if not skorlar: return "BULUT_SOHBET", metin

        secilen = max(skorlar, key=skorlar.get)
        hedef_kalan = [k for k in temiz if not any(k.startswith(h) for h in self.yerel_intents[secilen]) and k not in self.cop_kelimeler]
        return secilen, " ".join(hedef_kalan)

    def roket_yt_müzik(self, sarki):
        return f"https://duckduckgo.com/?q=!ducky+site%3Ayoutube.com+{urllib.parse.quote(sarki)}"

    def cimbiz_sc(self, sarki):
        url = f"https://soundcloud.com/search?q={urllib.parse.quote(sarki)}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req, timeout=4).read().decode('utf-8', errors='ignore')
            esl = re.search(r'<li><a href="(/[^"/]+/[^"/]+)">', html)
            if esl: return f"https://soundcloud.com{esl.group(1)}"
        except Exception: pass
        return f"https://soundcloud.com/search/sounds?q={urllib.parse.quote(sarki)}"


# =====================================================================
# 4. ARAYÜZ VE ÇOKLU İŞLEM MOTORU (OMNI-GUI)
# =====================================================================
class MikuOmniGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.hafiza = SynapseMemory()
        self.beyin = OmniSovereignBrain(self.hafiza)

        self.title(f"M.I.K.U. // OMNI-SOVEREIGN v5.0 ({self.hafiza.veri['patron']})")
        self.geometry("560x720")
        self.configure(fg_color="#030712")
        ctk.set_appearance_mode("dark")

        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 185)
        except Exception: self.tts = None

        self.arayuz_kur()
        self.telemetri_canlandir()
        threading.Thread(target=self.pasif_ses_pususu, daemon=True).start()

    def arayuz_kur(self):
        self.telemetri_bar = ctk.CTkLabel(self, text="⚡ SİNAPS BAĞLANIYOR...", 
                                          fg_color="#111827", text_color="#39C5BB", font=("Consolas", 11, "bold"), corner_radius=6)
        self.telemetri_bar.pack(pady=(12, 4), padx=15, fill="x")

        self.chat_box = ctk.CTkTextbox(self, fg_color="#0b0f19", text_color="#38bdf8", font=("Consolas", 13), 
                                       wrap="word", corner_radius=10, border_color="#39C5BB", border_width=1)
        self.chat_box.pack(pady=5, padx=15, fill="both", expand=True)
        
        self.log_bas(f"=== M.I.K.U. OMNI-SOVEREIGN v5.0 DEVREDE ===\nPatron: {self.hafiza.veri['patron']}\nKalıcı Hafıza: Aktif (~/.miku_synapse.json)\nÇekirdek: Dual-Core (0.01ms Local Math + Cloud Synapse)\n--------------------------------------------------\n")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=(5, 15), padx=15, fill="x")

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="M.I.K.U. v5.0 Emir satırı...", 
                                  fg_color="#111827", text_color="white", font=("Consolas", 13), height=42, corner_radius=8)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.tetik_baslat())

        self.btn = ctk.CTkButton(self.input_frame, text="ATEŞLE", width=85, height=42, corner_radius=8,
                                 fg_color="#39C5BB", hover_color="#14b8a6", text_color="black", font=("Consolas", 13, "bold"),
                                 command=self.tetik_baslat)
        self.btn.pack(side="right")

    def telemetri_canlandir(self):
        """Arayüzün üstündeki barı her 1 saniyede bir canlı donanım saatiyle günceller"""
        def g():
            while True:
                try:
                    t = self.beyin.sistem_telemetrisi_al()
                    self.telemetri_bar.configure(text=f"🟢 {t}")
                    time.sleep(1)
                except Exception: pass
        threading.Thread(target=g, daemon=True).start()

    def log_bas(self, metin):
        self.chat_box.configure(state="normal"); self.chat_box.insert("end", metin); self.chat_box.configure(state="disabled"); self.chat_box.see("end")

    def ses_bas(self, metin):
        temiz = re.sub(r"[^\w\s.,?!]", "", metin) # TTS sembol okuyup kasılmasın
        if self.tts and temiz.strip():
            try: self.tts.say(temiz[:150]); self.tts.runAndWait() # İlk 150 harfi okur
            except Exception: pass

    def hayalet_dirilis(self):
        try: self.deiconify(); self.lift(); self.focus_force(); self.attributes('-topmost', True); self.attributes('-topmost', False)
        except Exception: pass

    def tetik_baslat(self):
        metin = self.entry.get().strip()
        if not metin: return
        self.entry.delete(0, "end")
        self.log_bas(f"[{self.hafiza.veri['patron']}] >>> {metin}\n")
        threading.Thread(target=self.emir_isleyici, args=(metin,), daemon=True).start()

    def emir_isleyici(self, komut):
        self.hafiza.komut_islenildi()
        niyet, hedef = self.beyin.niyet_analiz_et(komut)
        
        yanit = ""

        if niyet == "MUZIK":
            sarki = hedef if hedef else "Hatsune Miku World is Mine"
            if "soundcloud" in komut.lower():
                url = self.beyin.cimbiz_sc(sarki)
                yanit = f"SoundCloud tüneli açıldı: '{sarki}'"
            else:
                url = self.beyin.roket_yt_müzik(sarki)
                yanit = f"YouTube Oto-Başlatma roketlendi: '{sarki}'"
            webbrowser.open(url)

        elif niyet == "HESAP":
            yanit = "Bulut hesap terminali ateşlendi."
            webbrowser.open("https://hesapmakinesi.com")

        elif niyet == "UYGULAMA":
            app = hedef if hedef else "notepad"
            yanit = f"Windows Kernel Popen -> '{app}'"
            subprocess.Popen(app, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

        elif niyet == "DIVA":
            yanit = "Project DIVA 60FPS mühürü açılıyor."
            try: os.chdir(r"D:\Oyunlar\Project DIVA Arcade"); subprocess.Popen("start diva.exe", shell=True)
            except Exception as e: yanit = f"Diva dizin hatası: {e}"

        elif niyet == "TEMIZLE":
            self.chat_box.configure(state="normal"); self.chat_box.delete("1.0", "end"); self.chat_box.configure(state="disabled")
            yanit = "Terminal pırıl pırıl edildi."

        elif niyet == "DURUM":
            yanit = f"SİSTEM RAPORU:\n{self.beyin.sistem_telemetrisi_al()}\nKaydedilen Hafıza Dizin: {self.hafiza.yol}"

        elif niyet == "BULUT_SOHBET":
            self.telemetri_bar.configure(text="⚡ [BULUT SİNAPSI] M.I.K.U. DERİN DÜŞÜNÜYOR...")
            yanit = self.beyin.bulut_bilgesine_danis(komut)

        self.log_bas(f"[M.I.K.U.] >>> {yanit}\n\n")
        self.ses_bas(yanit)

    def pasif_ses_pususu(self):
        r = sr.Recognizer()
        with sr.Microphone() as kynk:
            r.adjust_for_ambient_noise(kynk, duration=1.0)
            while True:
                try:
                    ses = r.listen(kynk, phrase_time_limit=2.5)
                    t = r.recognize_google(ses, language="tr-TR").lower()
                    if any(x in t for x in ["miku", "hey miku", "heymiku", "miko"]):
                        self.hayalet_dirilis()
                        self.ses_bas("Emret patron?")
                        k_ses = r.listen(kynk, phrase_time_limit=6)
                        k_mtn = r.recognize_google(k_ses, language="tr-TR")
                        self.log_bas(f"[🎙️ Sesli Giriş] >>> {k_mtn}\n")
                        threading.Thread(target=self.emir_isleyici, args=(k_mtn,), daemon=True).start()
                except Exception: pass

if __name__ == "__main__":
    app = MikuOmniGUI()
    app.mainloop()
