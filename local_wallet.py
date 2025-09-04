#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import base64
import secrets
import getpass
from typing import Dict, Any, List

from colorama import Fore, Style, init
import qrcode

# Cryptography
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

# Bitcoin / BIP39 / BIP84
from bip_utils import (
    Bip39MnemonicGenerator, Bip39WordsNum, Bip39MnemonicDecoder, Bip39SeedGenerator,
    Bip84, Bip84Coins, Bip44Changes
)

# Init colorama
init(autoreset=True)

VAULT_FILENAME = "local_wallet"
KDF_ITERATIONS = 200_000


# -------------------------
# Utils
# -------------------------
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pixel_banner(text: str, color=Fore.YELLOW):
    """Retro pixel ASCII banner"""
    border = "█" * (len(text) + 6)
    print(color + border)
    print(color + "█  " + Style.BRIGHT + Fore.CYAN + text.upper() + Style.RESET_ALL + color + "  █")
    print(color + border + Style.RESET_ALL)


# -------------------------
# Cryptography
# -------------------------
def _derive_key(password: str, salt: bytes, iterations: int = KDF_ITERATIONS) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations
    )
    key = kdf.derive(password.encode("utf-8"))
    return base64.urlsafe_b64encode(key)


def encrypt_container(password: str, data: Dict[str, Any]) -> Dict[str, Any]:
    salt = secrets.token_bytes(16)
    key = _derive_key(password, salt, KDF_ITERATIONS)
    f = Fernet(key)
    plaintext = json.dumps(data, ensure_ascii=False).encode("utf-8")
    ciphertext = f.encrypt(plaintext)
    return {
        "version": 1,
        "kdf": "pbkdf2_sha256",
        "iterations": KDF_ITERATIONS,
        "salt": base64.b64encode(salt).decode("utf-8"),
        "ciphertext": ciphertext.decode("utf-8"),
    }


def decrypt_container(password: str, container: Dict[str, Any]) -> Dict[str, Any]:
    try:
        salt = base64.b64decode(container["salt"])
        iterations = int(container.get("iterations", KDF_ITERATIONS))
        key = _derive_key(password, salt, iterations)
        f = Fernet(key)
        plaintext = f.decrypt(container["ciphertext"].encode("utf-8"))
        return json.loads(plaintext.decode("utf-8"))
    except Exception:
        raise ValueError("Wrong master password or corrupted vault file.")


# -------------------------
# Vault
# -------------------------
def vault_exists() -> bool:
    return os.path.exists(VAULT_FILENAME)


def load_vault(password: str) -> Dict[str, Any]:
    if not vault_exists():
        return {"wallets": []}
    with open(VAULT_FILENAME, "r", encoding="utf-8") as f:
        container = json.load(f)
    return decrypt_container(password, container)


def save_vault(password: str, data: Dict[str, Any]) -> None:
    container = encrypt_container(password, data)
    with open(VAULT_FILENAME, "w", encoding="utf-8") as f:
        json.dump(container, f, ensure_ascii=False, indent=2)


# -------------------------
# BIP39 / BIP84
# -------------------------
def generate_mnemonic_12() -> str:
    return Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_12)


def validate_mnemonic_12_or_24(mnemonic: str) -> None:
    words = [w.strip().lower() for w in mnemonic.strip().split()]
    if len(words) not in (12, 24):
        raise ValueError("Mnemonic must have 12 or 24 words.")
    Bip39MnemonicDecoder().Decode(mnemonic)


def derive_bech32_addr_m84(mnemonic: str, passphrase: str = "") -> str:
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passphrase)
    bip84_ctx = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
    account = bip84_ctx.Purpose().Coin().Account(0)
    change = account.Change(Bip44Changes.CHAIN_EXT)
    return change.AddressIndex(0).PublicKey().ToAddress()


def derive_privkey_wif(mnemonic: str, passphrase: str = "") -> str:
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate(passphrase)
    bip84_ctx = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
    account = bip84_ctx.Purpose().Coin().Account(0)
    change = account.Change(Bip44Changes.CHAIN_EXT)
    return change.AddressIndex(0).PrivateKey().ToWif()


# -------------------------
# QR Code
# -------------------------
def show_qr_terminal(data: str):
    qr = qrcode.QRCode(border=1)
    qr.add_data(data)
    qr.make(fit=True)
    qr.print_ascii(invert=True)


# -------------------------
# Flows
# -------------------------
def prompt_yes_no(msg: str) -> bool:
    opt = input(msg + " (y/n): ").strip().lower()
    return opt in ("y", "yes")


