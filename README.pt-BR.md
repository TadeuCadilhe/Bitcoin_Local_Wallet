# Local Wallet

**Local Wallet** é uma carteira de **Bitcoin offline, simples e segura**, escrita em Python.  
Ela permite transformar **qualquer computador antigo rodando Linux** em uma **carteira fria (cold storage)**, mantendo seus Bitcoins seguros e totalmente sob seu controle.

---

## 🔒 Por que usar o Local Wallet?

- **Segurança offline (air-gapped)**: Execute em um computador sem internet.
- **Reaproveite hardware antigo**: Qualquer máquina Linux pode virar uma carteira segura.
- **Padrões modernos do Bitcoin**: Utiliza **BIP39** para mnemônicos e **BIP84** para endereços bech32 (`bc1...`).
- **Cofre criptografado**: As carteiras são armazenadas em um arquivo protegido com criptografia AES-256 e senha mestra.
- **Privacidade garantida**: Suas chaves nunca saem do computador.
- **Estilo retrô**: Interface em ASCII pixelado, leve e prática.
- **Suporte a doações**: Geração simples de QR Code para transferências BTC.

---

## ✨ Funcionalidades

- Criar novas carteiras com **mnemônico de 12 palavras** (BIP39).
- Importar carteiras existentes com **12 ou 24 palavras**.
- Suporte a **passphrase BIP39 opcional**.
- Caminho de derivação: `m/84'/0'/0'/0/0`.
- Exportar chave privada em **WIF** via QR Code.
- Listar e deletar carteiras com segurança.
- Sessão **"Sobre o criador"** com QR Code de doação.

---

## 🛡️ Segurança

- Arquivo da carteira criptografado com **AES-256 (PBKDF2-HMAC-SHA256)**.
- Apenas o **endereço público** é exibido, a não ser que o usuário exporte a chave privada.
- Funciona 100% **offline** — sem conexão com a rede.
- Ideal para **cold storage** e **HODL de longo prazo**.
- Pode ser usado em um **Linux live USB** ou computador **air-gapped** para máxima proteção.

---

## 🖥️ Guia de Instalação (Linux)

### 1. Instale o Python
A maioria das distribuições já vem com Python 3.  
Verifique sua versão:

```bash
python3 --version
```

Se não tiver o Python 3.11+, instale com:

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

### 2. Clone o repositório

```bash
git clone https://github.com/TadeuCadilhe/local-wallet.git
cd local-wallet
```

---

### 3. Crie um ambiente virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Instale as dependências

```bash
pip install bip-utils cryptography qrcode colorama
```

---

### 5. Execute a carteira

```bash
python local_wallet.py
```

---

## 🚀 Uso

Menu principal:

```
█████████████████████████████
█        MENU PRINCIPAL      █
█████████████████████████████
█ 1 █ Criar nova carteira    █
█ 2 █ Importar carteira      █
█ 3 █ Acessar carteiras      █
█ 4 █ Deletar carteiras      █
█ 5 █ Exportar carteira (QR) █
█ 6 █ Sobre o criador        █
█ 0 █ Sair                   █
█████████████████████████████
```

---

## 🙋 Sobre o criador

Olá! Meu nome é **Tadeu Cadilhe**, sou um entusiasta de Bitcoin assim como você!  
Se quiser apoiar este projeto, considere uma doação:  

**Endereço BTC:**  
`bc1qk4r2429qz90uy4nxal3sf2fxekg0g6zj72h6jg`

- [LinkedIn](https://www.linkedin.com/in/tadeu-cadilhe/)  
- [GitHub](https://github.com/TadeuCadilhe)  

---

⚡ Mantenha sua soberania. Rode offline. Proteja suas chaves.
