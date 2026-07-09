#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GlobalTV Terminal - Streaming TV mondial depuis le terminal
Développé par HiddenWorld Communauté Tchadienne
Version: 2.0
"""

import os, sys, json, time, threading, subprocess, re, urllib.request
from urllib.parse import urlparse

try:
    import curses
except ImportError:
    print("curses non disponible - mode fallback")
    curses = None

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    class DummyFore:
        def __getattr__(self, name): return ''
    Fore = DummyFore()
    Back = DummyFore()
    Style = DummyFore()

# ============ DONNÉES DES CHAÎNES ============
CHANNELS = {
    "NEWS": {
        "FR": [
            {"name": "France 24", "url": "https://www.youtube.com/@France24/live", "type": "youtube"},
            {"name": "BFM TV", "url": "https://www.youtube.com/@BFMTV/live", "type": "youtube"},
            {"name": "LCI", "url": "https://www.youtube.com/@LCI/live", "type": "youtube"},
            {"name": "FR Info", "url": "https://www.youtube.com/@franceinfo/live", "type": "youtube"},
            {"name": "Euronews FR", "url": "https://www.youtube.com/@euronewsfr/live", "type": "youtube"},
        ],
        "US": [
            {"name": "CNN", "url": "https://www.youtube.com/@CNN/live", "type": "youtube"},
            {"name": "BBC News", "url": "https://www.youtube.com/@BBCNews/live", "type": "youtube"},
            {"name": "Al Jazeera", "url": "https://www.youtube.com/@AlJazeeraEnglish/live", "type": "youtube"},
            {"name": "Sky News", "url": "https://www.youtube.com/@SkyNews/live", "type": "youtube"},
            {"name": "CBS News", "url": "https://www.youtube.com/@CBSNews/live", "type": "youtube"},
        ],
        "AR": [
            {"name": "Al Jazeera Arabic", "url": "https://www.youtube.com/@aljazeera/live", "type": "youtube"},
            {"name": "Sky News Arabia", "url": "https://www.youtube.com/@skynewsarabia/live", "type": "youtube"},
            {"name": "BBC Arabic", "url": "https://www.youtube.com/@BBCArabic/live", "type": "youtube"},
        ],
    },
    "SPORTS": {
        "FR": [
            {"name": "L'Equipe", "url": "https://www.youtube.com/@lequipe/live", "type": "youtube"},
            {"name": "RMC Sport", "url": "https://www.youtube.com/@RMCSport/live", "type": "youtube"},
        ],
        "INT": [
            {"name": "FIFA", "url": "https://www.youtube.com/@fifa/live", "type": "youtube"},
            {"name": "Olympics", "url": "https://www.youtube.com/@Olympics/live", "type": "youtube"},
        ],
    },
    "MUSIC": {
        "INT": [
            {"name": "MTV", "url": "https://www.youtube.com/@MTV/live", "type": "youtube"},
            {"name": "Vevo", "url": "https://www.youtube.com/@Vevo/live", "type": "youtube"},
            {"name": "Radio France", "url": "https://www.youtube.com/@RadioFrance/live", "type": "youtube"},
        ],
    },
    "MOVIES": {
        "INT": [
            {"name": "Cinéma", "url": "https://www.youtube.com/@Cinema/live", "type": "youtube"},
        ],
    },
    "RELIGION": {
        "FR": [
            {"name": "KTO", "url": "https://www.youtube.com/@KTO/live", "type": "youtube"},
        ],
        "INT": [
            {"name": "Vatican News", "url": "https://www.youtube.com/@vaticannews/live", "type": "youtube"},
        ],
    },
    "KIDS": {
        "FR": [
            {"name": "Gulli", "url": "https://www.youtube.com/@Gulli/live", "type": "youtube"},
        ],
        "INT": [
            {"name": "Cartoon Network", "url": "https://www.youtube.com/@CartoonNetwork/live", "type": "youtube"},
        ],
    },
}

# ============ CONFIGURATION ============
CONFIG_FILE = os.path.expanduser("~/.globaltv_config.json")
FAVORITES_FILE = os.path.expanduser("~/.globaltv_favorites.json")
HISTORY_FILE = os.path.expanduser("~/.globaltv_history.json")

class GlobalTV:
    def __init__(self):
        self.current_channel = None
        self.player_process = None
        self.favorites = self.load_json(FAVORITES_FILE, [])
        self.history = self.load_json(HISTORY_FILE, [])
        self.config = self.load_json(CONFIG_FILE, {"player": "mpv", "quality": "best", "volume": 80})
        self.running = True
        self.scan_results = []
        self.current_category = "NEWS"
        self.current_country = "FR"

    def load_json(self, path, default):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            return default

    def save_json(self, path, data):
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def clear(self):
        os.system('clear' if os.name != 'nt' else 'cls')

    def banner(self):
        self.clear()
        print(f"{Fore.CYAN}")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║     🌍 GLOBALTV TERMINAL - TV MONDIALE EN DIRECT 🌍         ║")
        print("║         Développé par HiddenWorld Communauté Tchadienne      ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print(f"{Fore.YELLOW}   📡 Accédez aux chaînes mondiales gratuitement depuis terminal")
        print(f"{Fore.GREEN}   ✓ YouTube Live ✓ Streams publics ✓ Radio ✓ Podcasts")
        print()

    def check_dependencies(self):
        deps = ["mpv", "yt-dlp", "ffmpeg"]
        missing = []
        for dep in deps:
            if subprocess.run(["which", dep], capture_output=True).returncode != 0:
                missing.append(dep)
        if missing:
            print(f"{Fore.RED}⚠️ Dépendances manquantes: {', '.join(missing)}")
            print(f"{Fore.YELLOW}Installation: sudo apt install {' '.join(missing)}")
            return False
        return True

    def get_stream_url(self, channel):
        """Extrait l'URL direct du stream depuis YouTube"""
        if channel.get("type") == "youtube":
            try:
                cmd = ["yt-dlp", "-g", "-f", "best[height<=720]", channel["url"]]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip().split('\n')[0]
            except Exception as e:
                print(f"{Fore.RED}Erreur extraction: {e}")
        return channel.get("direct_url") or channel["url"]

    def play_channel(self, channel):
        """Lance la lecture d'une chaîne"""
        self.stop_player()
        self.current_channel = channel
        self.add_to_history(channel)

        print(f"{Fore.CYAN}📺 Lancement: {channel['name']}...")
        stream_url = self.get_stream_url(channel)

        if not stream_url:
            print(f"{Fore.RED}❌ Impossible d'obtenir le stream")
            return False

        player = self.config.get("player", "mpv")
        cmd = [
            player,
            "--fs=no",
            "--really-quiet",
            f"--volume={self.config.get('volume', 80)}",
            "--ytdl-format=best[height<=720]",
            stream_url
        ]

        try:
            self.player_process = subprocess.Popen(cmd)
            print(f"{Fore.GREEN}✅ Lecture démarrée: {channel['name']}")
            print(f"{Fore.YELLOW}⏹️  Appuyez sur Entrée pour arrêter...")
            input()
            self.stop_player()
            return True
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lecture: {e}")
            return False

    def stop_player(self):
        """Arrête le lecteur en cours"""
        if self.player_process:
            self.player_process.terminate()
            try:
                self.player_process.wait(timeout=3)
            except:
                self.player_process.kill()
            self.player_process = None
            print(f"{Fore.YELLOW}⏹️ Lecture arrêtée")

    def add_to_history(self, channel):
        self.history.insert(0, {"channel": channel, "time": time.strftime("%Y-%m-%d %H:%M:%S")})
        self.history = self.history[:50]
        self.save_json(HISTORY_FILE, self.history)

    def add_favorite(self, channel):
        if channel not in self.favorites:
            self.favorites.append(channel)
            self.save_json(FAVORITES_FILE, self.favorites)
            print(f"{Fore.GREEN}⭐ Ajouté aux favoris: {channel['name']}")
        else:
            print(f"{Fore.YELLOW}Déjà dans les favoris")

    def remove_favorite(self, channel_name):
        self.favorites = [c for c in self.favorites if c["name"] != channel_name]
        self.save_json(FAVORITES_FILE, self.favorites)
        print(f"{Fore.GREEN}⭐ Retiré des favoris")

    def show_channels(self, category=None, country=None):
        """Affiche les chaînes disponibles"""
        self.banner()
        cat = category or self.current_category
        cnt = country or self.current_country

        print(f"{Fore.CYAN}📂 Catégorie: {cat} | 🌍 Pays: {cnt}")
        print(f"{Fore.YELLOW}" + "─" * 60)

        channels = CHANNELS.get(cat, {}).get(cnt, [])
        if not channels:
            print(f"{Fore.RED}Aucune chaîne dans cette catégorie/pays")
            return []

        for i, ch in enumerate(channels, 1):
            fav = "⭐" if ch in self.favorites else "  "
            print(f"{Fore.GREEN}{i:2d}. {fav} {ch['name']:<30} {Fore.CYAN}[{ch.get('type', 'stream').upper()}]")

        return channels

    def show_favorites(self):
        self.banner()
        print(f"{Fore.YELLOW}⭐ MES FAVORIS")
        print("─" * 60)
        if not self.favorites:
            print(f"{Fore.RED}Aucun favori")
            return []
        for i, ch in enumerate(self.favorites, 1):
            print(f"{Fore.GREEN}{i}. {ch['name']}")
        return self.favorites

    def show_history(self):
        self.banner()
        print(f"{Fore.YELLOW}📜 HISTORIQUE")
        print("─" * 60)
        if not self.history:
            print(f"{Fore.RED}Aucun historique")
            return
        for i, h in enumerate(self.history[:20], 1):
            ch = h["channel"]
            print(f"{Fore.CYAN}{i}. {ch['name']:<25} {Fore.YELLOW}{h['time']}")

    def search_channels(self, query):
        """Recherche dans toutes les chaînes"""
        results = []
        query_lower = query.lower()
        for cat, countries in CHANNELS.items():
            for cnt, channels in countries.items():
                for ch in channels:
                    if query_lower in ch["name"].lower():
                        results.append((cat, cnt, ch))
        return results

    def scan_streams(self):
        """Scan rapide des streams disponibles"""
        self.banner()
        print(f"{Fore.CYAN}🔍 Scan des streams disponibles...")
        available = []
        for cat, countries in CHANNELS.items():
            for cnt, channels in countries.items():
                for ch in channels:
                    print(f"{Fore.YELLOW}Test: {ch['name']}...", end=" ")
                    try:
                        url = self.get_stream_url(ch)
                        if url:
                            print(f"{Fore.GREEN}✅ OK")
                            available.append(ch)
                        else:
                            print(f"{Fore.RED}❌ Indisponible")
                    except:
                        print(f"{Fore.RED}❌ Erreur")
        self.scan_results = available
        print(f"\n{Fore.GREEN}✅ {len(available)} streams disponibles")
        return available

    def record_stream(self, channel, duration=60):
        """Enregistre un stream"""
        filename = f"record_{channel['name'].replace(' ', '_')}_{int(time.time())}.mp4"
        stream_url = self.get_stream_url(channel)
        if not stream_url:
            print(f"{Fore.RED}❌ Stream non disponible")
            return

        print(f"{Fore.CYAN}⏺️ Enregistrement: {filename} ({duration}s)")
        cmd = [
            "ffmpeg", "-i", stream_url,
            "-t", str(duration),
            "-c", "copy",
            "-y", filename
        ]
        try:
            subprocess.run(cmd, timeout=duration + 10)
            print(f"{Fore.GREEN}✅ Enregistré: {filename}")
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur: {e}")

    def show_menu(self):
        self.banner()
        print(f"{Fore.CYAN}╔══════════════════════════════════════════════════════════════╗")
        print(f"{Fore.CYAN}║                    📺 MENU PRINCIPAL                         ║")
        print(f"{Fore.CYAN}╠══════════════════════════════════════════════════════════════╣")
        print(f"{Fore.CYAN}║  {Fore.GREEN}1.{Fore.WHITE} 📰 NEWS              {Fore.GREEN}7.{Fore.WHITE} ⭐ FAVORIS              ║")
        print(f"{Fore.CYAN}║  {Fore.GREEN}2.{Fore.WHITE} ⚽ SPORTS            {Fore.GREEN}8.{Fore.WHITE} 📜 HISTORIQUE           ║")
        print(f"{Fore.CYAN}║  {Fore.GREEN}3.{Fore.WHITE} 🎵 MUSIQUE           {Fore.GREEN}9.{Fore.WHITE} 🔍 RECHERCHE           ║")
        print(f"{Fore.CYAN}║  {Fore.GREEN}4.{Fore.WHITE} 🎬 FILMS             {Fore.GREEN}10.{Fore.WHITE} 🔍 SCAN STREAMS        ║")
        print(f"{Fore.CYAN}║  {Fore.GREEN}5.{Fore.WHITE} 🙏 RELIGION          {Fore.GREEN}11.{Fore.WHITE} ⏺️ ENREGISTRER         ║")
        print(f"{Fore.CYAN}║  {Fore.GREEN}6.{Fore.WHITE} 👶 ENFANTS           {Fore.GREEN}12.{Fore.WHITE} ⚙️ CONFIGURATION       ║")
        print(f"{Fore.CYAN}╠══════════════════════════════════════════════════════════════╣")
        print(f"{Fore.CYAN}║  {Fore.YELLOW}Q.{Fore.WHITE} Quitter | {Fore.YELLOW}P.{Fore.WHITE} Arrêter lecture                        ║")
        print(f"{Fore.CYAN}╚══════════════════════════════════════════════════════════════╝")

    def config_menu(self):
        self.banner()
        print(f"{Fore.YELLOW}⚙️ CONFIGURATION")
        print("─" * 60)
        print(f"{Fore.CYAN}1. Lecteur: {self.config.get('player', 'mpv')}")
        print(f"{Fore.CYAN}2. Qualité: {self.config.get('quality', 'best')}")
        print(f"{Fore.CYAN}3. Volume: {self.config.get('volume', 80)}%")
        print(f"{Fore.CYAN}4. Retour")

        choice = input(f"\n{Fore.GREEN}Choix: ")
        if choice == "1":
            self.config["player"] = input("Lecteur (mpv/vlc/ffplay): ") or "mpv"
        elif choice == "2":
            self.config["quality"] = input("Qualité (best/720/480): ") or "best"
        elif choice == "3":
            self.config["volume"] = int(input("Volume (0-100): ") or 80)
        self.save_json(CONFIG_FILE, self.config)

    def run(self):
        if not self.check_dependencies():
            input("Appuyez sur Entrée...")

        while self.running:
            self.show_menu()
            choice = input(f"\n{Fore.GREEN}Votre choix: ").strip().upper()

            if choice == "Q":
                self.running = False
                self.stop_player()
                print(f"{Fore.CYAN}👋 Au revoir!")
            elif choice == "P":
                self.stop_player()
            elif choice in ["1", "2", "3", "4", "5", "6"]:
                cats = ["NEWS", "SPORTS", "MUSIC", "MOVIES", "RELIGION", "KIDS"]
                self.current_category = cats[int(choice) - 1]
                self.select_country_and_channel()
            elif choice == "7":
                self.select_from_list(self.show_favorites())
            elif choice == "8":
                self.show_history()
                input("\nAppuyez sur Entrée...")
            elif choice == "9":
                self.do_search()
            elif choice == "10":
                self.scan_streams()
                input("\nAppuyez sur Entrée...")
            elif choice == "11":
                self.do_record()
            elif choice == "12":
                self.config_menu()
            else:
                print(f"{Fore.RED}Choix invalide")
                time.sleep(1)

    def select_country_and_channel(self):
        countries = list(CHANNELS.get(self.current_category, {}).keys())
        if len(countries) == 1:
            self.select_channel(self.current_category, countries[0])
            return

        self.banner()
        print(f"{Fore.CYAN}🌍 Sélectionnez le pays:")
        for i, cnt in enumerate(countries, 1):
            print(f"{Fore.GREEN}{i}. {cnt}")
        print(f"{Fore.YELLOW}0. Retour")

        try:
            c = int(input(f"\n{Fore.GREEN}Pays: "))
            if c == 0:
                return
            if 1 <= c <= len(countries):
                self.select_channel(self.current_category, countries[c - 1])
        except ValueError:
            pass

    def select_channel(self, cat, cnt):
        channels = self.show_channels(cat, cnt)
        if not channels:
            input("\nAppuyez sur Entrée...")
            return

        print(f"\n{Fore.YELLOW}0. Retour | F. Ajouter aux favoris")
        try:
            c = input(f"{Fore.GREEN}Chaîne (numéro/F): ").strip().upper()
            if c == "0":
                return
            if c == "F":
                fav = input("Numéro à ajouter: ")
                if fav.isdigit() and 1 <= int(fav) <= len(channels):
                    self.add_favorite(channels[int(fav) - 1])
                input("Appuyez sur Entrée...")
                return
            if c.isdigit() and 1 <= int(c) <= len(channels):
                self.play_channel(channels[int(c) - 1])
        except ValueError:
            pass

    def select_from_list(self, channels):
        if not channels:
            input("Appuyez sur Entrée...")
            return
        for i, ch in enumerate(channels, 1):
            print(f"{Fore.GREEN}{i}. {ch['name']}")
        try:
            c = int(input(f"\n{Fore.GREEN}Chaîne: "))
            if 1 <= c <= len(channels):
                self.play_channel(channels[c - 1])
        except ValueError:
            pass

    def do_search(self):
        self.banner()
        query = input(f"{Fore.GREEN}Rechercher: ").strip()
        if not query:
            return
        results = self.search_channels(query)
        if not results:
            print(f"{Fore.RED}Aucun résultat")
            input("Appuyez sur Entrée...")
            return

        print(f"\n{Fore.GREEN}{len(results)} résultat(s):")
        for i, (cat, cnt, ch) in enumerate(results, 1):
            print(f"{Fore.CYAN}{i}. [{cat}/{cnt}] {ch['name']}")

        try:
            c = int(input(f"\n{Fore.GREEN}Choisir (0=retour): "))
            if c == 0:
                return
            if 1 <= c <= len(results):
                self.play_channel(results[c - 1][2])
        except ValueError:
            pass

    def do_record(self):
        self.banner()
        query = input(f"{Fore.GREEN}Nom de la chaîne à enregistrer: ").strip()
        results = self.search_channels(query)
        if not results:
            print(f"{Fore.RED}Chaîne non trouvée")
            input("Appuyez sur Entrée...")
            return

        for i, (cat, cnt, ch) in enumerate(results, 1):
            print(f"{Fore.CYAN}{i}. {ch['name']}")
        try:
            c = int(input(f"\n{Fore.GREEN}Choisir: "))
            if 1 <= c <= len(results):
                dur = int(input("Durée en secondes (60): ") or 60)
                self.record_stream(results[c - 1][2], dur)
        except ValueError:
            pass
        input("Appuyez sur Entrée...")


if __name__ == "__main__":
    try:
        app = GlobalTV()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️ Interrompu")
        sys.exit(0)