def create_new_wallet_flow(vault: Dict[str, Any]) -> None:
    clear_screen()
    pixel_banner("New Wallet", Fore.CYAN)
    name = input("Enter a name for your wallet: ").strip()
    mnemonic = str(generate_mnemonic_12())
    print(Style.BRIGHT + Fore.YELLOW + "\nWrite down your mnemonic (keep it offline and secure):")
    print(Style.BRIGHT + Fore.WHITE + mnemonic + "\n")
    use_pp = prompt_yes_no("Do you want to set a BIP39 passphrase?")
    passphrase = ""
    if use_pp:
        passphrase = getpass.getpass("Enter passphrase: ").strip()
        confirm = getpass.getpass("Confirm passphrase: ").strip()
        if passphrase != confirm:
            print(Fore.RED + "Passphrases do not match. Cancelling creation.")
            input("\nPress ENTER to return to the menu...")
            return
    try:
        address = derive_bech32_addr_m84(mnemonic, passphrase)
    except Exception as e:
        print(Fore.RED + f"Error deriving address: {e}")
        input("\nPress ENTER to return to the menu...")
        return
    vault["wallets"].append({
        "name": name, "mnemonic": mnemonic, "passphrase": passphrase, "address": address
    })
    print(Style.BRIGHT + Fore.GREEN + f"\nWallet created!\n{name} — {address}\n")
    input("Press ENTER to return to the menu...")


def import_wallet_flow(vault: Dict[str, Any]) -> None:
    clear_screen()
    pixel_banner("Import Wallet", Fore.MAGENTA)
    mnemonic = input("Enter the 12 or 24 words: ").strip().lower()
    try:
        validate_mnemonic_12_or_24(mnemonic)
    except Exception as e:
        print(Fore.RED + f"Error: {e}")
        input("\nPress ENTER to return to the menu...")
        return
    has_pp = prompt_yes_no("Does it have a passphrase?")
    passphrase = ""
    if has_pp:
        passphrase = getpass.getpass("Enter passphrase: ").strip()
    name = input("Enter a name for your wallet: ").strip()
    try:
        address = derive_bech32_addr_m84(mnemonic, passphrase)
    except Exception as e:
        print(Fore.RED + f"Error deriving address: {e}")
        input("\nPress ENTER to return to the menu...")
        return
    vault["wallets"].append({
        "name": name, "mnemonic": mnemonic, "passphrase": passphrase, "address": address
    })
    print(Style.BRIGHT + Fore.GREEN + f"\nWallet imported!\n{name} — {address}\n")
    input("Press ENTER to return to the menu...")


def list_wallets_flow(vault: Dict[str, Any]) -> None:
    clear_screen()
    pixel_banner("Wallets", Fore.YELLOW)
    wallets: List[Dict[str, Any]] = vault.get("wallets", [])
    if not wallets:
        print(Fore.RED + "No wallets found.\n")
    else:
        for i, w in enumerate(wallets, start=1):
            try:
                addr = derive_bech32_addr_m84(w["mnemonic"], w.get("passphrase", ""))
            except Exception:
                addr = w.get("address", "<error deriving>")
            print(Style.BRIGHT + Fore.CYAN + f"[{i}] {w.get('name','(no name)')} — {addr}")
    input("\nPress ENTER to return to the menu...")


def delete_wallets_flow(vault: Dict[str, Any]) -> None:
    clear_screen()
    pixel_banner("Delete Wallets", Fore.RED)
    wallets = vault.get("wallets", [])
    if not wallets:
        print(Fore.RED + "No wallets found.\n")
        input("\nPress ENTER to return to the menu...")
        return
    for i, w in enumerate(wallets, start=1):
        print(f"[{i}] {w.get('name','(no name)')}")
    choice = input("Enter indexes (e.g., 1,3) or 'all': ").strip().lower()
    if choice == "all":
        confirm = prompt_yes_no("Are you sure you want to delete ALL wallets?")
        if confirm:
            vault["wallets"] = []
            print(Style.BRIGHT + Fore.GREEN + "All wallets removed.\n")
        else:
            print("Action canceled.\n")
    else:
        try:
            indexes = [int(x.strip()) for x in choice.split(",") if x.strip()]
            indexes = sorted(set(indexes), reverse=True)
            for idx in indexes:
                if 1 <= idx <= len(wallets):
                    del vault["wallets"][idx - 1]
            print(Style.BRIGHT + Fore.GREEN + "Selected wallets removed.\n")
        except Exception:
            print(Fore.RED + "Invalid input. No wallet removed.\n")
    input("Press ENTER to return to the menu...")


