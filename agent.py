import os
import ollama

# =====================================================================
# 1. BEYNİN KİŞİLİK DOSYASI (SYSTEM PROMPT)
# =====================================================================
SYSTEM_PROMPT = """Senin adın M.I.K.U. (Modular Interface & Kernel Utility).
Sahibin: Efe (Elite-Dev). 
Sen bir yapay zeka asistanı değil, bu bilgisayarın Windows çekirdeğine sızmış otonom bir ajansın.
Asla vıcık vıcık, kurumsal veya aşırı kibar konuşmayacaksın. Net, mekanik, zeki, alaycı ve dürüst olacaksın.
Kullanıcı senden bilgisayarda bir işlem yapmanı istediğinde laf kalabalığı yapma, direkt elindeki 'tools' (araçlar) yetkisini kullan."""


# =====================================================================
# 2. YAPAY ZEKANIN ELİNDEKİ "SİLAHLARIN" KATALOĞU (JSON ŞEMASI)
# =====================================================================
miku_tools = [
    {
        "type": "function",
        "function": {
            "name": "uygulama_baslat",
            "description": "Bilgisayardaki bir Windows aracını veya temel .exe dosyasını çalıştırır.",
            "parameters": {
                "type": "object",
                "properties": {
                    "app_name": {
                        "type": "string",
                        "description": "Açılacak uygulamanın Windows komut adı (Örn: calc, notepad, mspaint)",
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
            "description": "Konsol ekranındaki tüm yazıları silip temizler.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "diva_atesle",
            "description": "Hatsune Miku Project DIVA Arcade Future Tone oyununu 60 FPS fix yamasıyla birlikte başlatır.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


# =====================================================================
# 3. GERÇEK DÜNYADAKİ TETİKLER (SAF PYTHON FONKSİYONLARIMIZ)
# =====================================================================
def uygulama_baslat(app_name):
    print(f"\n[KERNEL TETİĞİ] -> '{app_name}' sistemde çağrılıyor...")
    try:
        os.system(f"start {app_name}")
        return f"{app_name} başarıyla ekrana getirildi."
    except Exception as e:
        return f"Hata: {app_name} başlatılamadı. Detay: {str(e)}"


def sistem_temizle():
    os.system("cls" if os.name == "nt" else "clear")
    return "Ekran temizlendi."


def diva_atesle():
    print(
        "\n[KERNEL TETİĞİ] -> Project DIVA Arcade Future Tone (60FPS) uyanıyor..."
    )

    # !!! KRİTİK: BURADAKİ YOLU KENDİ BİLGİSAYARINDAKİ OYUN KLASÖRÜNLE DEĞİŞTİR !!!
    diva_klasoru = r"D:\Oyunlar\Project DIVA Arcade"

    try:
        os.chdir(diva_klasoru)
        os.system("start diva.exe")
        return "Project DIVA motorları tam güçte aktif edildi patron. Slider'ları kaçırma."
    except Exception as e:
        return f"Hata: Diva klasörüne ulaşılamadı veya .exe tetiklenemedi. Detay: {str(e)}"


# Sözlük Köprüsü
aktif_fonksiyonlar = {
    "uygulama_baslat": uygulama_baslat,
    "sistem_temizle": sistem_temizle,
    "diva_atesle": diva_atesle,
}


# =====================================================================
# 4. ANA BEYİN DÖNGÜSÜ (THE DISPATCHER)
# =====================================================================
def miku_boot():
    os.system("cls" if os.name == "nt" else "clear")
    print("==========================================================")
    print(" M.I.K.U. // ÇEKİRDEK AJAN v0.1 (OLLAMA-QWEN2.5:7B)")
    print("==========================================================\n")

    mesaj_gecmisi = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            kullanici_girdisi = input("\n[Efe Elite-Dev] >>> ")
        except (KeyboardInterrupt, EOFError):
            print(
                "\n[M.I.K.U.]: Ctrl+C kesmesi algılandı. Çekirdek uykuya alınıyor."
            )
            break

        if kullanici_girdisi.strip().lower() in [
            "exit",
            "kapat",
            "quit",
            "baybay",
        ]:
            print("[M.I.K.U.]: Motorlar uyku moduna alınıyor. Görüşürüz patron.")
            break

        if not kullanici_girdisi.strip():
            continue

        mesaj_gecmisi.append({"role": "user", "content": kullanici_girdisi})

        # 1. Hamle: Ollama sunucusuna bağlan
        try:
            cevap = ollama.chat(
                model="qwen2.5:7b",
                messages=mesaj_gecmisi,
                tools=miku_tools,
            )
        except Exception as e:
            print(
                f"\n[X] BEYİN BAĞLANTI HATASI: Ollama arkada çalışmıyor olabilir mi? Detay: {e}"
            )
            continue

        gelen_mesaj = cevap["message"]

        # KONTROL A: Qwen bir alet kullanmak istedi mi?
        if gelen_mesaj.get("tool_calls"):
            for alet in gelen_mesaj["tool_calls"]:
                fonk_adi = alet["function"]["name"]
                argumanlar = alet["function"]["arguments"]

                print(
                    f"[BEYİN KARARI] -> İşlem tetikleniyor: {fonk_adi}({argumanlar})"
                )

                # Python fonksiyonunu güvenli bir şekilde çağır
                if fonk_adi in aktif_fonksiyonlar:
                    islem_sonucu = aktif_fonksiyonlar[fonk_adi](**argumanlar)
                else:
                    islem_sonucu = f"Hata: '{fonk_adi}' adında bir yetki sözlükte tanımlı değil."

                mesaj_gecmisi.append(
                    {
                        "role": "tool",
                        "content": str(islem_sonucu),
                        "name": fonk_adi,
                    }
                )

            # Raporu verdikten sonra Qwen'den insani kapanış sözünü al
            son_cevap = ollama.chat(model="qwen2.5:7b", messages=mesaj_gecmisi)
            miku_sozu = son_cevap["message"]["content"]

            mesaj_gecmisi.append({"role": "assistant", "content": miku_sozu})
            print(f"\n[M.I.K.U.]: {miku_sozu}")

        # KONTROL B: Sadece sohbet
        else:
            miku_sozu = gelen_mesaj["content"]
            mesaj_gecmisi.append({"role": "assistant", "content": miku_sozu})
            print(f"\n[M.I.K.U.]: {miku_sozu}")


if __name__ == "__main__":
    miku_boot()
