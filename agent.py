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
from duckduckgo_search import DDGS  # <--- YENİ CANLI KULAĞIMIZ

# --- Noconsole Çökme Koruması ---
if sys.stdin is None:
    sys.stdin = open(os.devnull, "r")
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

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

        self.title("M.I.K.U. // OS KONSOLU v1.2 (Live Deep-Scan)")
        self.geometry("540x700")
        self.configure(fg_color="#0a1128")
        ctk.set_appearance_mode("dark")

        try:
            self.tts = pyttsx3.init()
            self.tts.setProperty("rate", 185)
        except Exception:
            self.tts = None

        self.mesaj_gecmisi = [{"role": "system", "content": SYSTEM_PROMPT}]
        self.arayuzu_kur()

        threading.Thread(target=self.pasif_ses_pususu, daemon=True).start()

    def arayuzu_kur(self):
        self.status_bar = ctk.CTkLabel(
            self,
            text="🟢 M.I.K.U. BULUT KERNEL // CANLI İNTERNET MODU",
            fg_color="#1c2541",
            text_color="#39C5BB",
            font=("Consolas", 12, "bold"),
            corner_radius=8,
        )
        self.status_bar.pack(pady=(15, 5), padx=15, fill="x")

        self.chat_box = ctk.CTkTextbox(
            self,
            fg_color="#0f172a",
            text_color="#00b4d8",
            font=("Consolas", 13),
            wrap="word",
            corner_radius=10,
            border_color="#39C5BB",
            border_width=1,
        )
        self.chat_box.pack(pady=5, padx=15, fill="both", expand=True)
        self.log_bas(
            "=== M.I.K.U. DEEP-SCAN v1.2 YÜKLENDİ ===\nPatron: Efe Elite-Dev\nYetkiler: Regex Kernel UI + 4-Aşamalı Canlı Web Ajanı\n--------------------------------------------------\n"
        )

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

    def log_bas(self, metin):
        self.chat_box.configure(state="normal")
        self.chat_box.insert("end", metin)
        self.chat_box.configure(state="disabled")
        self.chat_box.see("end")

    def ses_bas(self, metin):
        temiz = re.sub(r"\[.*?\]", "", metin)
        if self.tts and temiz.strip():
            try:
                self.tts.say(temiz)
                self.tts.runAndWait()
            except Exception:
                pass

    def ask_cloud_ai(self, prompt_text, temp=0.5):
        url = "https://text.pollinations.ai/openai/v1/chat/completions"
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt_text}],
            "temperature": temp,
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read().decode("utf-8"))["choices"][0][
                    "message"
                ]["content"]
        except Exception as e:
            return f"API Hatası: {e}"

    # --- ASIL TETİK MOTORU ---
    def gonder_tetik(self):
        metin = self.entry.get().strip()
        if not metin:
            return
        self.entry.delete(0, "end")
        self.log_bas(f"[Efe Elite-Dev] >>> {metin}\n")
        threading.Thread(
            target=self.ajan_motorunu_islet, args=(metin,), daemon=True
        ).start()

    def ajan_motorunu_islet(self, komut):
        k_kontrol = komut.lower().strip()

        # =============================================================
        # ★ MAKAS KÖPRÜSÜ: "ARAŞTIR" SİNYALİ YAKALANDI MI?
        # =============================================================
        if any(
            k_kontrol.startswith(x)
            for x in ["araştır:", "arastir:", "araştır ", "arastir "]
        ):
            # İki nokta veya boşluktan sonraki asıl sorguyu ayıkla:
            sorgu = (
                re.split(r":|\s", komut, 1)[1].strip()
                if re.search(r":|\s", komut)
                else komut
            )

            # Normal sohbeti öldür, 4-Aşamalı Deep-Scan Boru Hattını fırlat!
            self.miku_deep_research_pipeline(sorgu)
            return

        # Normal Sohbet & Regex İşleyicisi
        self.status_bar.configure(text="⚡ M.I.K.U. DÜŞÜNÜYOR...")
        yanit = self.ask_cloud_ai(
            SYSTEM_PROMPT + f"\n\nKullanıcı: {komut}", temp=0.5
        )

        self.log_bas(f"[M.I.K.U.] >>> {yanit}\n\n")
        self.ses_bas(yanit)

        # Regex Kalkanları
        if re.search(r"\[RUN:(.*?)\]", yanit):
            app = re.search(r"\[RUN:(.*?)\]", yanit).group(1).strip()
            self.log_bas(f"[KERNEL] -> '{app}' çalıştırıldı.\n\n")
            subprocess.Popen(
                app, shell=True, creationflags=subprocess.CREATE_NO_WINDOW
            )

        if re.search(r"\[SC:(.*?)\]", yanit):
            sarki = re.search(r"\[SC:(.*?)\]", yanit).group(1).strip()
            self.log_bas(f"[KERNEL] -> SoundCloud '{sarki}' açılıyor.\n\n")
            webbrowser.open(
                f"https://soundcloud.com/search/sounds?q={urllib.parse.quote(sarki)}"
            )

        if "[DIVA]" in yanit:
            self.log_bas("[KERNEL] -> Project DIVA 60FPS tetiklendi.\n\n")
            try:
                os.chdir(r"D:\Oyunlar\Project DIVA Arcade")
                subprocess.Popen("start diva.exe", shell=True)
            except Exception as e:
                self.log_bas(f"[HATA]: Diva açılamadı -> {e}\n")

        if "[CLEAR]" in yanit:
            self.chat_box.configure(state="normal")
            self.chat_box.delete("1.0", "end")
            self.chat_box.configure(state="disabled")

        self.status_bar.configure(
            text="🟢 M.I.K.U. DEVREDE // CANLI İNTERNET MODU"
        )

    # =================================================================
    # 🚀 4-AŞAMALI MS PAINT BORU HATTI (CANLI DUCKDUCKGO ENJEKSİYONU)
    # =================================================================
    def miku_deep_research_pipeline(self, sorgu_konusu):
        self.status_bar.configure(
            text="⚡ [BORU HATTI]: 1/4 - CANLI WEB TARANIYOR..."
        )
        self.log_bas(
            f"\n[🚀 DEEP-SCAN PROTOKOLÜ BAŞLADI]: '{sorgu_konusu}'\n"
            + "-" * 50
            + "\n"
        )

        # 1. YUVARLAK: [GERÇEK CANLI İNTERNET]
        self.log_bas("  [>] Node 1 (Live DDG Search): Google ağı taranıyor...\n")
        try:
            ddg_sonuclar = DDGS().text(sorgu_konusu, max_results=4)
            ham_veri = "\n\n".join(
                [f"Site: {r['href']}\nÖzet: {r['body']}" for r in ddg_sonuclar]
            )
            if not ham_veri.strip():
                ham_veri = (
                    "Arama motoru bu spesifik konuda sonuç döndüremedi."
                )
        except Exception as e:
            ham_veri = f"Arama ağı kilitlendi: {e}"

        # 2. YUVARLAK: [DOĞRULUK KONTROLÜ]
        self.status_bar.configure(
            text="⚡ [BORU HATTI]: 2/4 - BİLGİLER TEYİT EDİLİYOR..."
        )
        self.log_bas(
            "  [>] Node 2 (Fact-Checker)   : Yalanlar ve gürültü filtreleniyor...\n"
        )
        p2 = f"Sen bir Doğruluk Denetçisisin. Sorulan soru: '{sorgu_konusu}'. Aşağıdaki canlı arama motoru sonuçlarını analiz et, uydurma veya alakasız linkleri çöpe at ve sadece teyitli bilgiyi sentezle:\n\n{ham_veri}"
        dogru_veri = self.ask_cloud_ai(p2, temp=0.2)

        # 3. YUVARLAK: [ÇEVİRMEN]
        self.status_bar.configure(
            text="⚡ [BORU HATTI]: 3/4 - DİL KALİBRASYONU..."
        )
        self.log_bas(
            "  [>] Node 3 (Linguist)       : Türkçe dil yapısına oturttuluyor...\n"
        )
        p3 = f"Şu metni siber-mekanik, akıcı ve üst düzey bir Türkçe ile yeniden yaz:\n\n{dogru_veri}"
        turkce_veri = self.ask_cloud_ai(p3, temp=0.3)

        # 4. YUVARLAK: [KISA VE ÖZ]
        self.status_bar.configure(
            text="⚡ [BORU HATTI]: 4/4 - RAPOR DAMITILIYOR..."
        )
        self.log_bas(
            "  [>] Node 4 (Distiller)      : TL;DR algoritması devrede...\n"
        )
        p4 = f"Şu Türkçe metni laf kalabalığından tamamen arındır; Efe'nin saniyeler içinde okuyup anlayacağı, vurucu ve net bir Özet Rapor haline getir:\n\n{turkce_veri}"
        final_rapor = self.ask_cloud_ai(p4, temp=0.4)

        self.log_bas(
            "\n"
            + "=" * 50
            + f"\n[★ KESİN RAPOR]: {sorgu_konusu}\n"
            + "=" * 50
            + f"\n{final_rapor}\n\n"
        )
        self.status_bar.configure(
            text="🟢 M.I.K.U. DEVREDE // CANLI İNTERNET MODU"
        )
        self.ses_bas(final_rapor)

    # --- DEMİR ADAM SES PUSUSU ---
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
                        self.log_bas(f"[🎙️ Sesli Giriş] >>> {k_metin}\n")
                        threading.Thread(
                            target=self.ajan_motorunu_islet,
                            args=(k_metin,),
                            daemon=True,
                        ).start()
                except Exception:
                    pass


if __name__ == "__main__":
    app = MikuKernelGUI()
    app.mainloop()
