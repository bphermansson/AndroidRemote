# Android Remote (Ubuntu 25.10 + Android)

En enkel mobilvanlig webbapp som visar knappar pa telefonen och kor fordefinierade kommandon pa din Ubuntu-dator.

## 1. Installera

```bash
cd /media/patrik/Extra1TB/Programmering/Python/AndroidRemote
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Konfigurera kommandon

Skapa lokal config (denna fil committas inte):

```bash
cp commands.example.json commands.json
```

Redigera `commands.json`:

- Byt `api_token` till ett langt hemligt token.
- Behall bara kommandon du verkligen vill tillata.
- `command` kors med shell pa servern, sa hall filen privat.

## 3. Starta servern

```bash
source .venv/bin/activate
uvicorn server.main:app --host 0.0.0.0 --port 8000
```

## 4. Oppna pa Android

- Oppna `http://DIN_UBUNTU_IP:8000` i mobilens webblasare.
- Skriv in samma server-URL och API-token.
- Tryck `Hamta knappar`.
- Installera som hemskarm-genvag via webblasaren (Add to Home screen).

## 4b. Anvand `ubuntu.local` via mDNS/Avahi

Pa Ubuntu 25.10:

```bash
sudo apt update
sudo apt install -y avahi-daemon libnss-mdns
sudo systemctl enable --now avahi-daemon
```

Kontrollera att datorn heter `ubuntu`:

```bash
hostnamectl
```

Om hostname inte ar `ubuntu`, byt:

```bash
sudo hostnamectl set-hostname ubuntu
sudo systemctl restart avahi-daemon
```

Verifiera lokalt:

```bash
getent hosts ubuntu.local
```

Nar detta fungerar, anvand i mobilen:

- `http://ubuntu.local:8000`

Obs: Telefon och Ubuntu maste vara pa samma lokala nat (samma Wi-Fi/LAN).

## 5. Rekommenderad hardning

- Kor helst bakom VPN (t.ex. Tailscale) i stallet for oppen port.
- Om du exponerar pa internet: lagg reverse proxy med TLS och IP-filter.
- Anvand en separat Linux-anvandare med minimal behorighet.

## Exempel: systemd-service

Skapa `/etc/systemd/system/android-remote.service`:

```ini
[Unit]
Description=Android Remote Commands API
After=network.target

[Service]
Type=simple
User=patrik
WorkingDirectory=/media/patrik/Extra1TB/Programmering/Python/AndroidRemote
ExecStart=/media/patrik/Extra1TB/Programmering/Python/AndroidRemote/.venv/bin/uvicorn server.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Aktivera:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now android-remote
sudo systemctl status android-remote
```
