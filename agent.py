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

# --- Noconsole Çökme Koruması (stdin/stdout/stderr akışlarını güvenceye al) ---
if sys.stdin is None:
    sys.stdin = open(os.devnull, "r")
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

SYSTEM_PROMPT = """Senin adın M.I.K.U. (Modular Interface & Kernel Utility). Sahibin: Efe (Elite-Dev).
Sen Windows çekirdeğine entegre edilmiş fütüristik bir siber ajansın.
Net, mekanik, zeki, alaycı ve dürüst cevaplar ver. Görev aldığında lafı uzatmadan icraat yap."""

miku_tools = [
    {
        "type": "function",
        "function": {
            "name": "uygulama_baslat",
            "description": "Bilgisayardaki bir Windows uygulamasını açar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Örn: calc, notepad",
                    }
                },
                "required": ["app_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sistem_temizle",
            "description": "Arayüzdeki sohbet geçmişi ekranını temizler.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "diva_atesle",
            "description": "Project DIVA Arcade Future Tone oyununu başlatır.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "soundcloud_sarki_ac",
            "description": "SoundCloud platformunda şarkı aratır ve açar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sarki_adi": {
                        "type": "string",
                        "description": "Örn: Ghost Rule",
                    }
                },
                "required": ["sarki_adi"],
            },
        },
    },
]


