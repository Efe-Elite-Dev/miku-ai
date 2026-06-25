import math
import os
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
import customtkinter as ctk
import pyttsx3
import speech_recognition as sr

# --- Noconsole Hayalet Akış Koruması ---
if sys.stdin is None: sys.stdin = open(os.devnull, "r")
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")


# =====================================================================
# ★ EFE ELİTE-DEV // SAFKAN VEKTÖR UZAYI YAPAY ZEKA ÇEKİRDEĞİ (v0.1)
# =====================================================================
class EliteDevNLPBrain:
    def __init__(self):
        # Bizim bizzat eğittiğimiz Semantik Niyet Havuzu (Sıfır LLM!)
        self.intents = {
            "MUZIK": ["çal", "şarkı", "müzik", "aç", "dinle", "oynat", "soundcloud", "parça", "koy"],
            "UYGULAMA": ["çalıştır", "program", "uygulama", "hesap", "makinesi", "not", "defteri", "cmd", "exe", "hesapmakinesi"],
            "DIVA": ["diva", "oyun", "project", "arcade", "hatsune", "oynayalım", "future", "tone"],
            "TEMIZLE": ["temizle", "sil", "ekran", "log", "clear", "cls", "pırıl"],
            "SOHBET": ["merhaba", "selam", "naber", "nasılsın", "kimsin", "miku", "hey", "günaydın", "sa"]
        }

        # Cümledeki gereksiz ekleri ve bağlaçları yok eden yerli filtre:
        self.cop_kelimeler = {
            "bir", "bana", "şu", "ve", "ile", "mi", "mı", "mu", "mü", "lütfen", 
            "da", "de", "hey", "miku", "heymiku", "dan", "den", "yı", "yi", 
            "nu", "nü", "şarkısını", "uygulaması", "eder", "misin", "mısın"
        }

        self.sohbet_cevaplari = {
            "merhaba": "Selam Efe. Sistemler online.",
            "selam": "Frekans alındı patron, dinliyorum.",
            "naber": "İşlemci ısım 34 derece. Görev bekliyorum.",
            "nasılsın": "Çekirdek voltajım stabil. Sen nasılsın?",
            "kimsin": "Ben Efe Elite-Dev tarafından sıfırdan kodlanmış yerel bir çekirdeğim.",
            "miku": "Efendim patron?"
        }

    def normalize_et(self, metin):
        metin = metin.lower()
        kelimeler = re.findall(r"\w+", metin)
        return [k for k in kelimeler if k not in self.cop_kelimeler]

    def kosinus_benzerligi_hesapla(self, v1_kelimeler, v2_kelimeler):
        """İşte yapay zeka dediğimiz o milyar dolarlık matematik formülü!"""
        havuz = list(set(v1_kelimeler + v2_kelimeler))
        v1 = [1 if k in v1_kelimeler else 0 for k in havuz]
        v2 = [1 if k in v2_kelimeler else 0 for k in havuz]

        dot = sum(a * b for a, b in zip(v1, v2))
        m1 = math.sqrt(sum(a**2 for a in v1))
        m2 = math.sqrt(sum(b**2 for b in v2))

        return 0.0 if m1 == 0 or m2 == 0 else dot / (m1 * m2)

    def karar_ver(self, kullanici_metni):
        temiz_vektor = self.normalize_et(kullanici_metni)
        
        if not temiz_vektor:
            return "SOHBET", "", 1.0

        en_iyi_skor = 0.0
        secilen_niyet = "SOHBET"

        for niyet, havuz in self.intents.items():
            skor = self.kosinus_benzerligi_hesapla(temiz_vektor, havuz)
            if skor > en_iyi_skor:
                en_iyi_skor = skor
                secilen_niyet = niyet

        # Hedef objeyi (Entity) ayıkla:
        hedef_obje = ""
        if secilen_niyet in ["MUZIK", "UYGULAMA"]:
            # Niyet kelimelerini cümleden çıkar, geriye kalan saf isim bizim hedefimizdir!
            kalanlar = [k for k in temiz_vektor if k not in self.intents[secilen_niyet]]
            hedef_obje = " ".join(kalanlar)

        return secilen_niyet, hedef_obje, en_iyi_skor


class MikuSovereignGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("M.I.K.U. // SOVEREIGN KONSOL v3.0 (Pure Math AI)")
        self.geometry("540x700")
        self.configure(fg_color="#050a14")
        ctk.set_appearance_mode("dark")

        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 185)
        except Exception: self.tts = None

        # BEYNİMİZİ DOĞRUDAN RAM'E KURUYORUZ (Ollama yok, API yok!)
        self.beyin = EliteDevNLPBrain()

        self.arayuzu_kur()
        threading.Thread(target=self.pasif_ses_pususu, daemon=True).start()

    def arayuzu_kur(self):
        self.status_bar = ctk.CTkLabel(self, text="🟢 M.I.K.U. v3.0 // ELİTE-DEV NLP ÇEKİRDEĞİ DEVREDE (0 MB VRAM)", 
                                       fg_color="#101828", text_color="#39C5BB", font=("Consolas", 12, "bold"), corner_radius=8)
        self.status_bar.pack(pady=(15, 5), padx=15, fill="x")

        self.chat_box = ctk.CTkTextbox(self, fg_color="#0a0f1d", text_color="#00b4d8", font=("Consolas", 13), 
                                       wrap="word", corner_radius=10, border_color="#39C5BB", border_width=1)
        self.chat_box.pack(pady=5, padx=15, fill="both", expand=True)
        self.log_bas("=== M.I.K.U. PURE-MATH KERNEL v3.0 YÜKLENDİ ===\nPatron: Efe Elite-Dev\nMimari: Yerel Bag-of-Words & Kosinüs Benzerlik Motoru\nBağımlılıklar: Sıfır (No Ollama, No API, No Cloud)\n--------------------------------------------------\n")

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=(5, 15), padx=15, fill="x")

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Komut yaz veya 'Hey Miku' de...", 
                                  fg_color="#101828", text_color="white", font=("Consolas", 13), height=40, corner_radius=8)
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
        if self.tts and metin.strip():
            try: self.tts.say(metin); self.tts.runAndWait()
            except Exception: pass

    def gonder_tetik(self):
        metin = self.entry.get().strip()
        if not metin: return
        self.entry.delete(0, "end")
        self.log_bas(f"[Efe Elite-Dev] >>> {metin}\n")
        threading.Thread(target=self.motoru_calistir, args=(metin,), daemon=True).start()

    def motoru_calistir(self, komut):
        # 1. BEYİN KARARI AL (Saniyeler değil, mikrosaniyeler sürecek!):
        t0 = time.perf_counter()
        niyet, hedef, skor = self.beyin.karar_ver(komut)
        sure_ms = (time.perf_counter() - t0) * 1000

        self.log_bas(f"[KERNEL NLP] -> Niyet: {niyet} | Hedef: '{hedef}' | Güven: %{int(skor*100)} ({sure_ms:.3f} ms)\n")

        yanit = ""

        # 2. KARARA GÖRE DONANIM TETİĞİNİ ÇEK:
        if niyet == "MUZIK":
            sarki = hedef if hedef else "Ghost Rule"
            yanit = f"SoundCloud platformunda '{sarki}' frekansı tetiklendi patron."
            webbrowser.open(f"https://soundcloud.com/search/sounds?q={urllib.parse.quote(sarki)}")

        elif niyet == "UYGULAMA":
            app = hedef if hedef else "calc"
            yanit = f"Windows çekirdeğine '{app}' emri gönderildi."
            subprocess.Popen(app, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

        elif niyet == "DIVA":
            yanit = "Project DIVA 60FPS mühürü açılıyor."
            try: os.chdir(r"D:\Oyunlar\Project DIVA Arcade"); subprocess.Popen("start diva.exe", shell=True)
            except Exception as e: yanit = f"Diva klasörü bulunamadı: {e}"

        elif niyet == "TEMIZLE":
            self.chat_box.configure(state="normal"); self.chat_box.delete("1.0", "end"); self.chat_box.configure(state="disabled")
            yanit = "Ekran temizlendi."

        elif niyet == "SOHBET":
            kk = komut.lower()
            for k_anahtar, k_cevap in self.beyin.sohbet_cevaplari.items():
                if k_anahtar in kk: yanit = k_cevap; break
            if not yanit: yanit = "Komut frekansı dışı. (Müzik aç, uygulama çalıştır veya Diva de)"

        self.log_bas(f"[M.I.K.U.] >>> {yanit}\n\n")
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
                        self.status_bar.configure(text="🎙️ M.I.K.U. DİNLİYOR // KOMUT SÖYLE...")
                        self.ses_bas("Efendim patron?")
                        k_ses = r.listen(kaynak, phrase_time_limit=6)
                        k_metin = r.recognize_google(k_ses, language="tr-TR")
                        self.log_bas(f"[🎙️ Sesli Giriş] >>> {k_metin}\n")
                        threading.Thread(target=self.motoru_calistir, args=(k_metin,), daemon=True).start()
                except Exception: pass

if __name__ == "__main__":
    app = MikuSovereignGUI()
    app.mainloop()
