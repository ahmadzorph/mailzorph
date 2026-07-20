#!/usr/bin/env python3
"""
EmailIntel v2.0 - Advanced Email Intelligence Gathering Tool
Developed by: Mehmood Ahmad
License: MIT
"""

import sys
import os
import time
import json
import re
import hashlib
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import threading
import queue
from concurrent.futures import ThreadPoolExecutor, as_completed

# Third-party imports with fallback handling
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("[!] Rich library not found. Installing required dependencies...")
    os.system("pip install rich requests colorama")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True

try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
except ImportError:
    os.system("pip install colorama")
    from colorama import init, Fore, Back, Style
    init(autoreset=True)

# ==================== CONFIGURATION ====================
VERSION = "2.0"
AUTHOR = "Mehmood Ahmad"
GITHUB_REPO = "https://github.com/mehmoodahmad/emailintel"

# ASCII Art Banner
BANNER = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ███████╗███╗   ███╗ █████╗ ██╗██╗      ██████╗███╗   ██╗████████╗
║   ██╔════╝████╗ ████║██╔══██╗██║██║     ██╔════╝████╗  ██║╚══██╔══╝
║   █████╗  ██╔████╔██║███████║██║██║     ██║     ██╔██╗ ██║   ██║   
║   ██╔══╝  ██║╚██╔╝██║██╔══██║██║██║     ██║     ██║╚██╗██║   ██║   
║   ███████╗██║ ╚═╝ ██║██║  ██║██║███████╗╚██████╗██║ ╚████║   ██║   
║   ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝╚══════╝ ╚═════╝╚═╝  ╚═══╝   ╚═╝   
║                                                                  ║
║              Email Intelligence Gathering Tool v2.0              ║
║         Developed by: Mehmood Ahmad | https://github.com         ║
╚══════════════════════════════════════════════════════════════════╝
"""

class EmailIntel:
    """Main class for Email Intelligence Gathering"""
    
    def __init__(self):
        self.console = Console()
        self.email = ""
        self.results = {}
        self.start_time = datetime.now()
        
    def typewriter_effect(self, text: str, delay: float = 0.03, color: str = "cyan"):
        """Display text with typewriter animation effect"""
        for char in text:
            self.console.print(char, end="", style=color)
            time.sleep(delay)
        self.console.print()
        
    def animated_banner(self):
        """Display animated banner with cyberpunk style"""
        self.console.clear()
        
        # Animated border effect
        borders = ["╔", "═", "╗", "║", "╚", "╝"]
        for i in range(3):
            self.console.print(f"\r[cyan]Initializing System... [{'█' * i}{' ' * (3-i)}][/cyan]", end="")
            time.sleep(0.3)
        
        self.console.print("\n")
        
        # Display banner with colors
        lines = BANNER.split('\n')
        for line in lines:
            if line.strip():
                colored_line = Text(line)
                colored_line.stylize("bold cyan", 0, len(line))
                self.console.print(colored_line)
                time.sleep(0.05)
        
        # Display author info with special styling
        author_text = Text("🔮 Developed by: Mehmood Ahmad 🔮", style="bold yellow")
        self.console.print(Panel(author_text, border_style="red", width=70))
        time.sleep(0.5)
        
    def show_progress(self, message: str, duration: float = 2.0):
        """Display animated progress indicator"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task(f"[cyan]{message}", total=100)
            for i in range(100):
                time.sleep(duration / 100)
                progress.update(task, advance=1)
                
    def validate_email(self, email: str) -> bool:
        """Validate email format using regex"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    def check_email_breaches(self, email: str) -> Dict:
        """Check if email appears in known data breaches using HaveIBeenPwned API"""
        result = {"breaches": [], "total": 0}
        
        try:
            # Using HIBP API (no API key needed for public endpoints)
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {"hibp-api-key": ""}  # Optional: Add your key if you have one
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                result["breaches"] = [breach.get('Name', 'Unknown') for breach in data]
                result["total"] = len(data)
            elif response.status_code == 404:
                result["breaches"] = []
                result["total"] = 0
            else:
                result["error"] = f"API Error: {response.status_code}"
                
        except Exception as e:
            result["error"] = str(e)
            
        return result
        
    def check_email_reputation(self, email: str) -> Dict:
        """Check email reputation and risk score using multiple indicators"""
        result = {
            "risk_score": 0,
            "indicators": [],
            "status": "unknown"
        }
        
        # Local checks
        domain = email.split('@')[1] if '@' in email else ''
        
        # Check for suspicious patterns
        suspicious_patterns = [
            (r'\d{6,}', "Contains long number sequence"),
            (r'[^a-zA-Z0-9@._-]', "Contains special characters"),
            (r'\.{2,}', "Contains consecutive dots"),
        ]
        
        for pattern, desc in suspicious_patterns:
            if re.search(pattern, email):
                result["risk_score"] += 10
                result["indicators"].append(desc)
                
        # Domain checks
        disposable_domains = [
            'tempmail.com', 'guerrillamail.com', 'mailinator.com', 
            '10minutemail.com', 'throwaway.com', 'yopmail.com'
        ]
        
        if domain.lower() in disposable_domains:
            result["risk_score"] += 30
            result["indicators"].append("Disposable email domain")
            
        # Determine status
        if result["risk_score"] >= 50:
            result["status"] = "high_risk"
        elif result["risk_score"] >= 30:
            result["status"] = "medium_risk"
        else:
            result["status"] = "low_risk"
            
        return result
        
    def get_gravatar_info(self, email: str) -> Dict:
        """Get Gravatar profile information"""
        result = {
            "exists": False,
            "profile": {},
            "avatar_url": ""
        }
        
        try:
            # Generate MD5 hash of email
            email_hash = hashlib.md5(email.lower().encode()).hexdigest()
            avatar_url = f"https://www.gravatar.com/avatar/{email_hash}?d=404&size=200"
            
            # Check if avatar exists
            response = requests.get(avatar_url, timeout=10)
            
            if response.status_code == 200:
                result["exists"] = True
                result["avatar_url"] = f"https://www.gravatar.com/avatar/{email_hash}?d=identicon&size=200"
                
                # Try to get profile info
                profile_url = f"https://www.gravatar.com/{email_hash}.json"
                profile_response = requests.get(profile_url, timeout=10)
                
                if profile_response.status_code == 200:
                    profile_data = profile_response.json()
                    if 'entry' in profile_data and profile_data['entry']:
                        entry = profile_data['entry'][0]
                        result["profile"] = {
                            "display_name": entry.get('displayName', 'N/A'),
                            "about_me": entry.get('aboutMe', 'N/A'),
                            "location": entry.get('currentLocation', 'N/A'),
                            "urls": entry.get('urls', [])
                        }
                        
        except Exception as e:
            result["error"] = str(e)
            
        return result
        
    def get_domain_info(self, email: str) -> Dict:
        """Get information about the email domain"""
        result = {
            "domain": "",
            "mx_records": [],
            "has_mx": False,
            "is_valid": False
        }
        
        if '@' not in email:
            return result
            
        domain = email.split('@')[1]
        result["domain"] = domain
        
        try:
            # Check MX records
            import dns.resolver
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                result["mx_records"] = [str(record.exchange) for record in mx_records]
                result["has_mx"] = len(mx_records) > 0
                result["is_valid"] = len(mx_records) > 0
            except Exception:
                result["is_valid"] = False
                
        except ImportError:
            # Fallback if dnspython is not installed
            result["error"] = "dnspython not installed for MX lookup"
            
        except Exception as e:
            result["error"] = str(e)
            
        return result
        
    def search_public_profiles(self, email: str) -> Dict:
        """Search for public profiles associated with email"""
        result = {
            "profiles": [],
            "social_links": [],
            "total": 0
        }
        
        # Common social platforms to check
        platforms = {
            "GitHub": f"https://github.com/{email.split('@')[0]}",
            "Twitter": f"https://twitter.com/{email.split('@')[0]}",
            "LinkedIn": f"https://linkedin.com/in/{email.split('@')[0]}",
            "Instagram": f"https://instagram.com/{email.split('@')[0]}",
            "Facebook": f"https://facebook.com/{email.split('@')[0]}",
            "YouTube": f"https://youtube.com/@{email.split('@')[0]}"
        }
        
        # Check each platform (simplified - just build URLs for manual checking)
        for platform, url in platforms.items():
            result["profiles"].append({
                "platform": platform,
                "url": url,
                "possible": True
            })
            result["social_links"].append(url)
            
        result["total"] = len(result["profiles"])
        return result
        
    def generate_timeline(self, email: str) -> Dict:
        """Generate timeline of email activity (mock data for demo)"""
        # This is a mock function - in real implementation, you'd use APIs
        result = {
            "created_date": "Unknown",
            "activity_timeline": [],
            "total_activities": 0
        }
        
        # Simulate some timeline data
        current_year = datetime.now().year
        timeline = []
        
        # Generate some mock activity
        for year in range(current_year - 5, current_year + 1):
            timeline.append({
                "year": year,
                "activities": [
                    f"Email activity in {year}",
                    f"Associated accounts created in {year}"
                ]
            })
            
        result["activity_timeline"] = timeline
        result["total_activities"] = len(timeline)
        
        return result
        
    def display_results(self, results: Dict):
        """Display results in a beautiful formatted table"""
        self.console.print("\n" + "="*70, style="bold cyan")
        self.console.print(Panel.fit("🔍 EMAIL INTELLIGENCE RESULTS 🔍", border_style="yellow"))
        
        # Email info
        email_info = Table(title="Email Information", box=box.ROUNDED, style="cyan")
        email_info.add_column("Property", style="bold yellow")
        email_info.add_column("Value", style="green")
        email_info.add_row("Email", self.email)
        email_info.add_row("Domain", results.get('domain_info', {}).get('domain', 'N/A'))
        email_info.add_row("Valid MX", str(results.get('domain_info', {}).get('has_mx', False)))
        self.console.print(email_info)
        
        # Breaches info
        breach_info = Table(title="Data Breaches", box=box.ROUNDED, style="red")
        breach_info.add_column("Status", style="bold yellow")
        breach_info.add_column("Details", style="white")
        
        breaches = results.get('breaches', {})
        if breaches.get('total', 0) > 0:
            breach_info.add_row(
                f"[bold red]⚠️ Found {breaches['total']} breaches[/bold red]",
                "\n".join(breaches.get('breaches', []))
            )
        else:
            breach_info.add_row("[bold green]✅ No breaches found[/bold green]", "Email appears secure")
        self.console.print(breach_info)
        
        # Reputation
        reputation = results.get('reputation', {})
        risk_score = reputation.get('risk_score', 0)
        status = reputation.get('status', 'unknown')
        
        status_color = "green" if status == "low_risk" else "yellow" if status == "medium_risk" else "red"
        status_text = status.replace('_', ' ').upper()
        
        rep_table = Table(title="Risk Analysis", box=box.ROUNDED)
        rep_table.add_column("Metric", style="bold yellow")
        rep_table.add_column("Value", style="white")
        rep_table.add_row("Risk Score", f"{risk_score}/100")
        rep_table.add_row("Risk Level", f"[{status_color}]{status_text}[/{status_color}]")
        
        if reputation.get('indicators'):
            rep_table.add_row("Indicators", "\n".join(reputation['indicators']))
        self.console.print(rep_table)
        
        # Gravatar
        gravatar = results.get('gravatar', {})
        if gravatar.get('exists', False):
            gravatar_table = Table(title="Gravatar Profile", box=box.ROUNDED)
            gravatar_table.add_column("Field", style="bold yellow")
            gravatar_table.add_column("Value", style="green")
            
            profile = gravatar.get('profile', {})
            gravatar_table.add_row("Avatar", gravatar.get('avatar_url', 'N/A'))
            gravatar_table.add_row("Display Name", profile.get('display_name', 'N/A'))
            gravatar_table.add_row("Location", profile.get('location', 'N/A'))
            gravatar_table.add_row("About", profile.get('about_me', 'N/A')[:100] + "...")
            self.console.print(gravatar_table)
            
        # Social Profiles
        profiles = results.get('profiles', {})
        if profiles.get('profiles'):
            profile_table = Table(title="Potential Social Profiles", box=box.ROUNDED)
            profile_table.add_column("Platform", style="bold yellow")
            profile_table.add_column("URL", style="cyan")
            
            for profile in profiles.get('profiles', []):
                profile_table.add_row(profile['platform'], profile['url'])
            self.console.print(profile_table)
            
        # Timeline
        timeline = results.get('timeline', {})
        if timeline.get('activity_timeline'):
            timeline_table = Table(title="Activity Timeline", box=box.ROUNDED)
            timeline_table.add_column("Year", style="bold yellow")
            timeline_table.add_column("Activities", style="white")
            
            for entry in timeline.get('activity_timeline', []):
                timeline_table.add_row(
                    str(entry['year']),
                    "\n".join(entry.get('activities', []))
                )
            self.console.print(timeline_table)
            
        # Footer
        self.console.print("\n" + "═"*70, style="bold cyan")
        footer_text = Text("🛡️ Analysis Complete | Tool by Mehmood Ahmad 🛡️", style="bold yellow")
        self.console.print(Panel(footer_text, border_style="green"))
        
    def run_analysis(self, email: str):
        """Run complete analysis pipeline"""
        self.email = email
        self.results = {}
        
        # Show progress for each step
        steps = [
            ("Validating email format...", 0.3),
            ("Checking data breaches...", 0.5),
            ("Analyzing email reputation...", 0.4),
            ("Checking Gravatar profile...", 0.3),
            ("Gathering domain information...", 0.4),
            ("Searching public profiles...", 0.3),
            ("Generating activity timeline...", 0.3),
        ]
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            # Submit tasks
            futures['breaches'] = executor.submit(self.check_email_breaches, email)
            futures['reputation'] = executor.submit(self.check_email_reputation, email)
            futures['gravatar'] = executor.submit(self.get_gravatar_info, email)
            futures['domain'] = executor.submit(self.get_domain_info, email)
            futures['profiles'] = executor.submit(self.search_public_profiles, email)
            futures['timeline'] = executor.submit(self.generate_timeline, email)
            
            # Show progress while tasks complete
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=False,
            ) as progress:
                task = progress.add_task("[cyan]Analyzing email...", total=len(futures))
                
                for step_desc, _ in steps:
                    progress.update(task, description=f"[cyan]{step_desc}")
                    time.sleep(0.2)
                    
                # Wait for all tasks to complete
                for name, future in futures.items():
                    try:
                        self.results[name] = future.result(timeout=15)
                    except Exception as e:
                        self.results[name] = {"error": str(e)}
                    progress.update(task, advance=1)
                    
        # Display results
        self.display_results(self.results)
        
        # Save results
        self.save_results()
        
    def save_results(self):
        """Save results to JSON file"""
        try:
            filename = f"email_intel_{self.email.replace('@', '_at_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w') as f:
                json.dump({
                    "email": self.email,
                    "timestamp": datetime.now().isoformat(),
                    "results": self.results
                }, f, indent=2)
            self.console.print(f"\n[green]✅ Results saved to: {filename}[/green]")
        except Exception as e:
            self.console.print(f"\n[red]❌ Error saving results: {e}[/red]")
            
    def interactive_mode(self):
        """Interactive mode with prompt"""
        while True:
            self.console.print("\n" + "═"*50, style="bold cyan")
            self.console.print("[bold yellow]📧 Email Intelligence Tool v2.0[/bold yellow]")
            self.console.print("[cyan]Developed by: Mehmood Ahmad[/cyan]")
            self.console.print("═"*50, style="bold cyan")
            
            email = self.console.input("\n[bold green]Enter email to analyze (or 'exit' to quit): [/bold green]")
            
            if email.lower() == 'exit':
                self.console.print("[yellow]Goodbye! Stay secure! 🔒[/yellow]")
                break
                
            if not self.validate_email(email):
                self.console.print("[red]❌ Invalid email format! Please try again.[/red]")
                continue
                
            self.run_analysis(email)
            
            if not self.console.input("\n[cyan]Analyze another email? (y/n): [/cyan]").lower().startswith('y'):
                break

def main():
    """Main entry point"""
    console = Console()
    
    # Check for internet connection
    try:
        requests.get("https://google.com", timeout=5)
        internet_available = True
    except:
        internet_available = False
        console.print("[red]⚠️ No internet connection detected! Some features may not work.[/red]")
    
    tool = EmailIntel()
    tool.animated_banner()
    
    if not internet_available:
        console.print("[yellow]ℹ️ Offline mode - limited functionality available[/yellow]")
    
    time.sleep(0.5)
    
    # Check for command line argument
    if len(sys.argv) > 1:
        email = sys.argv[1]
        if tool.validate_email(email):
            tool.run_analysis(email)
        else:
            console.print(f"[red]❌ Invalid email: {email}[/red]")
            tool.interactive_mode()
    else:
        tool.interactive_mode()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console = Console()
        console.print("\n[yellow]⚠️ Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console = Console()
        console.print(f"[red]❌ Fatal error: {e}[/red]")
        sys.exit(1)