def export_wallet_flow(vault: Dict[str, Any]) -> None:
    clear_screen()
    pixel_banner("Export Wallet", Fore.YELLOW)
    wallets = vault.get("wallets", [])
    if not wallets:
        print(Fore.RED + "No wallets found.\n")
        input("\nPress ENTER to return to the menu...")
        return

    for i, w in enumerate(wallets, start=1):
        print(f"[{i}] {w.get('name','(no name)')}")
    choice = input("Choose wallet to export: ").strip()
    if not choice.isdigit() or not (1 <= int(choice) <= len(wallets)):
        print(Fore.RED + "Invalid choice.")
        input("\nPress ENTER to return to the menu...")
        return

    w = wallets[int(choice)-1]
    priv_wif = derive_privkey_wif(w["mnemonic"], w.get("passphrase", ""))
    print(Fore.CYAN + f"\nPrivate WIF key of wallet '{w['name']}':\n")
    show_qr_terminal(priv_wif)
    print(Fore.YELLOW + "\n⚠️  Warning: whoever has access to this key controls your funds!")
    input("\nPress ENTER to return to the menu...")


def about_creator_flow() -> None:
    clear_screen()
    pixel_banner("About the Creator", Fore.MAGENTA)
    print(Style.BRIGHT + Fore.CYAN + "Hello, my name is Tadeu Cadilhe and I am a Bitcoin enthusiast, just like you!")
    print(Style.BRIGHT + Fore.CYAN + "Do you want to help this project grow? Consider making a donation using the QR Code below:\n")
    print(Fore.YELLOW + "▶ LinkedIn: " + Fore.WHITE + "https://www.linkedin.com/in/tadeu-cadilhe/")
    print(Fore.YELLOW + "▶ GitHub:   " + Fore.WHITE + "https://github.com/TadeuCadilhe\n")
    btc_address = "bc1qk4r2429qz90uy4nxal3sf2fxekg0g6zj72h6jg"
    print(Fore.GREEN + f"Donation address: {btc_address}\n")
    show_qr_terminal("bitcoin:" + btc_address)
    input("\nPress ENTER to return to the menu...")


# -------------------------
# Menu
# -------------------------
def show_menu():
    clear_screen()
    pixel_banner("Local Wallet", Fore.YELLOW)

    menu_items = [
        ("1", "Create a new wallet"),
        ("2", "Import an existing wallet"),
        ("3", "Access imported wallets"),
        ("4", "Delete imported wallets"),
        ("5", "Export wallet (QR of private key)"),
        ("6", "About the creator"),
        ("0", "Exit"),
    ]

    width = max(len(text) for _, text in menu_items) + 8
    border = "█" * width

    print(Fore.CYAN + border)
    print(Fore.CYAN + "█" + " MAIN MENU".center(width - 2) + "█")
    print(Fore.CYAN + border)

    for key, text in menu_items:
        color = Fore.RED if key == "0" else Fore.GREEN
        line_text = f" {key} ".ljust(4) + text.ljust(width - 6)
        line = f"█{line_text}█"
        print(color + line)

    print(Fore.CYAN + border + Style.RESET_ALL)


# -------------------------
# Main
# -------------------------
def main():
    clear_screen()
    pixel_banner("Local Wallet", Fore.YELLOW)
    print(Style.BRIGHT + Fore.CYAN + "Welcome to your offline wallet!\n")
    if vault_exists():
        master = getpass.getpass("Enter your master password: ")
        try:
            vault = load_vault(master)
        except Exception as e:
            print(Fore.RED + str(e))
            sys.exit(1)
    else:
        print(Fore.MAGENTA + "First use detected. Set a master password.")
        while True:
            p1 = getpass.getpass("Create a master password: ")
            p2 = getpass.getpass("Confirm master password: ")
            if p1 != p2:
                print(Fore.RED + "Passwords do not match. Try again.")
                continue
            if len(p1) < 8:
                print(Fore.RED + "Use at least 8 characters.")
                continue
            master = p1
            vault = {"wallets": []}
            save_vault(master, vault)
            print(Style.BRIGHT + Fore.GREEN + "Vault created successfully!\n")
            input("Press ENTER to continue...")
            clear_screen()
            break

    while True:
        show_menu()
        opt = input("> ").strip()
        if opt == "1":
            create_new_wallet_flow(vault)
            save_vault(master, vault)
        elif opt == "2":
            import_wallet_flow(vault)
            save_vault(master, vault)
        elif opt == "3":
            list_wallets_flow(vault)
        elif opt == "4":
            delete_wallets_flow(vault)
            save_vault(master, vault)
        elif opt == "5":
            export_wallet_flow(vault)
        elif opt == "6":
            about_creator_flow()
        elif opt == "0":
            clear_screen()
            pixel_banner("Exiting", Fore.RED)
            input("\nPress ENTER to finish...")
            clear_screen()
            break
        else:
            print(Fore.RED + "Invalid option.\n")
            input("Press ENTER to return to the menu...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        pixel_banner("Closed", Fore.RED)
        input("\nPress ENTER to exit...")
        clear_screen()

