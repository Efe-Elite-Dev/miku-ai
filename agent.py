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
# ★★★ UYANDIRMA KELİMELERİNİ BURADAN İSTEDİĞİN GİBİ DEĞİŞTİR ★★★
# =====================================================================
UYANDIRMA_KELIMELERI = ["hey miku", "heymiku", "miku", "sistem uyan", "uyan"]


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
            "rutbe": "God-Mode Architect",
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
            "HESAP": ["hesap", "makine", "topla", "çıkar", "çarp", "böl", "matematik", "hesapla"],
            "UYGULAMA": ["çalıştır", "program", "uygulama", "notepad", "defteri", "cmd", "exe"],
            "DIVA": ["diva", "project", "arcade", "hatsune"],
            "TEMIZLE": ["temizle", "sil", "ekran", "log", "clear", "cls"],
            "DURUM": ["durum", "rapor", "telemetri", "sistem", "bilgi", "saat", "tarih"],
            "KAPAT": ["kapat", "kapan", "söndür", "uykuya", "yatır", "fişi"],
            "PANIK": ["panik", "gizle", "sakla", "kurtar", "tehlike", "kapat"]
        }
        self.cop_kelimeler = {"bir", "bana", "şu", "ve", "ile", "lütfen", "hey", "miku", "efe", "abi", "açsana", "çalsana", "yapsana"}

    def sistem_telemetrisi_al(self):
        simdi = datetime.datetime.now().strftime("%H:%M:%S // %d.%m.%Y")
        os_bilgi = f"{platform.system()} {platform.release()}"
        return f"Saat: {simdi} | OS: {os_bilgi} | Emir: {self.hafiza.veri['toplam_komut']}"

    def bulut_bilgesine_danis(self, soru):
        sistem_kimligi = f"Senin adın M.I.K.U. Sahibin {self.hafiza.veri['patron']}. Sen fütüristik, zeki, alaycı yapay zeka kızısın. Efe Türkçe'yi inanılmaz hızlı, heyecanlı ve bazen harfleri atlayarak yazar. Bu yüzden cümleleri bozuk olsa bile ne demek istediğini anla ve ona bir siber-ortağı gibi mükemmel cevap ver. Sistem telemetrin: {self.sistem_telemetrisi_al()}."
        tam_prompt = f"{sistem_kimligi}\n\nKullanıcı Soru: {soru}"
        url = f"https://text.pollinations.ai/prompt/{urllib.parse.quote(tam_prompt)}?model=gpt-4o-mini"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=7) as r: return r.read().decode('utf-8')
        except Exception: return "Bulut sinapsım koptu patron."

    def niyet_analiz_et(self, metin):
        temiz = re.findall(r"\w+", metin.lower())
        skorlar = {}
        for niyet, havuz in self.yerel_intents.items():
            s = 0
            for k in temiz:
                if k in self.cop_kelimeler: continue
                yakin_mi = difflib.get_close_matches(k, havuz, n=1, cutoff=0.70)
                if yakin_mi or any(k.startswith(h) for h in havuz):
                    s += 1
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
        if "çeyrek saat" in mt: return 900
        if m_abs := re.search(r"(\d{1,2})[:.](\d{2})", mt):
            h, m = int(m_abs.group(1)), int(m_abs.group(2))
            s = datetime.datetime.now(); hdf = s.replace(hour=h, minute=m, second=0)
            if hdf <= s: hdf += datetime.timedelta(days=1)
            return int((hdf - s).total_seconds())
        if m_tek := re.search(r"saat\s*(\d{1,2})", mt):
            h = int(m_tek.group(1))
            s = datetime.datetime.now(); hdf = s.replace(hour=h, minute=0, second=0)
            if hdf <= s: hdf += datetime.timedelta(days=1)
            return int((hdf - s).total_seconds())
        return 60

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


class MikuGodGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.hafiza = SynapseMemory()
        self.beyin = GodModeBrain(self.hafiza)
        self.title(f"M.I.K.U. // GOD-MODE v6.2 (UX Overhaul)")
        self.geometry("560x720")
        self.configure(fg_color="#02040a")
        ctk.set_appearance_mode("dark")

        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 185)
        except Exception: self.tts = None

        self.arayuz_kur()
        self.telemetri_canlandir()
        threading.Thread(target=self.pasif_ses_pususu, daemon=True).start()

    def arayuz_kur(self):
        self.telemetri_bar = ctk.CTkLabel(self, text="⚡ TANRI MODU BAŞLATILIYOR...", fg_color="#0f172a", text_color="#39C5BB", font=("Consolas", 11, "bold"), corner_radius=6)
        self.telemetri_bar.pack(pady=(12, 0), padx=15, fill="x")

        # ★ SİBER DİNLEME ANİMASYONU (ProgressBar)
        self.ses_animasyon = ctk.CTkProgressBar(self, mode="indeterminate", fg_color="#0f172a", progress_color="#eab308", height=4)
        self.ses_animasyon.pack(pady=(2, 4), padx=15, fill="x")
        self.ses_animasyon.set(0) # Başlangıçta hareketsiz

        self.chat_box = ctk.CTkTextbox(self, fg_color="#080c14", text_color="#38bdf8", font=("Consolas", 13), wrap="word", corner_radius=10, border_color="#eab308", border_width=1)
        self.chat_box.pack(pady=5, padx=15, fill="both", expand=True)
        self.log_bas(f"=== M.I.K.U. GOD-MODE v6.2 YÜKLENDİ ===\nPatron: Efe Elite-Dev\nHotfix: Kinetik Animasyon Barı eklendi.\nHotfix: 'Duyamadım/Anlayamadım' hata blokları yazıldı.\nHotfix: Uyandırma kelimesi serbest bırakıldı.\n--------------------------------------------------\n")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=(5, 15), padx=15, fill="x")

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="GOD-MODE Emir satırı...", fg_color="#0f172a", text_color="white", font=("Consolas", 13), height=42, corner_radius=8)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.tetik_baslat())

        self.btn = ctk.CTkButton(self.input_frame, text="ATEŞLE", width=85, height=42, corner_radius=8, fg_color="#eab308", hover_color="#ca8a04", text_color="black", font=("Consolas", 13, "bold"), command=self.tetik_baslat)
        self.btn.pack(side="right")

    def telemetri_canlandir(self):
        def g():
            while True:
                try: self.telemetri_bar.configure(text=f"👑 {self.beyin.sistem_telemetrisi_al()}"); time.sleep(1)
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
        
        if "panik" in komut.lower() or "tehlike" in komut.lower():
            self.log_bas("[KERNEL] -> 🚨 PANİK PROTOKOLÜ: Her şey gizleniyor!\n\n")
            ctypes.windll.user32.keybd_event(0x5B, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0x44, 0, 0, 0)
            ctypes.windll.user32.keybd_event(0x44, 0, 2, 0)
            ctypes.windll.user32.keybd_event(0x5B, 0, 2, 0)
            subprocess.Popen("notepad", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return

        niyet, hedef = self.beyin.niyet_analiz_et(komut)
        yanit = ""

        if niyet == "KAPAT":
            if any(w in komut.lower() for w in ["müzik", "şarkı", "uygulama", "diva"]): yanit = "Sadece komple sistemin fişini çekebilirim patron."
            elif any(k in komut.lower() for k in ["iptal", "dur", "vazgeç", "boz"]):
                os.system("shutdown /a"); yanit = "🔴 Kapatma tetiği iptal edildi!"
            else:
                saniye = self.beyin.kapatma_saniyesi_hesapla(komut); dk = saniye // 60
                os.system(f"shutdown /s /t {saniye}")
                yanit = f"⚠️ Windows çekirdeğine {dk} dakika sonra ölüm emri verildi. (İptal için: 'kapatmayı iptal et')"

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

    # =====================================================================
    # ★ KUSURSUZ ANİMASYONLU VE HATA AYIKLAMALI SES PROTOKOLÜ
    # =====================================================================
    def pasif_ses_pususu(self):
        r = sr.Recognizer()
        r.energy_threshold = 300 
        r.dynamic_energy_threshold = True

        with sr.Microphone() as kynk:
            r.adjust_for_ambient_noise(kynk, duration=1.0)
            while True:
                try:
                    # 1. Aşama: Arka planda odayı dinle
                    ses = r.listen(kynk, phrase_time_limit=4)
                    t = r.recognize_google(ses, language="tr-TR").lower()
                    
                    if any(x in t for x in UYANDIRMA_KELIMELERI):
                        self.hayalet_dirilis()
                        
                        # Tek nefes kontrolü
                        kalan_komut = t
                        for tetik in UYANDIRMA_KELIMELERI:
                            if tetik in kalan_komut:
                                kalan_komut = kalan_komut.split(tetik)[-1].strip()
                        
                        if len(kalan_komut) > 2:
                            self.log_bas(f"[🎙️ Hızlı Komut] >>> {kalan_komut}\n")
                            threading.Thread(target=self.emir_isleyici, args=(kalan_komut,), daemon=True).start()
                            continue
                            
                        # 2. Aşama: Uyandı ve ikinci komutu bekliyor!
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)
                        
                        # ★ ANİMASYONU BAŞLAT!
                        self.ses_animasyon.start()
                        self.telemetri_bar.configure(text_color="#eab308") # Sararır
                        
                        try:
                            # 6 saniye boyunca konuşmanı bekler
                            k_ses = r.listen(kynk, timeout=4, phrase_time_limit=6)
                            self.ses_animasyon.stop() # ★ ANİMASYONU DURDUR
                            self.telemetri_bar.configure(text_color="#39C5BB") # Yeşile dön
                            
                            k_mtn = r.recognize_google(k_ses, language="tr-TR")
                            self.log_bas(f"[🎙️ İkinci Komut] >>> {k_mtn}\n")
                            threading.Thread(target=self.emir_isleyici, args=(k_mtn,), daemon=True).start()
                            
                        # ★ HATA DURUMLARI (Sen konuşmazsan veya duyamazsa)
                        except sr.WaitTimeoutError:
                            self.ses_animasyon.stop()
                            self.telemetri_bar.configure(text_color="#39C5BB")
                            self.log_bas("[🎙️ Sistem] >>> Ses tespit edilemedi.\n\n")
                            self.ses_bas("Pardon patron, sesini duyamadım.")
                        except sr.UnknownValueError:
                            self.ses_animasyon.stop()
                            self.telemetri_bar.configure(text_color="#39C5BB")
                            self.log_bas("[🎙️ Sistem] >>> Kelimeler anlaşılamadı.\n\n")
                            self.ses_bas("Pardon patron, ne dediğini anlayamadım.")

                # Arka plan dinlemesindeki boş gürültüleri görmezden gel
                except sr.WaitTimeoutError: pass
                except sr.UnknownValueError: pass
                except Exception: pass

if __name__ == "__main__":
    app = MikuGodGUI()
    app.mainloop()
