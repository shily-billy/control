"""Playwright connector utilities"""

import os
from dataclasses import dataclass
from playwright.async_api import async_playwright

@dataclass
class PWConfig:
    user_data_dir: str
    headless: bool = True
    slow_mo_ms: int = 0

async def launch_persistent(config: PWConfig):
    pw = await async_playwright().start()
    browser = await pw.chromium.launch_persistent_context(
        user_data_dir=config.user_data_dir,
        headless=config.headless,
        slow_mo=config.slow_mo_ms,
    )
    return pw, browser
