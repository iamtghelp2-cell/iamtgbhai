# Copyright (c) 2025 devgagan : https://github.com/devgaganin.
# Licensed under the GNU General Public License v3.0.
# See LICENSE file in the repository root for full license text.

import os
from dotenv import load_dotenv
load_dotenv()

# ════════════════════════════════════════════════════════════════════════════════
# ░ CONFIGURATION SETTINGS
# ════════════════════════════════════════════════════════════════════════════════

# VPS --- FILL COOKIES 🍪 in """ ... """ 
INST_COOKIES = """
# write up here insta cookies
"""

YTUB_COOKIES = """
# write here yt cookies
"""

# ─── BOT / DATABASE CONFIG ──────────────────────────────────────────────────────
API_ID       = os.getenv("API_ID", "")
API_HASH     = os.getenv("API_HASH", "")
BOT_TOKEN    = os.getenv("BOT_TOKEN", "")
MONGO_DB     = os.getenv("MONGO_DB", "")
DB_NAME      = os.getenv("DB_NAME", "telegram_downloader")

# ─── OWNER / CONTROL SETTINGS ───────────────────────────────────────────────────
OWNER_ID     = list(map(int, os.getenv("OWNER_ID", "7951185227").split()))  # space-separated list
STRING       = os.getenv("STRING", None)  # optional session string
LOG_GROUP    = int(os.getenv("LOG_GROUP", "-1003506524877"))
FORCE_SUB    = int(os.getenv("FORCE_SUB", "-1004496131354"))

# ─── SECURITY KEYS ──────────────────────────────────────────────────────────────
# No defaults on purpose: the old public default keys made session encryption useless.
MASTER_KEY   = os.getenv("MASTER_KEY", "")  # 32 chars, session encryption
IV_KEY       = os.getenv("IV_KEY", "")      # 12 chars
if len(MASTER_KEY) != 32 or len(IV_KEY) != 12:
    raise RuntimeError("Set MASTER_KEY (32 chars) and IV_KEY (12 chars) in .env - see .env.example")

# ─── COOKIES HANDLING ───────────────────────────────────────────────────────────
YT_COOKIES   = os.getenv("YT_COOKIES", YTUB_COOKIES)
INSTA_COOKIES = os.getenv("INSTA_COOKIES", INST_COOKIES)

# ─── USAGE LIMITS ───────────────────────────────────────────────────────────────
FREEMIUM_LIMIT = int(os.getenv("FREEMIUM_LIMIT", "0"))
PREMIUM_LIMIT  = int(os.getenv("PREMIUM_LIMIT", "500"))

# ─── UI / LINKS ─────────────────────────────────────────────────────────────────
JOIN_LINK     = os.getenv("JOIN_LINK", "https://t.me/iamtghelp")
ADMIN_CONTACT = os.getenv("ADMIN_CONTACT", "https://t.me/Ownernrcbot")

# ════════════════════════════════════════════════════════════════════════════════
# ░ PREMIUM PLANS CONFIGURATION
# ════════════════════════════════════════════════════════════════════════════════

P0 = {
    "d": {
        "s": int(os.getenv("PLAN_D_S", 1)),
        "du": int(os.getenv("PLAN_D_DU", 1)),
        "u": os.getenv("PLAN_D_U", "days"),
        "l": os.getenv("PLAN_D_L", "Daily"),
    },
    "w": {
        "s": int(os.getenv("PLAN_W_S", 3)),
        "du": int(os.getenv("PLAN_W_DU", 1)),
        "u": os.getenv("PLAN_W_U", "weeks"),
        "l": os.getenv("PLAN_W_L", "Weekly"),
    },
    "m": {
        "s": int(os.getenv("PLAN_M_S", 5)),
        "du": int(os.getenv("PLAN_M_DU", 1)),
        "u": os.getenv("PLAN_M_U", "month"),
        "l": os.getenv("PLAN_M_L", "Monthly"),
    },
}

# ════════════════════════════════════════════════════════════════════════════════

# ════════════════════════════════════════════════════════════════════════════════
# ░ WATERMARK + TOPIC ROUTING (added)
# ════════════════════════════════════════════════════════════════════════════════
BRAND            = os.getenv("BRAND", "iamtghelp")
WATERMARK_TEXT   = os.getenv("WATERMARK_TEXT", "@iamtghelp")
WATERMARK_VIDEO  = os.getenv("WATERMARK_VIDEO", "true").lower() == "true"   # default for every user
WATERMARK_PDF    = os.getenv("WATERMARK_PDF", "true").lower() == "true"
ROUTE_CHAT       = int(os.getenv("ROUTE_CHAT", "0"))   # topics supergroup id (-100...), 0 = off
