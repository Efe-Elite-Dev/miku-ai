import ctypes
import datetime
import difflib
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
import winsound

def uac_yonetici_kalkani():
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
    except Exception: pass

uac_yonetici_kalkani()

# =====================================================================
# ★★★ OTA GÜNCELLEME AYARLARI (REPORUN ADINI BURAYA YAZ) ★★★
# =====================================================================
YEREL_SURUM = "v6.3"
GITHUB_REPO = "Efe-Elite-Dev/miku-ai" # <--- Örn: Efe-Elite-Dev/Miku-Karargah


if sys.stdin is None: sys.stdin = open(os.devnull, "r")
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")


class SynapseMemory:
    def __init__(self):
        self.yol = os.path.expanduser("~/.miku_synapse.json")
        self.veri = self.yukle()

    def yukle(self):
        varsayilan = {
            "kurulum_tamamlandi": False,
            "patron": "Efe Elite-Dev",
            "uyandirma_kelimesi": "hey miku",
            "toplam_komut": 0,
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


class GodModeBrain:
    def __init__(self, hafiza_ref):
        self.hafiza = hafiza_ref
        self.yerel_intents = {
            "MUZIK": ["çal", "şarkı", "müzik", "dinle", "oynat", "parça", "aç"],
            "MEDYA_DURDUR": ["durdur", "dur", "sus", "kes", "sessiz", "beklet"], # ★ DONANIM KANCASI
            "HESAP": ["hesap", "makine", "topla", "çıkar", "çarp", "böl", "matematik", "hesapla"],
            "UYGULAMA": ["çalıştır", "program", "uygulama", "notepad", "defteri", "cmd", "exe"],
            "DIVA": ["diva", "project", "arcade", "hatsune"],
            "TEMIZLE": ["temizle", "sil", "ekran", "log", "clear", "cls"],
            "DURUM": ["durum", "rapor", "telemetri", "sistem", "bilgi", "saat", "tarih", "sürüm"],
            "KAPAT": ["kapat", "kapan", "söndür", "uykuya", "yatır", "fişi"],
            "PANIK": ["panik", "gizle", "sakla", "kurtar", "tehlike"]
        }
        self.cop_kelimeler = {"bir", "bana", "şu", "ve", "ile", "lütfen", "hey", "miku", "efe", "abi", "açsana", "çalsana"}

    def sistem_telemetrisi_al(self):
        simdi = datetime.datetime.now().strftime("%H:%M:%S")
        return f"Saat: {simdi} | OS: {platform.system()} | Emir: {self.hafiza.veri['toplam_komut']} | Sürüm: {YEREL_SURUM}"

    def bulut_bilgesine_danis(self, soru):
        sistem_kimligi = f"Senin adın M.I.K.U. Sahibin {self.hafiza.veri['patron']}. Sen fütüristik, zeki yapay zeka kızısın. Efe hızlı ve disleksik tarzda yazar, ne demek istediğini anla. Sürümün: {YEREL_SURUM}."
        tam_prompt = f"{sistem_kimligi}\n\nKullanıcı Soru: {soru}"
        url = f"https://text.pollinations.ai/prompt/{urllib.parse.quote(tam_prompt)}?model=gpt-4o-mini"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=7) as r: return r.read().decode('utf-8')
        except Exception: return "Bulut bağlantım koptu patron."

    def niyet_analiz_et(self, metin):
        temiz = re.findall(r"\w+", metin.lower())
        skorlar = {}
        for niyet, havuz in self.yerel_intents.items():
            s = sum(1 for k in temiz if k not in self.cop_kelimeler and (difflib.get_close_matches(k, havuz, n=1, cutoff=0.7) or any(k.startswith(h) for h in havuz)))
            if s > 0: skorlar[niyet] = s

        if not skorlar: return "BULUT_SOHBET", metin
        secilen = max(skorlar, key=skorlar.get)
        hedef_kalan = [k for k in temiz if not difflib.get_close_matches(k, self.yerel_intents[secilen], n=1, cutoff=0.7) and k not in self.cop_kelimeler]
        return secilen, " ".join(hedef_kalan)

    def kapatma_saniyesi_hesapla(self, metin):
        mt = metin.lower()
        if m_dk := re.search(r"(\d+)\s*(?:dakika|dk)", mt): return int(m_dk.group(1)) * 60
        if m_saat := re.search(r"(\d+)\s*saat\s*sonra", mt): return int(m_saat.group(1)) * 3600
        if "yarım saat" in mt: return 1800
        return 60

    def roket_yt_müzik(self, sarki): return f"https://duckduckgo.com/?q=!ducky+site%3Ayoutube.com+{urllib.parse.quote(sarki)}"
    def cimbiz_sc(self, sarki):
        url = f"https://soundcloud.com/search?q={urllib.parse.quote(sarki)}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req, timeout=4).read().decode('utf-8', errors='ignore')
            if esl := re.search(r'<li><a href="(/[^"/]+/[^"/]+)">', html): return f"https://soundcloud.com{esl.group(1)}"
        except Exception: pass
        return f"https://soundcloud.com/search/sounds?q={urllib.parse.quote(sarki)}"


class MikuAppGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.hafiza = SynapseMemory()
        self.beyin = GodModeBrain(self.hafiza)
        self.geometry("560x720")
        self.configure(fg_color="#02040a")
        ctk.set_appearance_mode("dark")

        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 185)
        except Exception: self.tts = None

        # ★ MÜHENDİSLİK SEÇİMİ: Kurulum bitti mi?
        if not self.hafiza.veri.get("kurulum_tamamlandi", False):
            self.kurulum_sihirbazini_ac()
        else:
            self.ana_karargahi_kur()

    # =====================================================================
    # 1. KURULUM SİHİRBAZI EKRANI (FIRST RUN WIZARD)
    # =====================================================================
    def kurulum_sihirbazini_ac(self):
        self.title("M.I.K.U. // SİSTEM KURULUM SİHİRBAZI")
        self.setup_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.setup_frame.pack(fill="both", expand=True, padx=35, pady=40)

        ctk.CTkLabel(self.setup_frame, text="⚡ M.I.K.U. ÇEKİRDEK KURULUMU", font=("Consolas", 22, "bold"), text_color="#39C5BB").pack(pady=(10, 20))
        ctk.CTkLabel(self.setup_frame, text="Sistem yeni bir ana bilgisayar tespit etti.\nLütfen siber kimliğinizi tanımlayın:", font=("Consolas", 13), text_color="gray").pack(pady=(0, 25))

        ctk.CTkLabel(self.setup_frame, text="Patron Kod Adınız:", font=("Consolas", 13, "bold")).pack(anchor="w", pady=(10, 2))
        self.ent_isim = ctk.CTkEntry(self.setup_frame, placeholder_text="Örn: Efe Elite-Dev", height=40, fg_color="#0f172a")
        self.ent_isim.pack(fill="x")

        ctk.CTkLabel(self.setup_frame, text="Sesli Uyandırma Kelimesi (Küçük harf):", font=("Consolas", 13, "bold")).pack(anchor="w", pady=(15, 2))
        self.ent_wake = ctk.CTkEntry(self.setup_frame, placeholder_text="Örn: hey miku", height=40, fg_color="#0f172a")
        self.ent_wake.pack(fill="x")

        btn = ctk.CTkButton(self.setup_frame, text="KURULUMU MÜHÜRLE VE BAŞLAT 🚀", height=48, fg_color="#39C5BB", text_color="black", font=("Consolas", 14, "bold"), command=self.kurulumu_kaydet)
        btn.pack(pady=40, fill="x")

    def kurulumu_kaydet(self):
        isim = self.ent_isim.get().strip() or "Efe"
        wake = self.ent_wake.get().strip().lower() or "hey miku"

        self.hafiza.veri["patron"] = isim
        self.hafiza.veri["uyandirma_kelimesi"] = wake
        self.hafiza.veri["kurulum_tamamlandi"] = True
        self.hafiza.kaydet()

        self.setup_frame.destroy() # Sihirbazı yok et
        self.ana_karargahi_kur()   # Karargahı canlandır!

    # =====================================================================
    # 2. ANA KARARGAH EKRANI (DASHBOARD)
    # =====================================================================
    def ana_karargahi_kur(self):
        self.title(f"M.I.K.U. // APEX v6.3 ({self.hafiza.veri['patron']})")
        
        self.telemetri_bar = ctk.CTkLabel(self, text="⚡ SİNAPS DEVREDE", fg_color="#0f172a", text_color="#39C5BB", font=("Consolas", 11, "bold"), corner_radius=6)
        self.telemetri_bar.pack(pady=(12, 0), padx=15, fill="x")

        self.ses_animasyon = ctk.CTkProgressBar(self, mode="indeterminate", fg_color="#0f172a", progress_color="#eab308", height=4)
        self.ses_animasyon.pack(pady=(2, 4), padx=15, fill="x")
        self.ses_animasyon.set(0)

        self.chat_box = ctk.CTkTextbox(self, fg_color="#080c14", text_color="#38bdf8", font=("Consolas", 13), wrap="word", corner_radius=10, border_color="#eab308", border_width=1)
        self.chat_box.pack(pady=5, padx=15, fill="both", expand=True)
        
        self.log_bas(f"=== M.I.K.U. KARARGAH v6.3 DEVREDE ===\nPatron: {self.hafiza.veri['patron']}\nAktif Uyandırma Şifresi: '{self.hafiza.veri['uyandirma_kelimesi']}'\nOTA Hayalet Radar: Arka planda GitHub tarıyor...\n--------------------------------------------------\n")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=(5, 15), padx=15, fill="x")

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Komut satırı...", fg_color="#0f172a", text_color="white", font=("Consolas", 13), height=42, corner_radius=8)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.tetik_baslat())

        ctk.CTkButton(self.input_frame, text="ATEŞLE", width=85, height=42, fg_color="#eab308", text_color="black", font=("Consolas", 13, "bold"), command=self.tetik_baslat).pack(side="right")

        self.telemetri_canlandir()
        threading.Thread(target=self.pasif_ses_pususu, daemon=True).start()
        threading.Thread(target=self.ota_guncelleme_tarayici, daemon=True).start() # ★ OTA THREAD

    # --- GİTHUB OTA HAYALET RADARI ---
    def ota_guncelleme_tarayici(self):
        if "SENIN-REPO-ADIN" in GITHUB_REPO: return
        time.sleep(3) # Arayüz tam otursun
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                uzak_surum = data.get("tag_name", "")
                if uzak_surum and uzak_surum != YEREL_SURUM:
                    self.guncelleme_balonu_izdusumu(uzak_surum, data.get("html_url"))
        except Exception: pass

    def guncelleme_balonu_izdusumu(self, yeni_ver, link):
        banner = ctk.CTkFrame(self, fg_color="#ca8a04", corner_radius=8)
        banner.pack(fill="x", padx=15, pady=5, before=self.chat_box)
        ctk.CTkLabel(banner, text=f"🚀 YENİ SÜRÜM ÇIKTI ({yeni_ver})! GitHub vitrininde seni bekliyor.", font=("Consolas", 12, "bold"), text_color="black").pack(side="left", padx=10, pady=8)
        ctk.CTkButton(banner, text="İNDİR", width=65, fg_color="black", text_color="white", font=("Consolas", 11, "bold"), command=lambda: webbrowser.open(link)).pack(side="right", padx=10, pady=4)

    def telemetri_canlandir(self):
        def g():
            while True:
                try: self.telemetri_bar.configure(text=f"👑 {self.beyin.sistem_telemetrisi_al()}"); time.sleep(1)
                except Exception: pass
        threading.Thread(target=g, daemon=True).start()

    def log_bas(self, m): self.chat_box.configure(state="normal"); self.chat_box.insert("end", m); self.chat_box.configure(state="disabled"); self.chat_box.see("end")
    def ses_bas(self, m):
        t = re.sub(r"[^\w\s.,?!]", "", m)
        if self.tts and t.strip():
            try: self.tts.say(t[:150]); self.tts.runAndWait()
            except Exception: pass

    def hayalet_dirilis(self):
        try: self.deiconify(); self.lift(); self.focus_force(); self.attributes('-topmost', True); self.attributes('-topmost', False)
        except Exception: pass

    def tetik_baslat(self):
        m = self.entry.get().strip()
        if not m: return
        self.entry.delete(0, "end"); self.log_bas(f"[{self.hafiza.veri['patron']}] >>> {m}\n")
        threading.Thread(target=self.emir_isleyici, args=(m,), daemon=True).start()

    def emir_isleyici(self, komut):
        self.hafiza.komut_islenildi()
        if "panik" in komut.lower():
            ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0); ctypes.windll.user32.keybd_event(0x44, 0, 0, 0); ctypes.windll.user32.keybd_event(0x44, 0, 2, 0); ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)
            subprocess.Popen("notepad", shell=True, creationflags=subprocess.CREATE_NO_WINDOW); return

        niyet, hedef = self.beyin.niyet_analiz_et(komut)
        yanit = ""

        # ★★★ DONANIMSAL MEDYA KANCASI (Çal/Durdur) ★★★
        if niyet == "MEDYA_DURDUR":
            ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0) # 0xB3 = VK_MEDIA_PLAY_PAUSE
            ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0)
            yanit = "Sistem medya kancası tetiklendi (Oynat/Durdur sinyali gönderildi)."

        elif niyet == "KAPAT":
            if "iptal" in komut.lower(): os.system("shutdown /a"); yanit = "🔴 Kapatma iptal edildi!"
            else: sn = self.beyin.kapatma_saniyesi_hesapla(komut); os.system(f"shutdown /s /t {sn}"); yanit = f"⚠️ Sistem {sn//60} dk sonra kapanacak."

        elif niyet == "MUZIK":
            sarki = hedef if hedef else "Hatsune Miku World is Mine"
            url = self.beyin.cimbiz_sc(sarki) if "soundcloud" in komut.lower() else self.beyin.roket_yt_müzik(sarki)
            yanit = f"Müzik roketlendi: '{sarki}'"; webbrowser.open(url)

        elif niyet == "HESAP": yanit = "Bulut hesap terminali açıldı."; webbrowser.open("https://hesapmakinesi.com")
        elif niyet == "UYGULAMA": app = hedef if hedef else "notepad"; yanit = f"Kernel Popen -> '{app}'"; subprocess.Popen(app, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        elif niyet == "DIVA": yanit = "Diva aktif."; os.chdir(r"D:\Oyunlar\Project DIVA Arcade"); subprocess.Popen("start diva.exe", shell=True)
        elif niyet == "TEMIZLE": self.chat_box.configure(state="normal"); self.chat_box.delete("1.0", "end"); self.chat_box.configure(state="disabled"); yanit = "Ekran temiz."
        elif niyet == "DURUM": yanit = self.beyin.sistem_telemetrisi_al()
        elif niyet == "BULUT_SOHBET": self.telemetri_bar.configure(text="⚡ [BULUT] DÜŞÜNÜYOR..."); yanit = self.beyin.bulut_bilgesine_danis(komut)

        self.log_bas(f"[M.I.K.U.] >>> {yanit}\n\n"); self.ses_bas(yanit)

    def pasif_ses_pususu(self):
        r = sr.Recognizer(); r.energy_threshold = 300; r.dynamic_energy_threshold = True
        wake = self.hafiza.veri.get("uyandirma_kelimesi", "hey miku").lower()

        with sr.Microphone() as kynk:
            r.adjust_for_ambient_noise(kynk, duration=1.0)
            while True:
                try:
                    ses = r.listen(kynk, phrase_time_limit=4)
                    t = r.recognize_google(ses, language="tr-TR").lower()
                    
                    if wake in t or "miku" in t:
                        self.hayalet_dirilis()
                        kalan = t.split(wake)[-1].strip() if wake in t else ""
                        if len(kalan) > 2:
                            self.log_bas(f"[🎙️ Hızlı] >>> {kalan}\n"); threading.Thread(target=self.emir_isleyici, args=(kalan,), daemon=True).start(); continue
                            
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)
                        self.ses_animasyon.start(); self.telemetri_bar.configure(text_color="#eab308")
                        try:
                            k_ses = r.listen(kynk, timeout=4, phrase_time_limit=6)
                            self.ses_animasyon.stop(); self.telemetri_bar.configure(text_color="#39C5BB")
                            k_mtn = r.recognize_google(k_ses, language="tr-TR")
                            self.log_bas(f"[🎙️ Komut] >>> {k_mtn}\n"); threading.Thread(target=self.emir_isleyici, args=(k_mtn,), daemon=True).start()
                        except (sr.WaitTimeoutError, sr.UnknownValueError):
                            self.ses_animasyon.stop(); self.telemetri_bar.configure(text_color="#39C5BB")
                            self.ses_bas("Pardon patron, sesini duyamadım.")
                except Exception: pass

if __name__ == "__main__":
    app = MikuAppGUI()
    app.mainloop()