class MikuKernelGUI(ctk.CTk):

    def __init__(self):
        super().__init__()

        # 1. PENCERE KAPORTASI (Cyber-Miku Teal Paleti)
        self.title("M.I.K.U. // OS KONSOLU v1.0")
        self.geometry("540x700")
        self.configure(fg_color="#0a1128")
        ctk.set_appearance_mode("dark")

        # 2. SES MOTORU
        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 185)
        except Exception:
            self.tts = None

        self.mesaj_gecmisi = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.aktif_fonksiyonlar = {
            "uygulama_baslat": self.tool_uygulama_baslat,
            "sistem_temizle": self.tool_sistem_temizle,
            "diva_atesle": self.tool_diva_atesle,
            "soundcloud_sarki_ac": self.tool_soundcloud_ac,
        }

        self.arayuzu_kur()

        # 3. ARKA PLAN İŞÇİLERİ (Ollama Denetçisi + Ses Pususu)
        threading.Thread(
            target=self.ollama_servis_kontrol, daemon=True
        ).start()
        threading.Thread(target=self.pasif_ses_pususu, daemon=True).start()

    def arayuzu_kur(self):
        # Statüs Çubuğu
        self.status_bar = ctk.CTkLabel(
            self,
            text="🟡 SİSTEM BAŞLATILIYOR // OLLAMA BEKLENİYOR...",
            fg_color="#1c2541",
            text_color="#00b4d8",
            font=("Consolas", 12, "bold"),
            corner_radius=8,
        )
        self.status_bar.pack(pady=(15, 5), padx=15, fill="x")

        # Log Ekranı
        self.chat_box = ctk.CTkTextbox(
            self,
            fg_color="#0f172a",
            text_color="#39C5BB",
            font=("Consolas", 13),
            wrap="word",
            corner_radius=10,
            border_color="#00b4d8",
            border_width=1,
        )
        self.chat_box.pack(pady=5, padx=15, fill="both", expand=True)
        self.log_bas(
            "=== M.I.K.U. KERNEL SİSTEMİ AKTİF ===\nPatron: Efe Elite-Dev\nMod: Noconsole GUI & 'Hey Miku' Ses Kalkanı\n--------------------------------------------------\n"
        )

        # Girdi Alanı
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=(5, 15), padx=15, fill="x")

        self.entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Komut yaz veya 'Hey Miku' de...",
            fg_color="#1c2541",
            text_color="white",
            font=("Consolas", 13),
            height=40,
            corner_radius=8,
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.gonder_tetik())

        self.btn_send = ctk.CTkButton(
            self.input_frame,
            text="İLET",
            width=80,
            height=40,
            corner_radius=8,
            fg_color="#39C5BB",
            hover_color="#208b84",
            text_color="black",
            font=("Consolas", 13, "bold"),
            command=self.gonder_tetik,
        )
        self.btn_send.pack(side="right")

    # --- KERNEL ARAÇLARI ---
    def tool_uygulama_baslat(self, app_name):
        try:
            subprocess.Popen(
                app_name,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            return f"{app_name} başlatıldı."
        except Exception as e:
            return f"Hata: {e}"

    def tool_sistem_temizle(self):
        self.chat_box.configure(state="normal")
        self.chat_box.delete("1.0", "end")
        self.chat_box.configure(state="disabled")
        return "Ekran temizlendi."

    def tool_diva_atesle(self):
        diva_klasoru = r"D:\Oyunlar\Project DIVA Arcade"
        try:
            os.chdir(diva_klasoru)
            subprocess.Popen("start diva.exe", shell=True)
            return "Project DIVA 60FPS aktif."
        except Exception as e:
            return f"Diva hatası: {e}"

    def tool_soundcloud_ac(self, sarki_adi):
        query = urllib.parse.quote(sarki_adi)
        webbrowser.open(f"https://soundcloud.com/search/sounds?q={query}")
        return f"SoundCloud: '{sarki_adi}' açıldı."

    # --- YARDIMCILAR ---
    def log_bas(self, metin):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", metin)
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def ses_bas(self, metin):
        if self.tts:
            try:
                self.tts.say(metin)
                self.tts.runAndWait()
            except Exception:
                pass

    def ollama_servis_kontrol(self):
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            ciktilar = subprocess.check_output(
                'tasklist /FI "IMAGENAME eq ollama.exe"', startupinfo=si
            ).decode(errors="ignore")

            if "ollama.exe" not in ciktilar.lower():
                self.status_bar.configure(
                    text="🟡 OLLAMA KAPALI // MOTOR AYAĞA KALDIRILIYOR..."
                )
                subprocess.Popen(
                    "ollama serve",
                    shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                time.sleep(3)
            self.status_bar.configure(
                text="🟢 M.I.K.U. DEVREDE // SES & KLAVYE AKTİF"
            )
        except Exception:
            self.status_bar.configure(text="🔴 OLLAMA BAĞLANTI HATASI")

    # --- BEYİN TETİĞİ ---
    def gonder_tetik(self):
        metin = self.entry.get().strip()
        if not metin:
            return
        self.entry.delete(0, "end")
        self.log_bas(f"[Efe Elite-Dev] >>> {metin}\n")
        threading.Thread(
            target=self.yapay_zeka_cevapla, args=(metin,), daemon=True
        ).start()

    def yapay_zeka_cevapla(self, komut):
        self.status_bar.configure(text="⚡ M.I.K.U. DÜŞÜNÜYOR...")
        self.mesaj_gecmisi.append({"role": "user", "content": komut})

        try:
            cevap = ollama.chat(
                model="qwen2.5:7b",
                messages=self.mesaj_gecmisi,
                tools=miku_tools,
            )
        except Exception as e:
            self.log_bas(f"[HATA]: Ollama motoruna ulaşılamadı! ({e})\n\n")
            self.status_bar.configure(text="🔴 BAĞLANTI KOPTU")
            return

        gelen = cevap["message"]
        if gelen.get("tool_calls"):
            for alet in gelen["tool_calls"]:
                f_adi = alet["function"]["name"]
                args = alet["function"]["arguments"]
                self.log_bas(
                    f"[KERNEL PROTOKOLÜ] -> İşlem yetkisi tetiklendi: {f_adi}\n"
                )
                sonuc = self.aktif_fonksiyonlar.get(
                    f_adi, lambda **k: "Hata"
                )(**args)
                self.mesaj_gecmisi.append(
                    {
                        "role": "tool",
                        "content": str(sonuc),
                        "name": f_adi,
                    }
                )

            son_chat = ollama.chat(
                model="qwen2.5:7b", messages=self.mesaj_gecmisi
            )
            yanit = son_chat["message"]["content"]
        else:
            yanit = gelen["content"]

        self.mesaj_gecmisi.append({"role": "assistant", "content": yanit})
        self.log_bas(f"[M.I.K.U.] >>> {yanit}\n\n")
        self.status_bar.configure(
            text="🟢 M.I.K.U. DEVREDE // SES & KLAVYE AKTİF"
        )
        self.ses_bas(yanit)

    # --- DEMİR ADAM / JARVIS SES PUSUSU ---
    def pasif_ses_pususu(self):
        r = sr.Recognizer()
        with sr.Microphone() as kaynak:
            r.adjust_for_ambient_noise(kaynak, duration=1.0)
            while True:
                try:
                    ses = r.listen(kaynak, phrase_time_limit=2.5)
                    tetik = r.recognize_google(
                        ses, language="tr-TR"
                    ).lower()

                    if any(
                        x in tetik
                        for x in [
                            "miku",
                            "hey miku",
                            "heymiku",
                            "miko",
                            "mikü",
                        ]
                    ):
                        self.status_bar.configure(
                            text="🎙️ M.I.K.U. DİNLİYOR // KOMUT SÖYLE..."
                        )
                        self.ses_bas("Efendim patron?")

                        k_ses = r.listen(kaynak, phrase_time_limit=6)
                        k_metin = r.recognize_google(
                            k_ses, language="tr-TR"
                        )
                        self.log_bas(f"[🎙️ Sesli Komut] >>> {k_metin}\n")
                        threading.Thread(
                            target=self.yapay_zeka_cevapla,
                            args=(k_metin,),
                            daemon=True,
                        ).start()
                except Exception:
                    pass


if __name__ == "__main__":
    app = MikuKernelGUI()
    app.mainloop()
