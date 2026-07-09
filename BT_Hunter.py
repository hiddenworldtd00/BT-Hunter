#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ██████╗ ████████╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗  ║
║   ██╔══██╗╚══██╔══╝    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗ ║
║   ██████╔╝   ██║       ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝ ║
║   ██╔══██╗   ██║       ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗ ║
║   ██████╔╝   ██║       ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║ ║
║   ╚═════╝    ╚═╝       ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝ ║
║                                                                              ║
║   Développé par HiddenWorld Communauté Tchadienne                            ║
║   Outil de Surveillance & Contrôle Bluetooth Avancé                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import threading
import subprocess
import re
from datetime import datetime
from collections import deque

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class Fore:
        RED = '\033[91m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        BLUE = '\033[94m'
        MAGENTA = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        RESET = '\033[0m'
    class Style:
        BRIGHT = '\033[1m'
        RESET_ALL = '\033[0m'

class Colors:
    R = Fore.RED
    G = Fore.GREEN
    Y = Fore.YELLOW
    B = Fore.BLUE
    M = Fore.MAGENTA
    C = Fore.CYAN
    W = Fore.WHITE
    RST = Style.RESET_ALL
    BD = Style.BRIGHT

LOGO_BT = """
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣶⣿⣿⣷⣶⣄⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣾⣿⣿⡿⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣀⠀⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⢀⣾⣿⣿⡟⠁⣰⣿⣿⣿⡿⠿⠻⠿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⠏⠀⣴⣿⣿⣿⠉⠀⠀⠀⠀⠀⠈⢻⣿⣿⣇⠀⠀⠀⠀
        ⠀⠀⠀⠀⢀⣠⣼⣿⣿⡏⠀⢠⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⡀⠀⠀⠀
        ⠀⠀⠀⣰⣿⣿⣿⣿⣿⡇⠀⢸⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⡇⠀⠀⠀
        ⠀⠀⢰⣿⣿⡿⣿⣿⣿⡇⠀⠘⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⢀⣸⣿⣿⣿⠁⠀⠀⠀
        ⠀⠀⣿⣿⣿⠁⣿⣿⣿⡇⠀⠀⠻⣿⣿⣿⣷⣶⣶⣶⣶⣶⣿⣿⣿⣿⠃⠀⠀⠀⠀
        ⠀⢰⣿⣿⡇⠀⣿⣿⣿⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀
        ⠀⢸⣿⣿⡇⠀⣿⣿⣿⠀⠀⠀⠀⠀⠀⠉⠛⠛⠛⠉⢉⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀
        ⠀⢸⣿⣿⣇⠀⣿⣿⣿⠀⠀⠀⠀⠀⢀⣤⣤⣤⡀⠀⠀⣿⣿⣷⣦⣄⠀⠀⠀⠀⠀
        ⠀⠀⢻⣿⣿⣶⣿⣿⣿⠀⠀⠀⠀⠀⠈⠻⣿⣿⣿⣦⡀⠀⠉⠉⠻⣿⣿⡇⠀⠀⠀
        ⠀⠀⠀⠛⠿⣿⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀⠈⠹⣿⣿⣇⣀⠀⣠⣾⣿⣿⡇⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣦⣤⣤⣤⣤⣾⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠻⢿⣿⣿⣿⣿⣿⣿⠿⠋⠉⠛⠋⠉⠉⠁⠀⠀⠀⠀⠀
        ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠁
"""

class BTHunter:
    def __init__(self):
        self.devices = {}
        self.paired_devices = []
        self.scan_history = deque(maxlen=100)
        self.monitoring = False
        self.alert_mode = False
        self.auto_disconnect = False
        self.target_devices = []
        self.log_file = f"bt_hunter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        self.interface = "hci0"
        self.ensure_bluetooth()
        
    def ensure_bluetooth(self):
        try:
            subprocess.run(['systemctl', 'start', 'bluetooth'], check=False, capture_output=True)
            subprocess.run(['hciconfig', self.interface, 'up'], check=False, capture_output=True)
        except:
            pass
    
    def clear(self):
        os.system('clear')
    
    def banner(self):
        self.clear()
        print(f"{Colors.C}{Colors.BD}{LOGO_BT}{Colors.RST}")
        print(f"{Colors.G}{Colors.BD}        B T   H U N T E R{Colors.RST}")
        print(f"{Colors.M}        HiddenWorld - Hackers Tchadiens{Colors.RST}")
        print(f"{Colors.Y}        Outil de Surveillance Bluetooth Avancé{Colors.RST}")
        print(f"{Colors.C}{'═'*80}{Colors.RST}")
    
    def log(self, msg):
        entry = f"[{datetime.now().strftime('%H:%M:%S')}] {msg}"
        self.scan_history.append(entry)
        with open(self.log_file, 'a') as f:
            f.write(entry + '\n')
    
    def scan_devices(self):
        print(f"\n{Colors.G}[+] Scan des appareils Bluetooth...{Colors.RST}")
        try:
            result = subprocess.run(
                ['hcitool', 'scan', '--flush'],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                found = []
                for line in lines:
                    parts = line.strip().split('\t')
                    if len(parts) >= 2:
                        mac = parts[0].strip()
                        name = parts[1].strip()
                        found.append({'mac': mac, 'name': name, 'time': datetime.now().isoformat()})
                        self.devices[mac] = {'name': name, 'last_seen': datetime.now()}
                
                print(f"\n{Colors.C}[*] {len(found)} appareil(s) trouvé(s):{Colors.RST}")
                for i, dev in enumerate(found, 1):
                    print(f"  {Colors.BD}[{i}]{Colors.RST} {Colors.Y}{dev['name']}{Colors.RST}")
                    print(f"      MAC: {Colors.C}{dev['mac']}{Colors.RST}")
                    print(f"      Signal: {self.get_signal_strength(dev['mac'])}")
                self.log(f"Scan: {len(found)} appareils trouvés")
                return found
            else:
                print(f"{Colors.R}[!] Erreur scan. Essayez avec sudo.{Colors.RST}")
                return []
        except Exception as e:
            print(f"{Colors.R}[!] Erreur: {e}{Colors.RST}")
            return []
    
    def get_signal_strength(self, mac):
        try:
            result = subprocess.run(
                ['hcitool', 'rssi', mac],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                rssi = re.search(r'-?\d+', result.stdout)
                if rssi:
                    val = int(rssi.group())
                    if val > -50:
                        return f"{Colors.G}●●●●● Excellent ({val} dBm){Colors.RST}"
                    elif val > -70:
                        return f"{Colors.Y}●●●●○ Bon ({val} dBm){Colors.RST}"
                    else:
                        return f"{Colors.R}●●○○○ Faible ({val} dBm){Colors.RST}"
            return f"{Colors.D}○○○○○ Inconnu{Colors.RST}"
        except:
            return f"{Colors.D}○○○○○ N/A{Colors.RST}"
    
    def scan_le_devices(self):
        print(f"\n{Colors.G}[+] Scan Bluetooth Low Energy (BLE)...{Colors.RST}")
        try:
            result = subprocess.run(
                ['hcitool', 'lescan', '--duplicates'],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                found = []
                for line in lines:
                    if line.startswith('LE Scan'):
                        continue
                    parts = line.strip().split(' ')
                    if len(parts) >= 2:
                        mac = parts[0]
                        name = ' '.join(parts[1:]) if len(parts) > 1 else 'Inconnu'
                        found.append({'mac': mac, 'name': name})
                
                print(f"\n{Colors.C}[*] {len(found)} appareil(s) BLE trouvé(s):{Colors.RST}")
                for dev in found:
                    print(f"  {Colors.Y}{dev['name']}{Colors.RST} | {Colors.C}{dev['mac']}{Colors.RST}")
                self.log(f"BLE Scan: {len(found)} appareils")
                return found
        except Exception as e:
            print(f"{Colors.R}[!] Erreur: {e}{Colors.RST}")
            return []
    
    def get_device_info(self, mac):
        print(f"\n{Colors.G}[+] Informations sur {mac}...{Colors.RST}")
        try:
            result = subprocess.run(
                ['hcitool', 'name', mac],
                capture_output=True, text=True, timeout=5
            )
            name = result.stdout.strip() if result.returncode == 0 else "Inconnu"
            
            result2 = subprocess.run(
                ['sdptool', 'browse', mac],
                capture_output=True, text=True, timeout=10
            )
            services = []
            if result2.returncode == 0:
                for line in result2.stdout.split('\n'):
                    if 'Service Name:' in line:
                        services.append(line.split(':')[1].strip())
            
            print(f"\n{Colors.C}Nom:{Colors.RST} {Colors.BD}{name}{Colors.RST}")
            print(f"{Colors.C}MAC:{Colors.RST} {mac}")
            print(f"{Colors.C}Services:{Colors.RST}")
            for svc in services[:10]:
                print(f"  • {Colors.Y}{svc}{Colors.RST}")
            
            self.log(f"Info: {mac} - {name}")
        except Exception as e:
            print(f"{Colors.R}[!] Erreur: {e}{Colors.RST}")
    
    def continuous_scan(self):
        print(f"\n{Colors.G}[+] Mode scan continu activé...{Colors.RST}")
        print(f"{Colors.Y}[*] Ctrl+C pour arrêter{Colors.RST}")
        try:
            while True:
                self.scan_devices()
                time.sleep(5)
        except KeyboardInterrupt:
            print(f"\n{Colors.Y}[*] Scan continu arrêté{Colors.RST}")
    
    def monitor_mode(self):
        print(f"\n{Colors.G}[+] Mode surveillance activé...{Colors.RST}")
        self.monitoring = True
        known_devices = set()
        
        print(f"{Colors.Y}[*] Surveillance des nouveaux appareils...{Colors.RST}")
        try:
            while self.monitoring:
                result = subprocess.run(
                    ['hcitool', 'scan', '--flush'],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')[1:]
                    for line in lines:
                        parts = line.strip().split('\t')
                        if len(parts) >= 2:
                            mac = parts[0].strip()
                            name = parts[1].strip()
                            if mac not in known_devices:
                                known_devices.add(mac)
                                print(f"\n{Colors.G}[NOUVEAU] {Colors.BD}{name}{Colors.RST}")
                                print(f"         MAC: {Colors.C}{mac}{Colors.RST}")
                                print(f"         Heure: {datetime.now().strftime('%H:%M:%S')}")
                                self.log(f"NOUVEAU: {name} - {mac}")
                                
                                if self.alert_mode:
                                    self.trigger_alert(name, mac)
                                if self.auto_disconnect and mac in self.target_devices:
                                    self.disconnect_device(mac)
                time.sleep(3)
        except KeyboardInterrupt:
            self.monitoring = False
            print(f"\n{Colors.Y}[*] Surveillance arrêtée{Colors.RST}")
    
    def trigger_alert(self, name, mac):
        print(f"\n{Colors.R}{Colors.BD}╔══════════════════════════════════════╗")
        print(f"║     ⚠️  ALERTE BLUETOOTH  ⚠️        ║")
        print(f"╠══════════════════════════════════════╣")
        print(f"║  Appareil: {name[:25]:25} ║")
        print(f"║  MAC: {mac:30} ║")
        print(f"║  Heure: {datetime.now().strftime('%H:%M:%S'):27} ║")
        print(f"╚══════════════════════════════════════╝{Colors.RST}")
        
        # Son d'alerte
        try:
            subprocess.run(['paplay', '/usr/share/sounds/freedesktop/stereo/alarm.oga'], 
                         check=False, capture_output=True)
        except:
            print('\a')
    
    def disconnect_device(self, mac):
        print(f"\n{Colors.R}[!] Tentative de déconnexion de {mac}...{Colors.RST}")
        try:
            result = subprocess.run(
                ['hcitool', 'dc', mac],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print(f"{Colors.G}[+] Déconnexion réussie!{Colors.RST}")
                self.log(f"Déconnexion: {mac}")
            else:
                print(f"{Colors.Y}[*] Résultat: {result.stderr}{Colors.RST}")
        except Exception as e:
            print(f"{Colors.R}[!] Erreur: {e}{Colors.RST}")
    
    def list_paired(self):
        print(f"\n{Colors.G}[+] Appareils appairés...{Colors.RST}")
        try:
            result = subprocess.run(
                ['bluetoothctl', 'paired-devices'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'Device' in line:
                        parts = line.split(' ')
                        if len(parts) >= 3:
                            mac = parts[1]
                            name = ' '.join(parts[2:])
                            print(f"  {Colors.G}●{Colors.RST} {Colors.BD}{name}{Colors.RST}")
                            print(f"     MAC: {Colors.C}{mac}{Colors.RST}")
        except Exception as e:
            print(f"{Colors.R}[!] Erreur: {e}{Colors.RST}")
    
    def remove_device(self, mac):
        print(f"\n{Colors.Y}[!] Suppression de {mac}...{Colors.RST}")
        try:
            result = subprocess.run(
                ['bluetoothctl', 'remove', mac],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print(f"{Colors.G}[+] Appareil supprimé!{Colors.RST}")
                self.log(f"Suppression: {mac}")
            else:
                print(f"{Colors.R}[!] Échec: {result.stderr}{Colors.RST}")
        except Exception as e:
            print(f"{Colors.R}[!] Erreur: {e}{Colors.RST}")
    
    def block_device(self, mac):
        print(f"\n{Colors.R}[!] Blocage de {mac}...{Colors.RST}")
        try:
            with open('/etc/bluetooth/rfcomm.conf', 'a') as f:
                f.write(f"# Bloqué: {mac}\n")
            print(f"{Colors.G}[+] Appareil bloqué (nécessite redémarrage bluetooth){Colors.RST}")
            self.log(f"Blocage: {mac}")
        except Exception as e:
            print(f"{Colors.R}[!] Erreur: {e}{Colors.RST}")
    
    def spoof_mac(self):
        print(f"\n{Colors.G}[+] Spoofing MAC Bluetooth...{Colors.RST}")
        new_mac = input(f"{Colors.C}[?] Nouvelle MAC (xx:xx:xx:xx:xx:xx): {Colors.RST}").strip()
        if new_mac and re.match(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$', new_mac):
            try:
                subprocess.run(['hciconfig', self.interface, 'down'], check=False)
                subprocess.run(['hciconfig', self.interface, 'hci', 'reset'], check=False)
                result = subprocess.run(
                    ['bdaddr', '-i', self.interface, new_mac],
                    capture_output=True, text=True
                )
                subprocess.run(['hciconfig', self.interface, 'up'], check=False)
                print(f"{Colors.G}[+] MAC changée en {new_mac}{Colors.RST}")
                self.log(f"MAC spoof: {new_mac}")
            except Exception as e:
                print(f"{Colors.R}[!] Erreur: {e}{Colors.RST}")
        else:
            print(f"{Colors.R}[!] MAC invalide{Colors.RST}")
    
    def l2ping_flood(self, mac):
        print(f"\n{Colors.R}[!] L2Ping Flood sur {mac}...{Colors.RST}")
        print(f"{Colors.Y}[*] Ctrl+C pour arrêter{Colors.RST}")
        try:
            count = 0
            while True:
                subprocess.run(
                    ['l2ping', '-c', '1', mac],
                    capture_output=True, timeout=2
                )
                count += 1
                print(f"\r{Colors.C}Paquets envoyés: {Colors.BD}{count}{Colors.RST}", end="")
        except KeyboardInterrupt:
            print(f"\n{Colors.Y}[*] Flood arrêté. Total: {count}{Colors.RST}")
        except Exception as e:
            print(f"{Colors.R}[!] Erreur: {e}{Colors.RST}")
    
    def sdp_scan(self, mac):
        print(f"\n{Colors.G}[+] Scan SDP sur {mac}...{Colors.RST}")
        try:
            result = subprocess.run(
                ['sdptool', 'browse', mac],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                print(result.stdout)
                self.log(f"SDP Scan: {mac}")
            else:
                print(f"{Colors.R}[!] Échec{Colors.RST}")
        except Exception as e:
            print(f"{Colors.R}[!] Erreur: {e}{Colors.RST}")
    
    def rfcomm_scan(self):
        print(f"\n{Colors.G}[+] Scan ports RFCOMM...{Colors.RST}")
        try:
            result = subprocess.run(
                ['rfcomm', 'show', 'all'],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                print(result.stdout if result.stdout else "Aucun canal RFCOMM actif")
            else:
                print(f"{Colors.R}[!] Échec{Colors.RST}")
        except Exception as e:
            print(f"{Colors.R}[!] Erreur: {e}{Colors.RST}")
    
    def hci_dump(self):
        print(f"\n{Colors.G}[+] Capture HCI (hcidump)...{Colors.RST}")
        print(f"{Colors.Y}[*] Nécessite root. Ctrl+C pour arrêter{Colors.RST}")
        try:
            subprocess.run(['hcidump', '-X', '-t'], timeout=30)
        except subprocess.TimeoutExpired:
            pass
        except KeyboardInterrupt:
            print(f"\n{Colors.Y}[*] Capture arrêtée{Colors.RST}")
    
    def show_log(self):
        print(f"\n{Colors.G}[+] Journal des activités...{Colors.RST}")
        for entry in self.scan_history:
            print(f"  {Colors.D}{entry}{Colors.RST}")
    
    def export_json(self):
        filename = f"bt_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        data = {
            'devices': self.devices,
            'history': list(self.scan_history),
            'export_time': datetime.now().isoformat()
        }
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n{Colors.G}[+] Exporté: {filename}{Colors.RST}")
    
    def toggle_alert(self):
        self.alert_mode = not self.alert_mode
        status = f"{Colors.G}ACTIVÉ{Colors.RST}" if self.alert_mode else f"{Colors.R}DÉSACTIVÉ{Colors.RST}"
        print(f"\n{Colors.C}[*] Mode alerte: {status}{Colors.RST}")
    
    def toggle_auto_disconnect(self):
        self.auto_disconnect = not self.auto_disconnect
        status = f"{Colors.G}ACTIVÉ{Colors.RST}" if self.auto_disconnect else f"{Colors.R}DÉSACTIVÉ{Colors.RST}"
        print(f"\n{Colors.C}[*] Déconnexion auto: {status}{Colors.RST}")
        if self.auto_disconnect:
            macs = input(f"{Colors.C}[?] MAC cibles (séparées par virgule): {Colors.RST}").strip()
            self.target_devices = [m.strip() for m in macs.split(',') if m.strip()]
    
    def change_interface(self):
        iface = input(f"{Colors.C}[?] Interface (défaut: hci0): {Colors.RST}").strip()
        if iface:
            self.interface = iface
            print(f"{Colors.G}[+] Interface: {iface}{Colors.RST}")
    
    def reset_bluetooth(self):
        print(f"\n{Colors.Y}[!] Redémarrage du service Bluetooth...{Colors.RST}")
        try:
            subprocess.run(['systemctl', 'restart', 'bluetooth'], check=True)
            subprocess.run(['hciconfig', self.interface, 'up'], check=False)
            print(f"{Colors.G}[+] Bluetooth redémarré!{Colors.RST}")
        except Exception as e:
            print(f"{Colors.R}[!] Erreur: {e}{Colors.RST}")
    
    def show_menu(self):
        self.banner()
        print(f"\n{Colors.BD}{Colors.C}  ╔══════════════════════════════════════════════════════════════╗")
        print(f"  ║                    MENU PRINCIPAL BT HUNTER                  ║")
        print(f"  ╠══════════════════════════════════════════════════════════════╣")
        print(f"  ║  {Colors.Y}[1]{Colors.C}  Scan classique Bluetooth                        ║")
        print(f"  ║  {Colors.Y}[2]{Colors.C}  Scan Bluetooth Low Energy (BLE)                ║")
        print(f"  ║  {Colors.Y}[3]{Colors.C}  Scan continu                                   ║")
        print(f"  ║  {Colors.Y}[4]{Colors.C}  Mode surveillance (détection nouveaux)         ║")
        print(f"  ╠══════════════════════════════════════════════════════════════╣")
        print(f"  ║  {Colors.Y}[5]{Colors.C}  Infos appareil (nom, services, signal)         ║")
        print(f"  ║  {Colors.Y}[6]{Colors.C}  Liste appareils appairés                       ║")
        print(f"  ║  {Colors.Y}[7]{Colors.C}  Supprimer appareil appairé                     ║")
        print(f"  ║  {Colors.Y}[8]{Colors.C}  Bloquer appareil                               ║")
        print(f"  ╠══════════════════════════════════════════════════════════════╣")
        print(f"  ║  {Colors.Y}[9]{Colors.C}  Déconnecter appareil                           ║")
        print(f"  ║  {Colors.Y}[10]{Colors.C} L2Ping Flood (test de stress)                  ║")
        print(f"  ║  {Colors.Y}[11]{Colors.C} Scan SDP (services)                            ║")
        print(f"  ║  {Colors.Y}[12]{Colors.C} Scan RFCOMM                                    ║")
        print(f"  ╠══════════════════════════════════════════════════════════════╣")
        print(f"  ║  {Colors.Y}[13]{Colors.C} Spoofing MAC Bluetooth                         ║")
        print(f"  ║  {Colors.Y}[14]{Colors.C} Capture HCI (hcidump)                          ║")
        print(f"  ║  {Colors.Y}[15]{Colors.C} Changer interface                              ║")
        print(f"  ║  {Colors.Y}[16]{Colors.C} Redémarrer Bluetooth                           ║")
        print(f"  ╠══════════════════════════════════════════════════════════════╣")
        print(f"  ║  {Colors.Y}[17]{Colors.C} Toggle Alertes sonores: {Colors.G if self.alert_mode else Colors.R}{'ON' if self.alert_mode else 'OFF'}{Colors.C}                ║")
        print(f"  ║  {Colors.Y}[18]{Colors.C} Toggle Déconnexion auto: {Colors.G if self.auto_disconnect else Colors.R}{'ON' if self.auto_disconnect else 'OFF'}{Colors.C}              ║")
        print(f"  ║  {Colors.Y}[19]{Colors.C} Voir journal                                   ║")
        print(f"  ║  {Colors.Y}[20]{Colors.C} Exporter JSON                                  ║")
        print(f"  ╠══════════════════════════════════════════════════════════════╣")
        print(f"  ║  {Colors.R}[0]{Colors.C}  Quitter                                       ║")
        print(f"  ╚══════════════════════════════════════════════════════════════╝{Colors.RST}")
        
        choice = input(f"\n{Colors.C}{Colors.BD}[?] Choix: {Colors.RST}").strip()
        return choice
    
    def run(self):
        while True:
            choice = self.show_menu()
            
            if choice == '1':
                self.scan_devices()
            elif choice == '2':
                self.scan_le_devices()
            elif choice == '3':
                self.continuous_scan()
            elif choice == '4':
                self.monitor_mode()
            elif choice == '5':
                mac = input(f"{Colors.C}[?] MAC: {Colors.RST}").strip()
                if mac:
                    self.get_device_info(mac)
            elif choice == '6':
                self.list_paired()
            elif choice == '7':
                mac = input(f"{Colors.C}[?] MAC à supprimer: {Colors.RST}").strip()
                if mac:
                    self.remove_device(mac)
            elif choice == '8':
                mac = input(f"{Colors.C}[?] MAC à bloquer: {Colors.RST}").strip()
                if mac:
                    self.block_device(mac)
            elif choice == '9':
                mac = input(f"{Colors.C}[?] MAC à déconnecter: {Colors.RST}").strip()
                if mac:
                    self.disconnect_device(mac)
            elif choice == '10':
                mac = input(f"{Colors.C}[?] MAC cible: {Colors.RST}").strip()
                if mac:
                    self.l2ping_flood(mac)
            elif choice == '11':
                mac = input(f"{Colors.C}[?] MAC: {Colors.RST}").strip()
                if mac:
                    self.sdp_scan(mac)
            elif choice == '12':
                self.rfcomm_scan()
            elif choice == '13':
                self.spoof_mac()
            elif choice == '14':
                self.hci_dump()
            elif choice == '15':
                self.change_interface()
            elif choice == '16':
                self.reset_bluetooth()
            elif choice == '17':
                self.toggle_alert()
            elif choice == '18':
                self.toggle_auto_disconnect()
            elif choice == '19':
                self.show_log()
            elif choice == '20':
                self.export_json()
            elif choice == '0':
                print(f"\n{Colors.G}[+] Au revoir!{Colors.RST}")
                break
            
            input(f"\n{Colors.D}[Appuyez sur Entrée...]{Colors.RST}")

if __name__ == '__main__':
    hunter = BTHunter()
    hunter.run()
