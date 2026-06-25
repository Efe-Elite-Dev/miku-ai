import ctypes
import math
import os
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
# 1. YÖNETİCİ İZNİ KALKANI (HER AÇILIŞTA UAC ELEVATION)
# =====================================================================
def uac_yönetici_izin_kalkani():
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
    except Exception: pass

uac_yönetici_izin_kalkani()

# --- Noconsole Hayalet Akış Koruması ---
if sys.stdin is None: sys.stdin = open(os.devnull, "r")
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")


# =====================================================================
# ★ EFE ELİTE-DEV // OTO-BAŞLATMALI YAPAY ZEKA BEYNİ (v4.1)
# =====================================================================
class EliteDevApexBrain:
    def __init__(self):
        self.intents = {
            "MUZIK": ["çal", "şarkı", "müzik", "dinle", "oynat", "parça", "koy", "aç"],
            "HESAP": ["hesap", "makine", "topla", "çıkar", "çarp", "böl", "matematik", "hesapla"],
            "UYGULAMA": ["çalıştır", "program", "uygulama", "notepad", "defteri", "cmd", "exe", "yazı"],
            "DIVA": ["diva", "project", "arcade", "hatsune", "future", "tone"],
            "TEMIZLE": ["temizle", "sil", "ekran", "log", "clear", "cls", "pırıl"],
            "SOHBET": ["merhaba", "selam", "naber", "nasılsın", "kimsin", "miku", "hey", "sa"]
        }

        self.cop_kelimeler = {
            "bir", "bana", "şu", "ve", "ile", "mi", "mı", "mu", "mü", "lütfen", 
            "da", "de", "hey", "miku", "heymiku", "dan", "den", "yı", "yi", "ya",
            "nu", "nü", "şarkısını", "uygulaması", "eder", "misin", "mısın", "efe",
            "abi", "istiyorum", "açsana", "çalsana", "yapsana", "sana", "koysana", "soundcloud", "tan"
        }

        self.sohbet_cevaplari = {
            "merhaba": "Selam Efe. Tam Yönetici yetkisiyle arkandayım.",
            "selam": "Frekans alındı patron.",
            "naber": "Çekirdek yetkilerim maksimumda. Emir bekliyorum.",
            "nasılsın": "Sistem voltajım jilet gibi. Sen nasılsın?",
            "kimsin": "Ben Efe Elite-Dev tarafından dövülmüş %100 otonom bir siber ajansım."
        }

    def turkce_kok_eslesti_mi(self, u_kelimeler, havuz_kelimeleri):
        skor = 0
        for u in u_kelimeler:
            if u in self.cop_kelimeler: continue
            for h in havuz_kelimeleri:
                if u.startswith(h) or h.startswith(u):
                    skor += 1
                    break
        return skor

    def karar_ver(self, kullanici_metni):
        metin = kullanici_metni.lower()
        temiz_kelimeler = re.findall(r"\w+", metin)
        
        en_iyi_skor = 0
        secilen_niyet = "SOHBET"

        for niyet, havuz in self.intents.items():
            skor = self.turkce_kok_eslesti_mi(temiz_kelimeler, havuz)
            if skor > en_iyi_skor:
                en_iyi_skor = skor
                secilen_niyet = niyet

        hedef_kalanlar = [k for k in temiz_kelimeler if not any(k.startswith(h) for h in self.intents[secilen_niyet])]
        hedef_obje = " ".join([x for x in hedef_kalanlar if x not in self.cop_kelimeler])

        return secilen_niyet, hedef_obje

    # ★ SİBER ROKET: YOUTUBE NATIVE AUTOPLAY TUNNEL
    def aninda_calan_muzik_roketle(self, sarki_adi):
        """DuckDuckGo '!ducky' bang'i ile tarayıcıyı doğrudan şarkının saniyesinde çalan Youtube adresine zıplatır"""
        temiz_sorgu = urllib.parse.quote(f"{sarki_adi}")
        return f"https://duckduckgo.com/?q=!ducky+site%3Ayoutube.com+{temiz_sorgu}"

    def direkt_sc_linki_cimbizla(self, sarki_adi):
        url = f"https://soundcloud.com/search?q={urllib.parse.quote(sarki_adi)}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8', errors='ignore')
            esl = re.search(r'<li><a href="(/[^"/]+/[^"/]+)">', html)
            if esl: return f"https://soundcloud.com{esl.group(1)}"
        except Exception: pass
        return f"https://soundcloud.com/search/sounds?q={urllib.parse.quote(sarki_adi)}"


class MikuApexGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("M.I.K.U. // APEX SOVEREIGN v4.1 (Instant Autoplay)")
        self.geometry("540x700")
        self.configure(fg_color="#040811")
        ctk.set_appearance_mode("dark")

        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 185)
        except Exception: self.tts = None

        self.beyin = EliteDevApexBrain()
        self.arayuzu_kur()
        threading.Thread(target=self.pasif_ses_pususu, daemon=True).start()

    def arayuzu_kur(self):
        self.status_bar = ctk.CTkLabel(self, text="🟢 M.I.K.U. v4.1 // ANINDA OYNATMA ZIRHI AKTİF", 
                                       fg_color="#0d1526", text_color="#39C5BB", font=("Consolas", 12, "bold"), corner_radius=8)
        self.status_bar.pack(pady=(15, 5), padx=15, fill="x")

        self.chat_box = ctk.CTkTextbox(self, fg_color="#080c18", text_color="#00b4d8", font=("Consolas", 13), 
                                       wrap="word", corner_radius=10, border_color="#39C5BB", border_width=1)
        self.chat_box.pack(pady=5, padx=15, fill="both", expand=True)
        self.log_bas("=== M.I.K.U. APEX SOVEREIGN v4.1 YÜKLENDİ ===\nPatron: Efe Elite-Dev\nHotfix: Müzik talep edildiğinde tarayıcı kilitleri baypas edilip %100 otomatik oynatma tetiklenir.\n--------------------------------------------------\n")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=(5, 15), padx=15, fill="x")

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Komut yaz veya 'Hey Miku' de...", 
                                  fg_color="#0d1526", text_color="white", font=("Consolas", 13), height=40, corner_radius=8)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.gonder_tetik())

        self.btn_send = ctk.CTkButton(self.input_frame, text="İLET", width=80, height=40, corner_radius=8,
                                      fg_color="#39C5BB", hover_color="#208b84", text_color="black", font=("Consolas", 13, "bold"),
                                      command=self.gonder_tetik)
        self.btn_send.pack(side="right")

    def log_bas(self, metin):
        self.chat_box.configure(state="normal"); self.chat_box.insert("end", metin); self.chat_box.configure(state="disabled"); self.chat_box.see("end")

    def ses_bas(self, metin):
        if self.tts and metin.strip():
            try: self.tts.say(metin); self.tts.runAndWait()
            except Exception: pass

    def hayalet_dirilis_yap(self):
        try:
            self.deiconify(); self.lift(); self.focus_force()
            self.attributes('-topmost', True); self.attributes('-topmost', False)
        except Exception: pass

    def gonder_tetik(self):
        metin = self.entry.get().strip()
        if not metin: return
        self.entry.delete(0, "end")
        self.log_bas(f"[Efe Elite-Dev] >>> {metin}\n")
        threading.Thread(target=self.motoru_calistir, args=(metin,), daemon=True).start()

    def motoru_calistir(self, komut):
        niyet, hedef = self.beyin.karar_ver(komut)
        self.log_bas(f"[KERNEL NLP] -> Tespit: {niyet} | Hedef: '{hedef}'\n")

        yanit = ""

        if niyet == "MUZIK":
            sarki = hedef if hedef else "Hatsune Miku World is Mine"
            
            # Eğer cümlede özellikle "soundcloud" kelimesi geçiyorsa orayı açar (ama pause başlar)
            if "soundcloud" in komut.lower():
                self.status_bar.configure(text="⚡ [SNIPER] SOUNDCLOUD LİNKİ ÇEKİLİYOR...")
                sc_url = self.beyin.direkt_sc_linki_cimbizla(sarki)
                yanit = f"SoundCloud '{sarki}' açıldı (Play'e basman gerekebilir)."
                webbrowser.open(sc_url)
            else:
                # Sadece "müzik çal", "şarkı aç" dendiyse YOUTUBE AUTOPLAY roketini ateşler!
                self.status_bar.configure(text="⚡ [AUTOPLAY] YOUTUBE SES ROKETİ ATEŞLENİYOR...")
                yt_oto_url = self.beyin.aninda_calan_muzik_roketle(sarki)
                yanit = f"'{sarki}' %100 otomatik çalmak üzere ateşlendi patron!"
                webbrowser.open(yt_oto_url)

        elif niyet == "HESAP":
            yanit = "Hesap makinesi bulut terminaline yönlendirildi."
            webbrowser.open("https://hesapmakinesi.com")

        elif niyet == "UYGULAMA":
            app = hedef if hedef else "notepad"
            yanit = f"Windows çekirdeğine '{app}' emri verildi."
            subprocess.Popen(app, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

        elif niyet == "DIVA":
            yanit = "Project DIVA 60FPS mühürü ateşlendi."
            try: os.chdir(r"D:\Oyunlar\Project DIVA Arcade"); subprocess.Popen("start diva.exe", shell=True)
            except Exception as e: yanit = f"Diva Hatası: {e}"

        elif niyet == "TEMIZLE":
            self.chat_box.configure(state="normal"); self.chat_box.delete("1.0", "end"); self.chat_box.configure(state="disabled")
            yanit = "Terminal temizlendi."

        elif niyet == "SOHBET":
            for k_an, k_cvp in self.beyin.sohbet_cevaplari.items():
                if k_an in komut.lower(): yanit = k_cvp; break
            if not yanit: yanit = "Frekans anlaşılmadı. (Müzik aç, hesap makinesi de ya da uygulama adı söyle)"

        self.log_bas(f"[M.I.K.U.] >>> {yanit}\n\n")
        self.status_bar.configure(text="🟢 M.I.K.U. v4.1 // ANINDA OYNATMA ZIRHI AKTİF")
        self.ses_bas(yanit)

    def pasif_ses_pususu(self):
        r = sr.Recognizer()
        with sr.Microphone() as kaynak:
            r.adjust_for_ambient_noise(kaynak, duration=1.0)
            while True:
                try:
                    ses = r.listen(kaynak, phrase_time_limit=2.5)
                    tetik = r.recognize_google(ses, language="tr-TR").lower()
                    if any(x in tetik for x in ["miku", "hey miku", "heymiku", "miko", "mikü"]):
                        self.hayalet_dirilis_yap()
                        self.status_bar.configure(text="🎙️ M.I.K.U. DİNLİYOR // SÖYLE PATRON...")
                        self.ses_bas("Efendim patron?")
                        k_ses = r.listen(kaynak, phrase_time_limit=6)
                        k_metin = r.recognize_google(k_ses, language="tr-TR")
                        self.log_bas(f"[🎙️ Sesli Komut] >>> {k_metin}\n")
                        threading.Thread(target=self.motoru_calistir, args=(k_metin,), daemon=True).start()
                except Exception: pass

if __name__ == "__main__":
    app = MikuApexGUI()
    app.mainloop()
