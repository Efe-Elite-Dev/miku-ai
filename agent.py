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


class OmniSovereignBrain:
    def __init__(self, hafiza_ref):
        self.hafiza = hafiza_ref
        self.yerel_intents = {
            "MUZIK": ["çal", "şarkı", "müzik", "dinle", "oynat", "parça", "aç"],
            "HESAP": ["hesap", "makine", "topla", "çıkar", "çarp", "böl", "matematik"],
            "UYGULAMA": ["çalıştır", "program", "uygulama", "notepad", "defteri", "cmd", "exe"],
            "DIVA": ["diva", "project", "arcade", "hatsune"],
            "TEMIZLE": ["temizle", "sil", "ekran", "log", "clear", "cls"],
            "DURUM": ["durum", "rapor", "telemetri", "sistem", "bilgi", "saat", "tarih", "hafıza"],
            "KAPAT": ["kapat", "kapan", "söndür", "uykuya", "yatır", "fişi"] # ★ YENİ NİYET
        }
        self.cop_kelimeler = {"bir", "bana", "şu", "ve", "ile", "lütfen", "hey", "miku", "efe", "abi", "açsana", "çalsana", "yapsana"}

    def sistem_telemetrisi_al(self):
        simdi = datetime.datetime.now().strftime("%H:%M:%S // %d.%m.%Y")
        os_bilgi = f"{platform.system()} {platform.release()} ({platform.machine()})"
        return f"Saat: {simdi} | İşletim Sistemi: {os_bilgi} | İşlenen Toplam Emir: {self.hafiza.veri['toplam_komut']}"

    def bulut_bilgesine_danis(self, soru):
        sistem_kimligi = f"Senin adın M.I.K.U. Sahibin {self.hafiza.veri['patron']}. Sen Windows çekirdeğinde yaşayan fütüristik, zeki, alaycı yapay zeka kızısın. Sistem telemetrin: {self.sistem_telemetrisi_al()}."
        tam_prompt = f"{sistem_kimligi}\n\nKullanıcı Soru: {soru}"
        url = f"https://text.pollinations.ai/prompt/{urllib.parse.quote(tam_prompt)}?model=gpt-4o-mini"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
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

    # ★ SİBER ZAMAN CIMBIZI (Göreceli ve Mutlak Türkçe Saat Çözücü)
    def kapatma_saniyesi_hesapla(self, metin):
        mt = metin.lower()
        
        # 1. Göreceli: "20 dakika sonra", "15 dk"
        m_dk = re.search(r"(\d+)\s*(?:dakika|dk)", mt)
        if m_dk: return int(m_dk.group(1)) * 60

        m_saat = re.search(r"(\d+)\s*saat\s*sonra", mt)
        if m_saat: return int(m_saat.group(1)) * 3600

        if "yarım saat" in mt: return 1800
        if "çeyrek saat" in mt: return 900

        # 2. Mutlak: "saat 02:30", "2:30", "02.45"
        m_abs = re.search(r"(\d{1,2})[:.](\d{2})", mt)
        if m_abs:
            h, m = int(m_abs.group(1)), int(m_abs.group(2))
            simdi = datetime.datetime.now()
            hedef = simdi.replace(hour=h, minute=m, second=0, microsecond=0)
            if hedef <= simdi: hedef += datetime.timedelta(days=1)
            return int((hedef - simdi).total_seconds())

        # 3. Düz saat: "saat 3te kapat"
        m_tek = re.search(r"saat\s*(\d{1,2})", mt)
        if m_tek:
            h = int(m_tek.group(1))
            simdi = datetime.datetime.now()
            hedef = simdi.replace(hour=h, minute=0, second=0, microsecond=0)
            if hedef <= simdi: hedef += datetime.timedelta(days=1)
            return int((hedef - simdi).total_seconds())

        return 60 # Hiçbir süre söylemezse 60 sn verip uyarsın (iptal şansı olsun)

    def roket_yt_müzik(self, sarki): return f"https://duckduckgo.com/?q=!ducky+site%3Ayoutube.com+{urllib.parse.quote(sarki)}"
    def cimbiz_sc(self, sarki):
        url = f"https://soundcloud.com/search?q={urllib.parse.quote(sarki)}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req, timeout=4).read().decode('utf-8', errors='ignore')
            esl = re.search(r'<li><a href="(/[^"/]+/[^"/]+)">', html)
            if esl: return f"https://soundcloud.com{esl.group(1)}"
        except Exception: pass
        return f"https://soundcloud.com/search/sounds?q={urllib.parse.quote(sarki)}"


class MikuOmniGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.hafiza = SynapseMemory()
        self.beyin = OmniSovereignBrain(self.hafiza)
        self.title(f"M.I.K.U. // OMNI-SOVEREIGN v5.1 (Dead Man's Switch)")
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
        self.telemetri_bar = ctk.CTkLabel(self, text="⚡ SİNAPS BAĞLANIYOR...", fg_color="#111827", text_color="#39C5BB", font=("Consolas", 11, "bold"), corner_radius=6)
        self.telemetri_bar.pack(pady=(12, 4), padx=15, fill="x")

        self.chat_box = ctk.CTkTextbox(self, fg_color="#0b0f19", text_color="#38bdf8", font=("Consolas", 13), wrap="word", corner_radius=10, border_color="#39C5BB", border_width=1)
        self.chat_box.pack(pady=5, padx=15, fill="both", expand=True)
        self.log_bas(f"=== M.I.K.U. OMNI v5.1 YÜKLENDİ ===\nPatron: {self.hafiza.veri['patron']}\nGece Bekçisi: Aktif (Kernel Delegation Shutdown API)\n--------------------------------------------------\n")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=(5, 15), padx=15, fill="x")

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="M.I.K.U. v5.1 Emir satırı...", fg_color="#111827", text_color="white", font=("Consolas", 13), height=42, corner_radius=8)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.tetik_baslat())

        self.btn = ctk.CTkButton(self.input_frame, text="ATEŞLE", width=85, height=42, corner_radius=8, fg_color="#39C5BB", hover_color="#14b8a6", text_color="black", font=("Consolas", 13, "bold"), command=self.tetik_baslat)
        self.btn.pack(side="right")

    def telemetri_canlandir(self):
        def g():
            while True:
                try: self.telemetri_bar.configure(text=f"🟢 {self.beyin.sistem_telemetrisi_al()}"); time.sleep(1)
                except Exception: pass
        threading.Thread(target=g, daemon=True).start()

    def log_bas(self, metin): self.chat_box.configure(state="normal"); self.chat_box.insert("end", metin); self.chat_box.configure(state="disabled"); self.chat_box.see("end")
    def ses_bas(self, metin):
        temiz = re.sub(r"[^\w\s.,?!]", "", metin)
        if self.tts and temiz.strip():
            try: self.tts.say(temiz[:150]); self.tts.runAndWait()
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
        niyet, hedef = self.beyin.niyet_analiz_et(komut)
        yanit = ""

        if niyet == "KAPAT":
            # GÜVENLİK SİGORTASI: "müzik kapat" dediyse bilgisayarı söndürmesin
            if any(w in komut.lower() for w in ["müzik", "şarkı", "uygulama", "sekme", "site", "diva"]):
                yanit = "Sadece komple sistemin fişini çekebilirim patron, alt pencereleri sen kapat."
            elif any(k in komut.lower() for k in ["iptal", "dur", "vazgeç", "boz"]):
                os.system("shutdown /a")
                yanit = "🔴 [DEAD MAN'S SWITCH]: Kapatma tetiği çekirdekten iptal edildi!"
            else:
                saniye = self.beyin.kapatma_saniyesi_hesapla(komut)
                dk = saniye // 60
                os.system(f"shutdown /s /t {saniye}")
                yanit = f"⚠️ [DEAD MAN'S SWITCH ATEŞLENDİ]\nWindows çekirdeğine {saniye} saniye ({dk} dakika) sonra ölüm emri verildi.\n(İptal etmek için: 'kapatmayı iptal et' yaz)"

        elif niyet == "MUZIK":
            sarki = hedef if hedef else "Hatsune Miku World is Mine"
            url = self.beyin.cimbiz_sc(sarki) if "soundcloud" in komut.lower() else self.beyin.roket_yt_müzik(sarki)
            yanit = f"Müzik frekansı ateşlendi: '{sarki}'"
            webbrowser.open(url)

        elif niyet == "HESAP": yanit = "Bulut hesap terminali açıldı."; webbrowser.open("https://hesapmakinesi.com")
        elif niyet == "UYGULAMA": app = hedef if hedef else "notepad"; yanit = f"Kernel Popen -> '{app}'"; subprocess.Popen(app, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        elif niyet == "DIVA": yanit = "Diva aktif."; os.chdir(r"D:\Oyunlar\Project DIVA Arcade"); subprocess.Popen("start diva.exe", shell=True)
        elif niyet == "TEMIZLE": self.chat_box.configure(state="normal"); self.chat_box.delete("1.0", "end"); self.chat_box.configure(state="disabled"); yanit = "Ekran temiz."
        elif niyet == "DURUM": yanit = self.beyin.sistem_telemetrisi_al()
        elif niyet == "BULUT_SOHBET": self.telemetri_bar.configure(text="⚡ [BULUT SİNAPSI] M.I.K.U. DÜŞÜNÜYOR..."); yanit = self.beyin.bulut_bilgesine_danis(komut)

        self.log_bas(f"[M.I.K.U.] >>> {yanit}\n\n"); self.ses_bas(yanit)

    def pasif_ses_pususu(self):
        r = sr.Recognizer()
        with sr.Microphone() as kynk:
            r.adjust_for_ambient_noise(kynk, duration=1.0)
            while True:
                try:
                    ses = r.listen(kynk, phrase_time_limit=2.5)
                    t = r.recognize_google(ses, language="tr-TR").lower()
                    if any(x in t for x in ["miku", "hey miku", "heymiku"]):
                        self.hayalet_dirilis(); self.ses_bas("Emret patron?")
                        k_ses = r.listen(kynk, phrase_time_limit=6)
                        k_mtn = r.recognize_google(k_ses, language="tr-TR")
                        self.log_bas(f"[🎙️ Sesli Giriş] >>> {k_mtn}\n")
                        threading.Thread(target=self.emir_isleyici, args=(k_mtn,), daemon=True).start()
                except Exception: pass

if __name__ == "__main__":
    app = MikuOmniGUI()
    app.mainloop()
