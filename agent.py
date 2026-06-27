import sys
import os
import subprocess
import ctypes

# =====================================================================
# 1. YÖNETİCİ İZNİ KALKANI
# =====================================================================
def uac_yonetici_kalkani():
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
    except Exception: pass

uac_yonetici_kalkani()

# =====================================================================
# 2. SIFIR-BAĞIMLILIK OTO-KURULUM (Listeden PIL, psutil ve pyttsx3 KAZINDI!)
# =====================================================================
ZORUNLU_KUTUPHANELER = {
    "speech_recognition": "SpeechRecognition",
    "pyaudio": "PyAudio",
    "customtkinter": "customtkinter"
}

def siber_vucut_tarama_ve_nakil():
    eksik = [pip for mod, pip in ZORUNLU_KUTUPHANELER.items() if not _k(mod)]
    if eksik:
        ctypes.windll.user32.MessageBoxW(0, f"M.I.K.U. Eksik Temel Modüller:\n-> {', '.join(eksik)}\n\nİndirmek için 'Tamam'a basın.", "⚡ M.I.K.U. DERLEYİCİ v7.5", 0x40)
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *eksik])
            subprocess.Popen([sys.executable] + sys.argv); sys.exit(0)
        except Exception: sys.exit(1)

def _k(m):
    try: __import__(m); return True
    except ImportError: return False

siber_vucut_tarama_ve_nakil()


# =====================================================================
# ★★★ 3. BİZİM YAZDIĞIMIZ SAF METAL MOTORLAR (SIFIR KÜTÜPHANE) ★★★
# =====================================================================
class FILETIME(ctypes.Structure):
    _fields_ = [("dwLowDateTime", ctypes.c_ulong), ("dwHighDateTime", ctypes.c_ulong)]

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("sullAvailExtendedVirtual", ctypes.c_ulonglong)]

def saf_metal_telemetri():
    stat = MEMORYSTATUSEX(); stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
    ram_yuzde = stat.dwMemoryLoad

    def f2i(ft): return (ft.dwHighDateTime << 32) | ft.dwLowDateTime
    i1, k1, u1 = FILETIME(), FILETIME(), FILETIME()
    ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(i1), ctypes.byref(k1), ctypes.byref(u1))
    time.sleep(0.4) 
    i2, k2, u2 = FILETIME(), FILETIME(), FILETIME()
    ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(i2), ctypes.byref(k2), ctypes.byref(u2))
    
    sys_df = (f2i(k2) - f2i(k1)) + (f2i(u2) - f2i(u1))
    idl_df = f2i(i2) - f2i(i1)
    cpu_yuzde = int((sys_df - idl_df) * 100 / sys_df) if sys_df > 0 else 0

    return cpu_yuzde, ram_yuzde

def saf_metal_ekran_goruntusu():
    yol = os.path.expanduser("~/Desktop/MIKU_SS.png")
    cmd = f'powershell -command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Screen]::AllScreens | %{{ $b = New-Object System.Drawing.Bitmap $_.Bounds.Width, $_.Bounds.Height; $g = [System.Drawing.Graphics]::FromImage($b); $g.CopyFromScreen($_.Bounds.X, $_.Bounds.Y, 0, 0, $b.Size); $b.Save(\'{yol}\') }}"'
    subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)

# ★ YENİ: KÜTÜPHANESİZ SAF WİNDOWS SES MOTORU (.NET SAPI5)
def saf_metal_konus(metin):
    temiz_metin = re.sub(r'[^\w\s.,?!öçşığüÖÇŞİĞÜ]', '', metin).strip()
    if not temiz_metin: return
    # PowerShell üzerinden arka planda sessizce konuşma objesi yaratıp okutuyoruz!
    cmd = f'powershell -command "Add-Type -AssemblyName System.Speech; $s = New-Object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak(\'{temiz_metin}\')"'
    subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)


