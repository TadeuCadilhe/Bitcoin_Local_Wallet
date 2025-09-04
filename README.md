# Local Wallet

**Local Wallet** is a simple, secure, and offline **Bitcoin wallet** written in Python.  
It allows you to transform **any old computer running Linux** into a **cold storage wallet**, keeping your Bitcoin safe and fully under your control.

---

## 🔒 Why Local Wallet?

- **Air-gapped security**: Run on an offline computer (no internet needed).
- **Re-purpose old hardware**: Any old Linux machine can become a secure Bitcoin wallet.
- **Modern Bitcoin standards**: Uses **BIP39** for mnemonics and **BIP84** for native SegWit bech32 (`bc1...`) addresses.
- **Encrypted vault**: Wallets are stored in a file protected with AES-256 encryption and a master password.
- **Privacy by design**: Your keys never leave the machine.
- **Retro aesthetics**: ASCII pixel-style UI, lightweight and hacker-friendly.
- **Donation support**: Easy QR code generation for BTC transactions.

---

## ✨ Features

- Generate new wallets with **12-word mnemonic** (BIP39).
- Import existing wallets with **12 or 24 words**.
- Optional **BIP39 passphrase** support.
- Derivation path: `m/84'/0'/0'/0/0`.
- Export private key in **WIF format** via QR code.
- List and delete wallets securely.
- **About the creator** section with donation QR code.

---

## 🛡️ Security

- Wallet file is encrypted with **AES-256 (PBKDF2-HMAC-SHA256)**.
- Only the **public address** is shown unless explicitly exporting the private key.
- Works 100% **offline** — no network connection required.
- Perfect for **cold storage** and **long-term HODLing**.
- Run it on a **Linux live USB** or **air-gapped computer** for maximum safety.

---

## 🖥️ Installation Guide (Linux)

### 1. Install Python
Most Linux distros already come with Python 3.  
Check your version:

```bash
python3 --version
```

If you don’t have Python 3.11+, install it:

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip -y
```

**Fedora:**
```bash
sudo dnf install python3 python3-pip -y
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip
```

---

### 2. Clone the repository

```bash
git clone https://github.com/TadeuCadilhe/local-wallet.git
cd local-wallet
```

---

### 3. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Install dependencies

```bash
pip install bip-utils cryptography qrcode colorama
```

---

### 5. Run the wallet

```bash
python local_wallet.py
```

---

## 🚀 Usage

Main menu:

```
█████████████████████████████
█         MAIN MENU          █
█████████████████████████████
█ 1 █ Create a new wallet    █
█ 2 █ Import an existing one █
█ 3 █ Access imported wallets█
█ 4 █ Delete imported wallets█
█ 5 █ Export wallet (QR WIF) █
█ 6 █ About the creator      █
█ 0 █ Exit                   █
█████████████████████████████
```

---

## 🙋 About the creator

Hi! My name is **Tadeu Cadilhe**, I’m a Bitcoin enthusiast just like you!  
If you’d like to support this project, consider a donation:  

**BTC Address:**  
`bc1qk4r2429qz90uy4nxal3sf2fxekg0g6zj72h6jg`

- [LinkedIn](https://www.linkedin.com/in/tadeu-cadilhe/)  
- [GitHub](https://github.com/TadeuCadilhe)  

---

⚡ Stay sovereign. Run offline. Protect your keys.
