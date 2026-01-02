# app/common/session_manager.py
"""
مدیریت Session و Cookie برای کانکتورها
"""
import json
import os
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from app.common.log import console


class SessionManager:
    """
    مدیریت ذخیره و بازیابی session/cookie برای جلوگیری از login مکرر
    """
    
    def __init__(self, session_dir: str = ".sessions"):
        """
        Args:
            session_dir: مسیر پوشه ذخیره sessions
        """
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        
        # اضافه کردن .gitignore
        gitignore_path = self.session_dir / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text("*\n!.gitignore\n")
    
    def _get_session_path(self, vendor_name: str) -> Path:
        """دریافت مسیر فایل session"""
        return self.session_dir / f"{vendor_name}.json"
    
    def save_session(self, vendor_name: str, cookies: List[Dict], 
                     storage_state: Optional[Dict] = None) -> bool:
        """
        ذخیره session (cookies + storage state)
        
        Args:
            vendor_name: نام فروشگاه
            cookies: لیست cookies از browser
            storage_state: storage state از Playwright
            
        Returns:
            bool: موفقیت ذخیره
        """
        try:
            session_data = {
                "vendor": vendor_name,
                "cookies": cookies,
                "storage_state": storage_state,
                "saved_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
            }
            
            session_path = self._get_session_path(vendor_name)
            with open(session_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            console.print(f"[green]✓ Session saved for {vendor_name}[/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]✗ Failed to save session for {vendor_name}: {e}[/red]")
            return False
    
    def load_session(self, vendor_name: str) -> Optional[Dict]:
        """
        بارگذاری session
        
        Args:
            vendor_name: نام فروشگاه
            
        Returns:
            Dict یا None: داده session یا None اگر وجود نداشت
        """
        try:
            session_path = self._get_session_path(vendor_name)
            
            if not session_path.exists():
                console.print(f"[yellow]No saved session for {vendor_name}[/yellow]")
                return None
            
            with open(session_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # بررسی انقضا
            expires_at = datetime.fromisoformat(session_data['expires_at'])
            if datetime.now() > expires_at:
                console.print(f"[yellow]Session expired for {vendor_name}[/yellow]")
                self.delete_session(vendor_name)
                return None
            
            console.print(f"[green]✓ Session loaded for {vendor_name}[/green]")
            return session_data
            
        except Exception as e:
            console.print(f"[red]✗ Failed to load session for {vendor_name}: {e}[/red]")
            return None
    
    def delete_session(self, vendor_name: str) -> bool:
        """
        حذف session
        
        Args:
            vendor_name: نام فروشگاه
            
        Returns:
            bool: موفقیت حذف
        """
        try:
            session_path = self._get_session_path(vendor_name)
            if session_path.exists():
                session_path.unlink()
                console.print(f"[yellow]Session deleted for {vendor_name}[/yellow]")
                return True
            return False
            
        except Exception as e:
            console.print(f"[red]✗ Failed to delete session: {e}[/red]")
            return False
    
    def session_exists(self, vendor_name: str) -> bool:
        """بررسی وجود session معتبر"""
        session_data = self.load_session(vendor_name)
        return session_data is not None
    
    def list_sessions(self) -> List[str]:
        """لیست تمام sessionهای ذخیره شده"""
        try:
            sessions = []
            for file in self.session_dir.glob("*.json"):
                vendor_name = file.stem
                if self.session_exists(vendor_name):
                    sessions.append(vendor_name)
            return sessions
        except Exception as e:
            console.print(f"[red]Error listing sessions: {e}[/red]")
            return []
    
    def clear_all_sessions(self) -> int:
        """حذف تمام sessionها"""
        try:
            count = 0
            for file in self.session_dir.glob("*.json"):
                file.unlink()
                count += 1
            console.print(f"[yellow]Cleared {count} sessions[/yellow]")
            return count
        except Exception as e:
            console.print(f"[red]Error clearing sessions: {e}[/red]")
            return 0