# =====================================================================
# 4. ANA BİLİNÇ VE STANDART MODÜLLER
# =====================================================================
import datetime
import difflib
import json
import platform
import re
import threading
import urllib.parse
import urllib.request
import webbrowser
import customtkinter as ctk
import speech_recognition as sr
import winsound

if sys.stdin is None: sys.stdin = open(os.devnull, "r")
if sys.stdout is None: sys.stdout = open(os.devnull, "w")
if sys.stderr is None: sys.stderr = open(os.devnull, "w")

UYANDIRMA_KELIMELERI = ["hey miku", "heymiku", "miku", "uyan"]
YEREL_SURUM = "v7.5"
GITHUB_REPO = "Efe-Elite-Dev/SENIN-REPO-ADIN" # <--- Kendi reponu yaz!


def gercek_silikon_kimligi():
    try:
        cmd = 'powershell -command "(Get-CimInstance Win32_Processor).Name"'
        out = subprocess.check_output(cmd, shell=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if temiz := out.strip().split("\n")[0]: return re.sub(r'\s+', ' ', temiz)
    except Exception: pass
    return platform.processor() or "Bilinmeyen Silikon"


class SynapseMemory:
    def __init__(self):
        self.yol = os.path.expanduser("~/.miku_synapse.json")
        self.veri = self.yukle()

    def yukle(self):
        v = {"kurulum_tamamlandi": False, "patron": "Efe Elite-Dev", "uyandirma_kelimesi": "uyan", "toplam_komut": 0, "alarmlar": []}
        if os.path.exists(self.yol):
            try:
                with open(self.yol, "r", encoding="utf-8") as f: return json.load(f)
            except Exception: return v
        return v

    def kaydet(self):
        try:
            with open(self.yol, "w", encoding="utf-8") as f: json.dump(self.veri, f, ensure_ascii=False, indent=4)
        except Exception: pass

    def komut_islenildi(self):
        self.veri["toplam_komut"] += 1; self.kaydet()


class SovereignBrain:
    def __init__(self, hafiza_ref):
        self.hafiza = hafiza_ref
        self.yerel_intents = {
            "MUZIK": ["çal", "şarkı", "müzik", "dinle", "oynat", "parça", "müzka", "çla"],
            "MEDYA_DURDUR": ["durdur", "dur", "sus", "kes", "sessiz"],
            "ALARM": ["alarm", "zil", "uyandır", "hatırlat", "alram"],
            "KILITLE": ["kilitle", "kitle", "masadan"],
            "SS_AL": ["ekran görüntüsü", "ss al", "fotoğrafını çek", "foto"],
            "ZORLA_KAPAT": ["zorla kapat", "görevini sonlandır", "kill"],
            "HESAP": ["hesap", "makine", "topla", "çıkar", "çarp", "böl"],
            "UYGULAMA": ["çalıştır", "program", "uygulama", "notepad", "cmd"],
            "DIVA": ["diva", "project", "arcade"],
            "TEMIZLE": ["temizle", "sil", "ekran", "clear", "cls"],
            "DURUM": ["durum", "rapor", "telemetri", "sistem", "bilgi", "işlemci"],
            "KAPAT": ["bilgisayarı kapat", "kapan", "söndür", "uykuya", "fişi"],
            "PANIK": ["panik", "gizle", "tehlike"]
        }
        self.cop = {"bir", "bana", "şu", "ve", "ile", "lütfen", "hey", "miku", "efe", "abi", "açsana", "çalsana", "kur", "kursana"}

    def bulut_danis(self, soru):
        id_str = f"Adın M.I.K.U. Sahibin {self.hafiza.veri['patron']}. Sen fütüristik yapay zekasın. Efe disleksik tarzda yazar, ne dediğini anla."
        url = f"https://text.pollinations.ai/prompt/{urllib.parse.quote(id_str + ' Soru: ' + soru)}?model=gpt-4o-mini"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=6) as r: return r.read().decode('utf-8')
        except Exception: return "Bulut bağlantım koptu patron."

    def niyet_analiz(self, metin):
        mt = metin.lower()
        if any(k in mt for k in ["kapat", "söndür", "fişi"]) and not any(x in mt for x in ["chrome", "discord", "uygulama", "zorla"]): return "KAPAT", mt
        if any(a in mt for a in ["alarm", "uyandır", "alram"]): return "ALARM", mt

        temiz = re.findall(r"\w+", mt)
        skorlar = {}
        for niyet, havuz in self.yerel_intents.items():
            s = sum(1 for k in temiz if k not in self.cop and (difflib.get_close_matches(k, havuz, n=1, cutoff=0.60) or any(k.startswith(h) for h in havuz)))
            if s > 0: skorlar[niyet] = s

        if not skorlar: return "BULUT", metin
        secilen = max(skorlar, key=skorlar.get)
        hedef_kalan = [k for k in temiz if not difflib.get_close_matches(k, self.yerel_intents[secilen], n=1, cutoff=0.60) and k not in self.cop]
        return secilen, " ".join(hedef_kalan)

    def zaman_coz(self, metin):
        mt = metin.lower(); simdi = datetime.datetime.now()
        if m_abs := re.search(r"(\d{1,2})[:.](\d{2})", mt):
            h, m = int(m_abs.group(1)), int(m_abs.group(2))
            hedef = simdi.replace(hour=h, minute=m, second=0, microsecond=0)
            if hedef <= simdi: hedef += datetime.timedelta(days=1)
            return int((hedef - simdi).total_seconds()), hedef.strftime("%H:%M")

        if m_tek := re.search(r"(?:gece|akşam|sabah|saat)?\s*(\d{1,2})(?:\s*(?:da|de|ya|ye|buçuk))?", mt):
            h = int(m_tek.group(1))
            if any(w in mt for w in ["gece", "akşam"]) and h < 12: h += 12
            elif "gece" in mt and h == 12: h = 0
            m = 30 if "buçuk" in mt else 0
            hedef = simdi.replace(hour=h, minute=m, second=0, microsecond=0)
            if hedef <= simdi: hedef += datetime.timedelta(days=1)
            return int((hedef - simdi).total_seconds()), hedef.strftime("%H:%M")

        if m_st := re.search(r"(\d+)\s*saat", mt): return int(m_st.group(1))*3600, (simdi + datetime.timedelta(hours=int(m_st.group(1)))).strftime("%H:%M")
        if m_dk := re.search(r"(\d+)\s*(?:dakika|dk)", mt): return int(m_dk.group(1))*60, (simdi + datetime.timedelta(minutes=int(m_dk.group(1)))).strftime("%H:%M")
        return 60, (simdi + datetime.timedelta(seconds=60)).strftime("%H:%M")


