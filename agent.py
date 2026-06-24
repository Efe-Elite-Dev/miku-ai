import os
import sys
import time
import threading
import subprocess
import urllib.parse
import webbrowser
import customtkinter as ctk
import speech_recognition as sr
import pyttsx3
import ollama

# --- PyInstaller Noconsole Çökme Koruması ---
if sys.stdout is None: sys.stdout = open(os.devnull, 'w')
if sys.stderr is None: sys.stderr = open(os.devnull, 'w')

SYSTEM_PROMPT = """Senin adın M.I.K.U. (Modular Interface & Kernel Utility). Sahibin: Efe (Elite-Dev).
Sen Windows çekirdeğine entegre edilmiş fütüristik bir yapay zeka arayüzüsün.
Kısa, net, mekanik, zeki ve dürüst cevaplar ver. Görev aldığında lafı uzatmadan icraat yap."""

miku_tools = [
    {
        "type": "function",
        "function": {
            "name": "uygulama_baslat",
            "description": "Bilgisayardaki bir Windows uygulamasını açar.",
            "parameters": {"type": "object", "properties": {"app_name": {"type": "string"}}, "required": ["app_name"]}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sistem_temizle",
            "description": "Arayüzdeki sohbet geçmişi ekranını temizler.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "diva_atesle",
            "description": "Project DIVA Arcade Future Tone oyununu başlatır.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "soundcloud_sarki_ac",
            "description": "SoundCloud platformunda şarkı açar.",
            "parameters": {"type": "object", "properties": {"sarki_adi": {"type": "string"}}, "required": ["sarki_adi"]}
        }
    }
]

class MikuKernelGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. PENCERE AYARLARI (Cyberpunk Miku Paleti)
        self.title("M.I.K.U. // OS ÇEKİRDEK KONSOLU v1.0")
        self.geometry("520x680")
        self.configure(fg_color="#0d1b2a") # Koyu Lacivert/Teal Arkaplan
        ctk.set_appearance_mode("dark")

        # 2. SES MOTORU
        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', 185)
        except:
            self.tts = None

        self.mesaj_gecmisi = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # 3. YETKİ KÖPRÜLERİ
        self.aktif_fonksiyonlar = {
            "uygulama_baslat": self.tool_uygulama_baslat,
            "sistem_temizle": self.tool_sistem_temizle,
            "diva_atesle": self.tool_diva_atesle,
            "soundcloud_sarki_ac": self.tool_soundcloud_ac
        }

        self.arayuzu_ciz()
        
        # 4. OLLAMA'YI GİZLİCE UYANDIRMA VE ARKA PLAN DİNLEME SERVİSLERİ
        threading.Thread(target=self.ollama_kontrol_et_ve_baslat, daemon=True).start()
        threading.Thread(target=self.pasif_ses_pususu, daemon=True).start()

    def arayuzu_ciz(self):
        # Üst Statüs Barı
        self.status_bar = ctk.CTkLabel(self, text="🟡 SİSTEM BAŞLATILIYOR // OLLAMA ARANIYOR...", 
                                       fg_color="#1b263b", text_color="#00b4d8", font=("Consolas", 12, "bold"), corner_radius=8)
        self.status_bar.pack(pady=(12, 5), padx=15, fill="x")

        # Ana Sohbet Ekranı (Log Terminali)
        self.chat_box = ctk.CTkTextbox(self, fg_color="#101820", text_color="#e0e1dd", font=("Consolas", 13), 
                                       wrap="word", corner_radius=10, border_color="#39C5BB", border_width=1)
        self.chat_box.pack(pady=5, padx=15, fill="both", expand=True)
        self.log_bas("=== M.I.K.U. KERNEL SİSTEMİ BAŞARIYLA YÜKLENDİ ===\nPatron: Efe Elite-Dev\nMod: Canlı Arayüz & Arka Plan Ses Algılama\n--------------------------------------------------\n")

        # Alt Girdi Alanı
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=(5, 15), padx=15, fill="x")

        self.entry = ctk.CTkEntry(self.input_frame, placeholder_text="Miku'ya yaz veya 'Hey Miku' de...", 
                                  fg_color="#1b263b", text_color="white", font=("Consolas", 13), height=40, corner_radius=8)
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda event: self.gonder_tiklandi())

        self.btn_send = ctk.CTkButton(self.input_frame, text="İLET", width=80, height=40, corner_radius=8,
                                      fg_color="#39C5BB", hover_color="#279b92", text_color="black", font=("Consolas", 13, "bold"),
                                      command=self.gonder_tiklandi)
        self.btn_send.pack(side="right")

    # --- KERNEL ARAÇLARI (TOOLS) ---
    def tool_uygulama_baslat(self, app_name):
        try:
            subprocess.Popen(app_name, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return f"{app_name} başarıyla tetiklendi."
        except Exception as e: return f"Hata: {e}"

    def tool_sistem_temizle(self):
        self.chat_box.configure(state="normal")
        self.chat_box.delete("1.0", "end")
        self.chat_box.configure(state="disabled")
        return "Ekran pırıl pırıl yapıldı."

    def tool_diva_atesle(self):
        diva_klasoru = r"D:\Oyunlar\Project DIVA Arcade"
        try:
            os.chdir(diva_klasoru)
            subprocess.Popen("start diva.exe", shell=True)
            return "Project DIVA 60FPS mühürüyle açıldı."
        except Exception as e: return f"Diva başlatılamadı: {e}"

    def tool_soundcloud_ac(self, sarki_adi):
        query = urllib.parse.quote(sarki_adi)
        webbrowser.open(f"https://soundcloud.com/search/sounds?q={query}")
        return f"SoundCloud platformunda '{sarki_adi}' açıldı."

    # --- GİZLİ OLLAMA UYANDIRICISI ---
    def ollama_kontrol_et_ve_baslat(self):
        try:
            # Siyah ekran çıkartmayan gizli Windows Process sorgusu:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            ciktilar = subprocess.check_output('tasklist /FI "IMAGENAME eq ollama.exe"', startupinfo=si).decode(errors='ignore')
            
            if "ollama.exe" not in ciktilar.lower():
                self.status_guncelle("🟡 OLLAMA KAPALI // ARKA PLANDA MOTOR YAKILIYOR...")
                subprocess.Popen("ollama serve", shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                time.sleep(3) # Sunucunun ayağa kalkması için 3 saniye ver
            
            self.status_guncelle("🟢 M.I.K.U. ÇEKİRDEĞİ DEVREDE // FREKANSLAR AÇIK")
        except:
            self.status_guncelle("🔴 OLLAMA MOTORUNA ERİŞİLEMEDİ!")

    # --- GUI YARDIMCILARI ---
    def status_guncelle(self, metin):
        self.status_bar.configure(text=metin)

    def log_bas(self, metin):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", metin)
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def sesli_konus(self, metin):
        if self.tts:
            try:
                self.tts.say(metin)
                self.tts.runAndWait()
            except: pass

    # --- BEYİN TETİKLEYİCİSİ (MULTI-THREADED) ---
    def gonder_tiklandi(self):
        metin = self.entry.get().strip()
        if not metin: return
        self.entry.delete(0, "end")
        
        self.log_bas(f"[Efe Elite-Dev] >>> {metin}\n")
        threading.Thread(target=self.yapay_zeka_isle, args=(metin,), daemon=True).start()

    def yapay_zeka_isle(self, komut_metni):
        self.status_guncelle("⚡ M.I.K.U. SİSTEMİ SORGULUYOR...")
        self.mesaj_gecmisi.append({"role": "user", "content": komut_metni})
        
        try:
            cevap = ollama.chat(model="qwen2.5:7b", messages=self.mesaj_gecmisi, tools=miku_tools)
        except Exception as e:
            self.log_bas(f"[SİSTEM HATASI]: Ollama motoru yanıt vermedi. ({e})\n\n")
            self.status_guncelle("🔴 BAĞLANTI KOPTU")
            return

        gelen_mesaj = cevap["message"]

        if gelen_mesaj.get("tool_calls"):
            for alet in gelen_mesaj["tool_calls"]:
                fonk_adi = alet["function"]["name"]
                argumanlar = alet["function"]["arguments"]

                self.log_bas(f"[KERNEL PROTOKOLÜ] -> İşlem yetkisi kullanılıyor: {fonk_adi}\n")
                sonuc = self.aktif_fonksiyonlar.get(fonk_adi, lambda **k: "Hata")(**argumanlar)
                self.mesaj_gecmisi.append({"role": "tool", "content": str(sonuc), "name": fonk_adi})

            son_cevap = ollama.chat(model="qwen2.5:7b", messages=self.mesaj_gecmisi)
            miku_sozu = son_cevap["message"]["content"]
        else:
            miku_sozu = gelen_mesaj["content"]

        self.mesaj_gecmisi.append({"role": "assistant", "content": miku_sozu})
        self.log_bas(f"[M.I.K.U.] >>> {miku_sozu}\n\n")
        self.status_guncelle("🟢 FREKANSLAR AÇIK")
        self.sesli_konus(miku_sozu)

    # --- DEMİR ADAM / JARVIS ARKA PLAN SES PUSUSU ---
    def pasif_ses_pususu(self):
        r = sr.Recognizer()
        with sr.Microphone() as kaynak:
            r.adjust_for_ambient_noise(kaynak, duration=1.0)
            while True:
                try:
                    ses = r.listen(kaynak, phrase_time_limit=2.5)
                    tetik = r.recognize_google(ses, language="tr-TR").lower()
                    
                    if any(x in tetik for x in ["miku", "hey miku", "heymiku", "miko", "mikü"]):
                        self.status_guncelle("🎙️ M.I.K.U. DİNLİYOR // KOMUT VER PATRON...")
                        self.sesli_konus("Efendim patron?")
                        
                        komut_sesi = r.listen(kaynak, phrase_time_limit=6)
                        komut_metni = r.recognize_google(komut_sesi, language="tr-TR")
                        
                        self.log_bas(f"[🎙️ Sesli Giriş] >>> {komut_metni}\n")
                        threading.Thread(target=self.yapay_zeka_isle, args=(komut_metni,), daemon=True).start()
                except:
                    pass # Gürültüde sessizce beklemeye devam et

if __name__ == "__main__":
    app = MikuKernelGUI()
    app.mainloop()
