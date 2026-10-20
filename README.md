# 🤖 Telegram Daivinchik Tanyşlyk Boty (100% Mugt Doretmek)

Bu taslama Telegramda edil **Leonardo Daivinchik** ýaly işleýän, anketalary tanyşdyrýan we özara halama (Match) bolanda kontakt paýlaşýan botdyr.

---

## ❓ Soraglara Jogaplar

### 1. Hiç hili çykdajy etmän (0 TMT / 0$) döredip bolarmy?
**Hawa, 100% mugt döredip bolýar!**
- **Telegram Bot API**: Telegramdan bot döretmek doly mugt.
- **Python we Kitaphana**: Aiogram we aiosqlite doly mugt (açyk çeşmeli).
- **Mugt Serwer (Hosting)**:
  - **Render.com**: Background Worker ýa-da Web Service hökmünde mugt tier bar.
  - **Railway.app**: Aýda 5$ mugt kredit berýär (bot üçin ýeterlik).
  - **PythonAnywhere.com**: Mugt Python hosting.
  - **Kompýuteriňiz ýa-da Telefonyňyz (Termux)**: Öýüňizdäki kompýuterde ýa-da Android telefonda Termux arkaly 24/7 mugt işletmek bolýar.

---

## 🛠️ Boty 5 Minutda Döretmek we Işletmek

### 1-nji Ädim: Telegramdan Token Almak
1. Telegramda **@BotFather** gözläň we girip `/start` basyň.
2. `/newbot` komandasyny ýazyň.
3. Botyň adyny ýazyň (mysal: `Tanyslyk Turkmen Bot`).
4. Botyň username-ini ýazyň (mysal: `turkmen_tanyslyk_bot` - soňy `bot` bilen gutarmaly).
5. BotFather size şeýle görnüşde **API Token** berer:
   `7182938475:AAH_XYZ...abc`
   Bu tokeni ýatda saklaň!

### 2-nji Ädim: Kompýuteriňizde Barlap Görmek
1. Python 3 gurulan bolmaly (python.org).
2. Papka açyp, kitaphana gurmaly:
   ```bash
   pip install aiogram aiosqlite python-dotenv
   ```
3. `.env` faýlyna tokeni goýuň:
   ```
   BOT_TOKEN="siz_alan_tokeniniz"
   ```
4. Boty işlediň:
   ```bash
   python main.py
   ```
5. Telegramda öz döreden botuňyza girip `/start` basyň!

---

## 🚀 24/7 Mugt Serwere (Render.com) Goýmak

1. Bütin taslamany [GitHub](https://github.com)-a ýükläň (Private repo edip bilersiňiz).
2. [Render.com](https://render.com)-da mugt hasap açyň.
3. **New +** düwmesine basyp **Background Worker** saýlaň.
4. GitHub repozitoriýaňyzy birikdiriň.
5. Sazlamalar:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Environment Variables**: `BOT_TOKEN` = siziň tokeniňiz.
6. **Create Background Worker** basyň. Botyňyz 24 sagat öçmän mugt işlär!