class AlarmSirenPenceresi(ctk.CTkToplevel):
    def __init__(self, etiket):
        super().__init__(); self.title("🚨 ALARM!"); self.geometry("450x250"); self.configure(fg_color="#310a0a"); self.attributes("-topmost", True); self.aktif = True
        ctk.CTkLabel(self, text="⏰ M.I.K.U. ALARM DEVREDE", font=("Consolas", 24, "bold"), text_color="#f87171").pack(pady=30)
        ctk.CTkLabel(self, text=f"Hatırlatma: {etiket}", font=("Consolas", 14), text_color="white").pack(pady=10)
        ctk.CTkButton(self, text="SİRENİ SUSTUR", fg_color="white", text_color="black", font=("Consolas", 16, "bold"), height=50, command=self.kapat).pack(pady=20, padx=40, fill="x")
        threading.Thread(target=self.ses_dongusu, daemon=True).start()

    def ses_dongusu(self):
        while self.aktif: winsound.Beep(1200, 400); time.sleep(0.1); winsound.Beep(800, 400); time.sleep(0.2)
    def kapat(self): self.aktif = False; self.destroy()


class MikuArayuz(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.hafiza = SynapseMemory(); self.beyin = SovereignBrain(self.hafiza); self.islemci_adi = gercek_silikon_kimligi()
        self.geometry("600x750"); self.configure(fg_color="#050508") 
        ctk.set_appearance_mode("dark")

        if not self.hafiza.veri.get("kurulum_tamamlandi", False): self.kurulum_ac()
        else: self.karargah_kur()

    def kurulum_ac(self):
        self.title("M.I.K.U. // İLK KURULUM")
        f = ctk.CTkFrame(self, fg_color="transparent"); f.pack(fill="both", expand=True, padx=40, pady=60)
        ctk.CTkLabel(f, text="⚡ SİBER KİMLİK MÜHÜRÜ", font=("Consolas", 22, "bold"), text_color="#00E5FF").pack(pady=20)
        self.ent_i = ctk.CTkEntry(f, placeholder_text="Patron Adı (Örn: Efe)", height=42, fg_color="#0f172a"); self.ent_i.pack(fill="x", pady=10)
        self.ent_w = ctk.CTkEntry(f, placeholder_text="Uyandırma Kelimesi (Örn: uyan)", height=42, fg_color="#0f172a"); self.ent_w.pack(fill="x", pady=10)
        ctk.CTkButton(f, text="SİSTEMİ BAŞLAT 🚀", fg_color="#00E5FF", text_color="black", font=("Consolas", 14, "bold"), height=48, command=lambda: self.k_kaydet(f)).pack(pady=40, fill="x")

    def k_kaydet(self, f):
        self.hafiza.veri["patron"] = self.ent_i.get().strip() or "Efe"; self.hafiza.veri["uyandirma_kelimesi"] = self.ent_w.get().strip().lower() or "uyan"
        self.hafiza.veri["kurulum_tamamlandi"] = True; self.hafiza.kaydet(); f.destroy(); self.karargah_kur()

    def karargah_kur(self):
        self.title(f"M.I.K.U. Sovereign v7.5 // [{self.hafiza.veri['patron']}]")
        self.top_frame = ctk.CTkFrame(self, fg_color="#0a0f1d", corner_radius=8, border_color="#00E5FF", border_width=1)
        self.top_frame.pack(pady=(12, 5), padx=15, fill="x")
        self.lbl_cpu = ctk.CTkLabel(self.top_frame, text=f"💻 {self.islemci_adi}", font=("Consolas", 11, "bold"), text_color="#38bdf8")
        self.lbl_cpu.pack(pady=(6,2), padx=10, anchor="w")
        self.lbl_stats = ctk.CTkLabel(self.top_frame, text="⚡ Telemetri Yükleniyor...", font=("Consolas", 11), text_color="#94a3b8")
        self.lbl_stats.pack(pady=(0,6), padx=10, anchor="w")

        self.ses_bar = ctk.CTkProgressBar(self, mode="indeterminate", fg_color="#050508", progress_color="#00E5FF", height=3)
        self.ses_bar.pack(pady=2, padx=15, fill="x"); self.ses_bar.set(0)

        self.chat = ctk.CTkTextbox(self, fg_color="#020307", text_color="#00E5FF", font=("Consolas", 13), border_color="#1e293b", border_width=1, corner_radius=10)
        self.chat.pack(pady=5, padx=15, fill="both", expand=True)
        self.log(f"=== M.I.K.U. KERNEL v7.5 DEVREDE ===\nSilikon: {self.islemci_adi}\nFelsefe: [Bare Metal] pyttsx3 kütüphanesi çöpe atıldı!\nDonanım: Ses, SS, CPU ve RAM artık %100 saf metal.\n--------------------------------------------------\n")

        inp = ctk.CTkFrame(self, fg_color="transparent"); inp.pack(pady=(5, 12), padx=15, fill="x")
        self.ent = ctk.CTkEntry(inp, placeholder_text="Miku Emir Satırı...", fg_color="#0a0f1d", text_color="white", font=("Consolas", 13), height=42, border_color="#1e293b")
        self.ent.pack(side="left", fill="x", expand=True, padx=(0, 10)); self.ent.bind("<Return>", lambda e: self.tetik())
        ctk.CTkButton(inp, text="VUR", width=80, height=42, fg_color="#00E5FF", hover_color="#00b8d4", text_color="black", font=("Consolas", 13, "bold"), command=self.tetik).pack(side="right")

        threading.Thread(target=self.donanim_dongusu, daemon=True).start()
        threading.Thread(target=self.pasif_dinle, daemon=True).start()
        threading.Thread(target=self.alarm_bekcisi, daemon=True).start()
        threading.Thread(target=self.kusursuz_ota, daemon=True).start()

    def kusursuz_ota(self):
        if "SENIN-REPO-ADIN" in GITHUB_REPO: return
        time.sleep(4)
        try:
            req = urllib.request.Request(f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as r:
                d = json.loads(r.read().decode())
                if (uzak := d.get("tag_name", "").replace("v","").strip()) > YEREL_SURUM.replace("v","").strip():
                    self.ota_balon(d.get("tag_name"), d.get("html_url"))
        except Exception: pass

    def ota_balon(self, tag, link):
        b = ctk.CTkFrame(self, fg_color="#00E5FF", corner_radius=8); b.pack(fill="x", padx=15, pady=5, before=self.chat)
        ctk.CTkLabel(b, text=f"🚀 YENİ SÜRÜM ÇIKTI ({tag})!", font=("Consolas", 12, "bold"), text_color="black").pack(side="left", padx=10, pady=8)
        ctk.CTkButton(b, text="İNDİR", width=65, fg_color="black", text_color="white", font=("Consolas", 11, "bold"), command=lambda: webbrowser.open(link)).pack(side="right", padx=10, pady=4)

    def donanim_dongusu(self):
        while True:
            cpu, ram = saf_metal_telemetri()
            self.lbl_stats.configure(text=f"🔥 CPU Yükü: %{cpu} | 💾 RAM: %{ram} | 👑 Emir: {self.hafiza.veri['toplam_komut']}")
            time.sleep(1.2)

    def alarm_bekcisi(self):
        while True:
            simdi = datetime.datetime.now().strftime("%H:%M"); kl = []
            for al in self.hafiza.veri.get("alarmlar", []):
                if al["saat"] == simdi: self.log(f"\n[⏰ ALARM TETİKLENDİ] -> {al['saat']}\n"); AlarmSirenPenceresi(al.get("komut", "Uyanış!"))
                else: kl.append(al)
            self.hafiza.veri["alarmlar"] = kl; time.sleep(20)

    def log(self, m): self.chat.configure(state="normal"); self.chat.insert("end", m); self.chat.configure(state="disabled"); self.chat.see("end")
    
    def ses(self, m):
        # ★★★ ESKİ PYTTSX3 ÇÖPE ATILDI, SAF METAL ÇAĞRILIYOR ★★★
        threading.Thread(target=saf_metal_konus, args=(m,), daemon=True).start()

    def diril(self):
        try: self.deiconify(); self.lift(); self.focus_force()
        except Exception: pass

    def tetik(self):
        if not (m := self.ent.get().strip()): return
        self.ent.delete(0, "end"); self.log(f"[{self.hafiza.veri['patron']}] >>> {m}\n"); threading.Thread(target=self.isleyici, args=(m,), daemon=True).start()

    def isleyici(self, komut):
        self.hafiza.komut_islenildi(); niyet, hedef = self.beyin.niyet_analiz(komut); y = ""
        if niyet == "ALARM":
            sn, st = self.beyin.zaman_coz(komut); self.hafiza.veri["alarmlar"].append({"saat": st, "komut": komut}); self.hafiza.kaydet(); y = f"⏰ Alarm mühürlendi: Saat {st}'da çalacak!"
        elif niyet == "KAPAT":
            if "iptal" in komut: os.system("shutdown /a"); y = "🔴 Kapatma iptal!"
            else: sn, st = self.beyin.zaman_coz(komut); os.system(f"shutdown /s /t {sn}"); y = f"⚠️ Bilgisayar saat {st}'da kapanacak."
        elif niyet == "SS_AL": saf_metal_ekran_goruntusu(); y = "📸 [Saf Metal Kanca]: Ekran pikselleri yakalandı, Masaüstüne 'MIKU_SS.png' olarak bırakıldı."
        elif niyet == "KILITLE": ctypes.windll.user32.LockWorkStation(); y = "Sistem kilitlendi."
        elif niyet == "ZORLA_KAPAT": os.system(f"taskkill /f /im {hedef or 'chrome'}.exe"); y = f"'{hedef}.exe' zorla infaz edildi."
        elif niyet == "MEDYA_DURDUR": ctypes.windll.user32.keybd_event(0xB3, 0, 0, 0); ctypes.windll.user32.keybd_event(0xB3, 0, 2, 0); y = "Medya durduruldu."
        elif niyet == "MUZIK": s = hedef or "World is Mine"; webbrowser.open(self.beyin.cimbiz_sc(s) if "soundcloud" in komut else f"https://duckduckgo.com/?q=!ducky+site%3Ayoutube.com+{urllib.parse.quote(s)}"); y = f"Müzik açıldı: {s}"
        elif niyet == "HESAP": webbrowser.open("https://hesapmakinesi.com"); y = "Hesap makinesi açıldı."
        elif niyet == "UYGULAMA": subprocess.Popen(hedef or "notepad", shell=True); y = f"Açılıyor: {hedef}"
        elif niyet == "DIVA": os.chdir(r"D:\Oyunlar\Project DIVA Arcade"); subprocess.Popen("start diva.exe", shell=True); y = "Diva aktif."
        elif niyet == "TEMIZLE": self.chat.configure(state="normal"); self.chat.delete("1.0", "end"); self.chat.configure(state="disabled"); y = "Temizlendi."
        elif niyet == "DURUM": y = f"İşlemci: {self.islemci_adi} | Emir: {self.hafiza.veri['toplam_komut']}"
        elif niyet == "BULUT": y = self.beyin.bulut_danis(komut)
        self.log(f"[M.I.K.U.] >>> {y}\n\n"); self.ses(y)

    def pasif_dinle(self):
        r = sr.Recognizer(); r.energy_threshold = 300; r.dynamic_energy_threshold = True
        wake = self.hafiza.veri.get("uyandirma_kelimesi", "uyan").lower()
        with sr.Microphone() as k:
            r.adjust_for_ambient_noise(k, duration=1)
            while True:
                try:
                    ses = r.listen(k, phrase_time_limit=4); t = r.recognize_google(ses, language="tr-TR").lower()
                    if wake in t or "miku" in t:
                        self.diril()
                        if len(kalan := t.split(wake)[-1].strip() if wake in t else "") > 2:
                            self.log(f"[🎙️ Hızlı] >>> {kalan}\n"); threading.Thread(target=self.isleyici, args=(kalan,), daemon=True).start(); continue
                        winsound.MessageBeep(winsound.MB_ICONASTERISK); self.ses_bar.start()
                        try:
                            ks = r.listen(k, timeout=4, phrase_time_limit=6); self.ses_bar.stop()
                            km = r.recognize_google(ks, language="tr-TR"); self.log(f"[🎙️ Komut] >>> {km}\n"); threading.Thread(target=self.isleyici, args=(km,), daemon=True).start()
                        except Exception: self.ses_bar.stop(); self.ses("Pardon patron, duyamadım.")
                except Exception: pass

if __name__ == "__main__":
    MikuArayuz().mainloop()
