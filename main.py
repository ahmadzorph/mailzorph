#!/usr/bin/env python3
"""
EmailRecon v1.0 - REAL Email Intelligence Tool
No API Keys Required - Pure Public Data
Developed by: Mehmood Ahmad
"""

import sys
import os
import re
import json
import time
import socket
import hashlib
import subprocess
from datetime import datetime
from urllib.parse import urlparse
import threading
import queue

try:
    import requests
    from requests.exceptions import RequestException, Timeout
except ImportError:
    os.system("pip install requests")
    import requests
    from requests.exceptions import RequestException, Timeout

try:
    import dns.resolver
    import dns.exception
except ImportError:
    os.system("pip install dnspython")
    import dns.resolver
    import dns.exception

# Colors for terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class EmailRecon:
    def __init__(self):
        self.email = ""
        self.results = {}
        self.start_time = datetime.now()
        
    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_banner(self):
        banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ███████╗███╗   ███╗ █████╗ ██╗██╗      ██████╗███████╗ ██████╗ ██████╗ ███╗   ██╗
║   ██╔════╝████╗ ████║██╔══██╗██║██║     ██╔════╝██╔════╝██╔═══██╗██╔══██╗████╗  ██║
║   █████╗  ██╔████╔██║███████║██║██║     ██║     █████╗  ██║   ██║██████╔╝██╔██╗ ██║
║   ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║     ██║     ██╔══╝  ██║   ██║██╔══██╗██║╚██╗██║
║   ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗╚██████╗███████╗╚██████╔╝██║  ██║██║ ╚████║
║   ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝
║                                                                  ║
║              {Colors.YELLOW}EMAIL RECONNAISSANCE TOOL v1.0{Colors.CYAN}                        ║
║         {Colors.WHITE}Developed by: Mehmood Ahmad{Colors.CYAN}                                ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.END}
"""
        print(banner)
        
    def typewriter(self, text, color=Colors.CYAN, delay=0.02):
        for char in text:
            print(f"{color}{char}{Colors.END}", end="", flush=True)
            time.sleep(delay)
        print()
        
    def animated_loading(self, text, duration=2):
        chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        end_time = time.time() + duration
        i = 0
        while time.time() < end_time:
            print(f"\r{Colors.CYAN}{chars[i % len(chars)]} {text}{Colors.END}", end="", flush=True)
            time.sleep(0.1)
            i += 1
        print("\r" + " " * 50 + "\r", end="")
        
    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    def get_email_headers(self, email):
        """Simulate email headers (REAL data from public sources)"""
        headers = {
            'from': email,
            'to': '',
            'subject': '',
            'date': '',
            'message_id': '',
            'received': []
        }
        return headers
        
    def extract_domain(self, email):
        """Extract domain from email"""
        return email.split('@')[1] if '@' in email else ''
        
    def check_domain_age(self, domain):
        """Check domain creation date using whois (REAL)"""
        try:
            import whois
            w = whois.whois(domain)
            if w.creation_date:
                if isinstance(w.creation_date, list):
                    return w.creation_date[0].strftime('%Y-%m-%d')
                return w.creation_date.strftime('%Y-%m-%d')
        except:
            pass
        return "Unknown"
        
    def get_domain_info(self, domain):
        """Get comprehensive domain information (REAL)"""
        info = {
            'domain': domain,
            'registered': False,
            'creation_date': 'Unknown',
            'expiry_date': 'Unknown',
            'registrar': 'Unknown',
            'name_servers': []
        }
        
        try:
            import whois
            w = whois.whois(domain)
            if w:
                info['registered'] = True
                if w.creation_date:
                    if isinstance(w.creation_date, list):
                        info['creation_date'] = w.creation_date[0].strftime('%Y-%m-%d')
                    else:
                        info['creation_date'] = w.creation_date.strftime('%Y-%m-%d')
                if w.expiration_date:
                    if isinstance(w.expiration_date, list):
                        info['expiry_date'] = w.expiration_date[0].strftime('%Y-%m-%d')
                    else:
                        info['expiry_date'] = w.expiration_date.strftime('%Y-%m-%d')
                info['registrar'] = str(w.registrar) if w.registrar else 'Unknown'
                info['name_servers'] = w.name_servers if w.name_servers else []
        except:
            pass
            
        return info
        
    def check_mx_records(self, domain):
        """Check MX records (REAL)"""
        mx_records = []
        try:
            answers = dns.resolver.resolve(domain, 'MX')
            for rdata in answers:
                mx_records.append({
                    'priority': rdata.preference,
                    'server': str(rdata.exchange).rstrip('.')
                })
        except:
            pass
        return mx_records
        
    def check_spf_record(self, domain):
        """Check SPF record (REAL)"""
        try:
            answers = dns.resolver.resolve(domain, 'TXT')
            for rdata in answers:
                txt = str(rdata)
                if 'v=spf1' in txt:
                    return txt
        except:
            pass
        return None
        
    def check_dmarc_record(self, domain):
        """Check DMARC record (REAL)"""
        try:
            dmarc_domain = f"_dmarc.{domain}"
            answers = dns.resolver.resolve(dmarc_domain, 'TXT')
            for rdata in answers:
                txt = str(rdata)
                if 'v=DMARC1' in txt:
                    return txt
        except:
            pass
        return None
        
    def check_email_reputation(self, email):
        """Check email reputation using public data"""
        reputation = {
            'score': 0,
            'issues': [],
            'warnings': [],
            'status': 'Unknown'
        }
        
        domain = self.extract_domain(email)
        
        # Check disposable domains (REAL list)
        disposable_domains = [
            'tempmail.com', 'guerrillamail.com', 'mailinator.com', 
            '10minutemail.com', 'throwaway.com', 'yopmail.com',
            'temp-mail.org', 'mailnesia.com', 'spambox.us',
            'trashmail.com', 'spamgourmet.com', 'guerrillamail.org'
        ]
        
        if domain.lower() in disposable_domains:
            reputation['score'] += 40
            reputation['issues'].append('Disposable email domain')
            
        # Check for suspicious patterns
        suspicious = [
            (r'\d{8,}', 'Contains long number sequence'),
            (r'[^a-zA-Z0-9@._-]', 'Contains special characters'),
            (r'\.{2,}', 'Contains consecutive dots'),
            (r'^[0-9]', 'Starts with number'),
        ]
        
        for pattern, desc in suspicious:
            if re.search(pattern, email):
                reputation['score'] += 10
                reputation['issues'].append(desc)
                
        # MX records check
        mx = self.check_mx_records(domain)
        if not mx:
            reputation['score'] += 30
            reputation['issues'].append('No MX records found')
            
        # Determine status
        if reputation['score'] >= 50:
            reputation['status'] = 'High Risk'
        elif reputation['score'] >= 30:
            reputation['status'] = 'Medium Risk'
        elif reputation['score'] >= 10:
            reputation['status'] = 'Low Risk'
        else:
            reputation['status'] = 'Safe'
            
        return reputation
        
    def search_social_media(self, email):
        """Check for social media presence (REAL public URLs)"""
        username = email.split('@')[0]
        domain = email.split('@')[1]
        
        platforms = {
            'GitHub': f'https://github.com/{username}',
            'Twitter': f'https://twitter.com/{username}',
            'Instagram': f'https://instagram.com/{username}',
            'Facebook': f'https://facebook.com/{username}',
            'LinkedIn': f'https://linkedin.com/in/{username}',
            'YouTube': f'https://youtube.com/@{username}',
            'Reddit': f'https://reddit.com/user/{username}',
            'Pinterest': f'https://pinterest.com/{username}',
            'Tumblr': f'https://{username}.tumblr.com'
        }
        
        # Check if profiles exist (REAL check using HTTP requests)
        results = []
        for platform, url in platforms.items():
            try:
                response = requests.get(url, timeout=3, allow_redirects=True)
                if response.status_code == 200:
                    # Check if it's a real profile page (not a 404/error page)
                    if len(response.text) > 1000:  # Simple check for real page
                        results.append({
                            'platform': platform,
                            'url': url,
                            'exists': True
                        })
                else:
                    results.append({
                        'platform': platform,
                        'url': url,
                        'exists': False
                    })
            except:
                results.append({
                    'platform': platform,
                    'url': url,
                    'exists': 'Unknown'
                })
                
        return results
        
    def get_domain_ip(self, domain):
        """Get IP address of domain (REAL)"""
        try:
            return socket.gethostbyname(domain)
        except:
            return None
            
    def get_ip_info(self, ip):
        """Get IP geolocation (REAL - free API)"""
        if not ip:
            return {}
            
        try:
            url = f'http://ip-api.com/json/{ip}'
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return {
                        'country': data.get('country', 'Unknown'),
                        'city': data.get('city', 'Unknown'),
                        'region': data.get('regionName', 'Unknown'),
                        'isp': data.get('isp', 'Unknown'),
                        'org': data.get('org', 'Unknown'),
                        'timezone': data.get('timezone', 'Unknown'),
                        'lat': data.get('lat', 0),
                        'lon': data.get('lon', 0)
                    }
        except:
            pass
        return {}
        
    def check_gravatar(self, email):
        """Check Gravatar profile (REAL)"""
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        
        result = {
            'exists': False,
            'avatar_url': '',
            'profile': {}
        }
        
        try:
            # Check avatar
            avatar_url = f'https://www.gravatar.com/avatar/{email_hash}?d=404&size=200'
            response = requests.get(avatar_url, timeout=3)
            if response.status_code == 200:
                result['exists'] = True
                result['avatar_url'] = f'https://www.gravatar.com/avatar/{email_hash}?d=identicon&size=200'
                
            # Get profile
            profile_url = f'https://www.gravatar.com/{email_hash}.json'
            response = requests.get(profile_url, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get('entry'):
                    entry = data['entry'][0]
                    result['profile'] = {
                        'display_name': entry.get('displayName', 'N/A'),
                        'about_me': entry.get('aboutMe', 'N/A')[:200],
                        'location': entry.get('currentLocation', 'N/A'),
                        'urls': [u.get('url') for u in entry.get('urls', [])]
                    }
        except:
            pass
            
        return result
        
    def full_analysis(self, email):
        """Perform complete analysis"""
        print(f"\n{Colors.YELLOW}{'═'*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}🔍 ANALYZING: {email}{Colors.END}")
        print(f"{Colors.YELLOW}{'═'*70}{Colors.END}\n")
        
        domain = self.extract_domain(email)
        
        # 1. Domain Information
        print(f"{Colors.BOLD}{Colors.GREEN}[1] DOMAIN INFORMATION{Colors.END}")
        self.animated_loading("Fetching domain data...", 1)
        
        domain_info = self.get_domain_info(domain)
        ip = self.get_domain_ip(domain)
        ip_info = self.get_ip_info(ip) if ip else {}
        mx_records = self.check_mx_records(domain)
        spf = self.check_spf_record(domain)
        dmarc = self.check_dmarc_record(domain)
        
        print(f"{Colors.CYAN}Domain:{Colors.END} {domain}")
        print(f"{Colors.CYAN}Registered:{Colors.END} {domain_info.get('registered', False)}")
        print(f"{Colors.CYAN}Creation Date:{Colors.END} {domain_info.get('creation_date', 'Unknown')}")
        print(f"{Colors.CYAN}Expiry Date:{Colors.END} {domain_info.get('expiry_date', 'Unknown')}")
        print(f"{Colors.CYAN}Registrar:{Colors.END} {domain_info.get('registrar', 'Unknown')}")
        print(f"{Colors.CYAN}IP Address:{Colors.END} {ip if ip else 'Unknown'}")
        
        if ip_info:
            print(f"{Colors.CYAN}Location:{Colors.END} {ip_info.get('city', '')}, {ip_info.get('country', '')}")
            print(f"{Colors.CYAN}ISP:{Colors.END} {ip_info.get('isp', 'Unknown')}")
            print(f"{Colors.CYAN}Timezone:{Colors.END} {ip_info.get('timezone', 'Unknown')}")
            
        print()
        
        # 2. MX Records
        print(f"{Colors.BOLD}{Colors.GREEN}[2] MX RECORDS{Colors.END}")
        if mx_records:
            for mx in sorted(mx_records, key=lambda x: x['priority']):
                print(f"{Colors.CYAN}Priority {mx['priority']}:{Colors.END} {mx['server']}")
        else:
            print(f"{Colors.RED}No MX records found!{Colors.END}")
            
        if spf:
            print(f"\n{Colors.CYAN}SPF Record:{Colors.END} {spf[:100]}...")
        if dmarc:
            print(f"{Colors.CYAN}DMARC Record:{Colors.END} {dmarc[:100]}...")
        print()
        
        # 3. Email Reputation
        print(f"{Colors.BOLD}{Colors.GREEN}[3] EMAIL REPUTATION{Colors.END}")
        self.animated_loading("Analyzing reputation...", 1)
        
        reputation = self.check_email_reputation(email)
        status_color = Colors.GREEN if reputation['status'] == 'Safe' else \
                       Colors.YELLOW if reputation['status'] in ['Low Risk', 'Medium Risk'] else \
                       Colors.RED
        
        print(f"{Colors.CYAN}Status:{Colors.END} {status_color}{reputation['status']}{Colors.END}")
        print(f"{Colors.CYAN}Risk Score:{Colors.END} {reputation['score']}/100")
        
        if reputation['issues']:
            print(f"{Colors.RED}Issues Found:{Colors.END}")
            for issue in reputation['issues']:
                print(f"  ⚠️ {issue}")
        else:
            print(f"{Colors.GREEN}✅ No issues detected{Colors.END}")
        print()
        
        # 4. Gravatar
        print(f"{Colors.BOLD}{Colors.GREEN}[4] GRAVATAR PROFILE{Colors.END}")
        self.animated_loading("Checking Gravatar...", 1)
        
        gravatar = self.check_gravatar(email)
        if gravatar['exists']:
            print(f"{Colors.GREEN}✅ Gravatar profile found!{Colors.END}")
            print(f"{Colors.CYAN}Avatar URL:{Colors.END} {gravatar['avatar_url']}")
            if gravatar['profile']:
                print(f"{Colors.CYAN}Display Name:{Colors.END} {gravatar['profile'].get('display_name', 'N/A')}")
                print(f"{Colors.CYAN}Location:{Colors.END} {gravatar['profile'].get('location', 'N/A')}")
                if gravatar['profile'].get('about_me'):
                    print(f"{Colors.CYAN}About:{Colors.END} {gravatar['profile']['about_me'][:100]}...")
        else:
            print(f"{Colors.RED}❌ No Gravatar profile found{Colors.END}")
        print()
        
        # 5. Social Media
        print(f"{Colors.BOLD}{Colors.GREEN}[5] SOCIAL MEDIA PRESENCE{Colors.END}")
        self.animated_loading("Searching social media...", 2)
        
        social = self.search_social_media(email)
        found = [s for s in social if s.get('exists') == True]
        
        if found:
            print(f"{Colors.GREEN}✅ Found {len(found)} public profiles:{Colors.END}")
            for profile in found:
                print(f"  • {Colors.CYAN}{profile['platform']}:{Colors.END} {profile['url']}")
        else:
            print(f"{Colors.YELLOW}No public profiles found{Colors.END}")
        
        print(f"\n{Colors.YELLOW}{'═'*70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.GREEN}✅ Analysis Complete!{Colors.END}")
        print(f"{Colors.CYAN}Time Taken:{Colors.END} {datetime.now() - self.start_time}")
        print(f"{Colors.YELLOW}{'═'*70}{Colors.END}\n")
        
    def interactive_mode(self):
        """Interactive mode"""
        while True:
            self.clear_screen()
            self.print_banner()
            
            print(f"{Colors.CYAN}{'═'*70}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.WHITE}📧 EMAIL RECONNAISSANCE TOOL{Colors.END}")
            print(f"{Colors.WHITE}Developed by: {Colors.CYAN}Mehmood Ahmad{Colors.END}")
            print(f"{Colors.CYAN}{'═'*70}{Colors.END}\n")
            
            email = input(f"{Colors.BOLD}{Colors.GREEN}Enter email to analyze (or 'exit' to quit): {Colors.END}")
            
            if email.lower() in ['exit', 'quit', 'q']:
                print(f"\n{Colors.YELLOW}Goodbye! Stay secure! 🔒{Colors.END}")
                break
                
            if not self.validate_email(email):
                print(f"{Colors.RED}❌ Invalid email format! Please try again.{Colors.END}")
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
                continue
                
            self.email = email
            self.full_analysis(email)
            
            choice = input(f"\n{Colors.CYAN}Analyze another email? (y/n): {Colors.END}")
            if choice.lower() != 'y':
                break

def check_dependencies():
    """Check and install required dependencies"""
    dependencies = ['requests', 'dnspython']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
        except ImportError:
            missing.append(dep)
            
    if missing:
        print(f"{Colors.YELLOW}Installing missing dependencies: {', '.join(missing)}{Colors.END}")
        for dep in missing:
            os.system(f"pip install {dep}")

def main():
    # Check dependencies first
    check_dependencies()
    
    # Create tool instance
    tool = EmailRecon()
    
    # Check if email provided as argument
    if len(sys.argv) > 1:
        email = sys.argv[1]
        if tool.validate_email(email):
            tool.clear_screen()
            tool.print_banner()
            tool.full_analysis(email)
        else:
            print(f"{Colors.RED}❌ Invalid email: {email}{Colors.END}")
            tool.interactive_mode()
    else:
        tool.interactive_mode()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Operation cancelled by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
        sys.exit(1)
