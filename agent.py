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
from duckduckgo_search import DDGS

# --- Noconsole Çökme Koruması ---
if sys.stdin is None: sys.stdin = open(os.devnull, "r")
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")

CHROME_AGENT = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

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
        self.title("M.I.K.U. // OS KONSOLU v1.3 (Dual-Core Edition)")
        self.geometry("540x700")
        self.configure(fg_color="#0a1128")
        ctk.set_appearance_mode("dark")

        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 185)
        except Exception: self.tts = None

        self.mesaj_gecmisi = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.arayuzu_kur()
        threading.Thread(target=self.pasif_ses_pususu, daemon=True).start()

    def arayuzu_kur(self):
        self.status_bar = ctk.CTkLabel(self, text="🟢 M.I.K.U. ÇİFT MOTOR // YEDEKLİ AI DEVREDE", 
                                       fg_color="#1c2541", text_color="#39C5BB", font=("Consolas", 12, "bold"), corner_radius=8)
        self.status_bar.pack(pady=(15, 5), padx=15, fill="x")

        self.chat_box = ctk.CTkTextbox(self, fg_color="#0f172a", text_color="#00b4d8", font=("Consolas", 13), 
                                       wrap="word", corner_radius=10, border_color="#39C5BB", border_width=1)
        self.chat_box.pack(pady=5, padx=15, fill="both", expand=True)
        self.log_bas("=== M.I.K.U. DUAL-CORE v1.3 YÜKLENDİ ===\nPatron: Efe Elite-Dev\nSiber Zırh: Redundant AI Cluster (DDG -> Pollinations Root)\n--------------------------------------------------\n")

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
    # ★ KESİN ÇÖZÜM: ÇİFT MOTORLU YEDEKLİ BEYİN (FAILOVER CLUSTER)
    # =================================================================
    def ask_cloud_ai(self, yeni_mesaj):
        self.mesaj_gecmisi.append({"role": "user", "content": yeni_mesaj})

        # --- MOTOR A: DUCKDUCKGO NATIVE CHAT (Sıfır 404 riski) ---
        try:
            sohbet_metni = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in self.mesaj_gecmisi])
            ddg_yanit = DDGS().chat(sohbet_metni, model="gpt-4o-mini")
            if ddg_yanit:
                self.mesaj_gecmisi.append({"role": "assistant", "content": ddg_yanit})
                return ddg_yanit
        except Exception as e1:
            pass # Ses çıkarma, çaktırmadan Motor B'ye kay

        # --- MOTOR B: POLLINATIONS KÖK ADRESİ (404/403 Fixli) ---
        try:
            url = "https://text.pollinations.ai/"  # <- DİKKAT: Sonunda hiçbir şey yok, KÖK!
            payload = {"messages": self.mesaj_gecmisi, "model": "gpt-4o-mini"}
            
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'), 
                headers={'Content-Type': 'application/json', **CHROME_AGENT}
            )
            with urllib.request.urlopen(req, timeout=12) as r:
                # Kök adres JSON dönmez, direkt düz metin (string) döner:
                pol_yanit = r.read().decode('utf-8')
                self.mesaj_gecmisi.append({"role": "assistant", "content": pol_yanit})
                return pol_yanit
        except Exception as e2:
            return f"Sistem çöktü patron. Her iki yapay zeka köprüsü de koptu.\nMotor A (DDG): {e1}\nMotor B (Pol): {e2}"

    # --- MS PAINT ALT-AJANLARI İÇİN DE ÇİFT MOTOR ---
    def alt_ajan_sorgula(self, prompt_metni):
        try: return DDGS().chat(prompt_metni, model="gpt-4o-mini")
        except Exception:
            try:
                req = urllib.request.Request("https://text.pollinations.ai/", 
                      data=json.dumps({"messages":[{"role":"user","content":prompt_metni}]}).encode('utf-8'), 
                      headers={'Content-Type': 'application/json', **CHROME_AGENT})
                with urllib.request.urlopen(req, timeout=10) as r: return r.read().decode('utf-8')
            except Exception: return "Alt-Ajan tıkandı."

    def gonder_tetik(self):
        metin = self.entry.get().strip()
        if not metin: return
        self.entry.delete(0, "end")
        self.log_bas(f"[Efe Elite-Dev] >>> {metin}\n")
        threading.Thread(target=self.ajan_motorunu_islet, args=(metin,), daemon=True).start()

    def ajan_motorunu_islet(self, komut):
        k_kontrol = komut.lower().strip()

        if any(k_kontrol.startswith(x) for x in ["araştır:", "arastir:", "araştır ", "arastir "]):
            sorgu = re.split(r":|\s", komut, 1)[1].strip() if re.search(r":|\s", komut) else komut
            self.miku_deep_research_pipeline(sorgu)
            return

        self.status_bar.configure(text="⚡ M.I.K.U. DÜŞÜNÜYOR (Dual V8)...")
        yanit = self.ask_cloud_ai(komut)

        self.log_bas(f"[M.I.K.U.] >>> {yanit}\n\n")
        self.ses_bas(yanit)

        if re.search(r"\[RUN:(.*?)\]", yanit):
            app = re.search(r"\[RUN:(.*?)\]", yanit).group(1).strip()
            self.log_bas(f"[KERNEL] -> '{app}' çalıştırıldı.\n\n")
            subprocess.Popen(app, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

        if re.search(r"\[SC:(.*?)\]", yanit):
            sarki = re.search(r"\[SC:(.*?)\]", yanit).group(1).strip()
            self.log_bas(f"[KERNEL] -> SoundCloud '{sarki}' açılıyor.\n\n")
            webbrowser.open(f"https://soundcloud.com/search/sounds?q={urllib.parse.quote(sarki)}")

        if "[DIVA]" in yanit:
            self.log_bas("[KERNEL] -> Project DIVA 60FPS tetiklendi.\n\n")
            try: os.chdir(r"D:\Oyunlar\Project DIVA Arcade"); subprocess.Popen("start diva.exe", shell=True)
            except Exception as e: self.log_bas(f"[HATA]: Diva açılamadı -> {e}\n")

        if "[CLEAR]" in yanit:
            self.chat_box.configure(state="normal"); self.chat_box.delete("1.0", "end"); self.chat_box.configure(state="disabled")

        self.status_bar.configure(text="🟢 M.I.K.U. ÇİFT MOTOR // YEDEKLİ AI DEVREDE")

    def miku_deep_research_pipeline(self, sorgu_konusu):
        self.status_bar.configure(text="⚡ [BORU HATTI]: 1/4 - CANLI WEB TARANIYOR...")
        self.log_bas(f"\n[🚀 DEEP-SCAN PROTOKOLÜ]: '{sorgu_konusu}'\n" + "-" * 50 + "\n")

        self.log_bas("  [>] Node 1 (Live DDG Search): İnternet ağı deşiliyor...\n")
        try:
            ddg_sonuclar = DDGS().text(sorgu_konusu, max_results=4)
            ham_veri = "\n\n".join([f"Site: {r['href']}\nÖzet: {r['body']}" for r in ddg_sonuclar])
            if not ham_veri.strip(): ham_veri = "Sonuç bulunamadı."
        except Exception as e: ham_veri = f"Ağ Hatası: {e}"

        self.status_bar.configure(text="⚡ [BORU HATTI]: 2/4 - TEYİT EDİLİYOR...")
        self.log_bas("  [>] Node 2 (Fact-Checker)   : Yalanlar süzülüyor...\n")
        dogru_veri = self.alt_ajan_sorgula(f"Şu bilgileri analiz et, sadece teyitli olanları özetle:\nSoru: {sorgu_konusu}\nVeri: {ham_veri}")

        self.status_bar.configure(text="⚡ [BORU HATTI]: 3/4 - TÜRKÇE KALİBRASYON...")
        self.log_bas("  [>] Node 3 (Linguist)       : Dil yapısı kalibre ediliyor...\n")
        turkce_veri = self.alt_ajan_sorgula(f"Şu metni siber-mekanik, kusursuz bir Türkçe ile yaz:\n{dogru_veri}")

        self.status_bar.configure(text="⚡ [BORU HATTI]: 4/4 - DAMITILIYOR...")
        self.log_bas("  [>] Node 4 (Distiller)      : TL;DR presi vuruluyor...\n")
        final_rapor = self.alt_ajan_sorgula(f"Şu metni Efe'nin saniyeler içinde anlayacağı net bir Özet Rapor yap:\n{turkce_veri}")

        self.log_bas("\n" + "=" * 50 + f"\n[★ KESİN RAPOR]: {sorgu_konusu}\n" + "=" * 50 + f"\n{final_rapor}\n\n")
        self.status_bar.configure(text="🟢 M.I.K.U. ÇİFT MOTOR // YEDEKLİ AI DEVREDE")
        self.ses_bas(final_rapor)

    def pasif_ses_pususu(self):
        r = sr.Recognizer()
        with sr.Microphone() as kaynak:
            r.adjust_for_ambient_noise(kaynak, duration=1.0)
            while True:
                try:
                    ses = r.listen(kaynak, phrase_time_limit=2.5)
                    tetik = r.recognize_google(ses, language="tr-TR").lower()
                    if any(x in tetik for x in ["miku", "hey miku", "heymiku", "miko", "mikü"]):
                        self.status_bar.configure(text="🎙️ M.I.K.U. DİNLİYOR // SÖYLE PATRON...")
                        self.ses_bas("Efendim patron?")
                        k_ses = r.listen(kaynak, phrase_time_limit=6)
                        k_metin = r.recognize_google(k_ses, language="tr-TR")
                        self.log_bas(f"[🎙️ Sesli Giriş] >>> {k_metin}\n")
                        threading.Thread(target=self.ajan_motorunu_islet, args=(k_metin,), daemon=True).start()
                except Exception: pass

if __name__ == "__main__":
    app = MikuKernelGUI()
    app.mainloop()
