# Commands for topic routing and watermark (added).
from pyrogram import filters
from shared_client import app
from config import WATERMARK_TEXT, WATERMARK_VIDEO, WATERMARK_PDF
from utils.func import get_user_data_key, save_user_data
from utils.router import get_cfg, set_map, norm

HELP = (
    "**Auto mirror (recommended)**\n"
    "Topic `History (वीर बैच)` of the source group -> topic with the SAME name in your group.\n"
    "`/route_chat -100...` (your group), then `/mirror on`. `/clone_topics <source group id or @username>` creates ALL source topics in your group at once. Missing topics are created automatically "
    "(`/autocreate off` to stop that). `/sync_topics` re-reads your existing topics.\n\n"
    "**Topic routing**\n"
    "`/route_chat -100xxxxxxxxxx` - topics supergroup\n"
    "`/map_topic keyword topic_id` - e.g. `/map_topic physics 12`\n"
    "`/unmap_topic keyword`\n"
    "`/map_source channel_id_or_username topic_id` - whole source channel/group -> one topic\n"
    "`/unmap_source channel_id_or_username`\n"
    "`/default_topic topic_id` (0 = off) - used when no keyword matches\n"
    "`/topics` - show settings, `/route_off` - disable\n"
    "Keyword is matched in file name + caption (any font style).\n\n"
    "**Watermark**\n"
    "`/wm` - show, `/wm text YOUR TEXT`, `/wm video on|off`, `/wm pdf on|off`"
)

@app.on_message(filters.command("topics") & filters.private)
async def topics_cmd(_, m):
    c = await get_cfg(m.from_user.id)
    srows = "\n".join(f"• `{k}` → {v}" for k, v in c["src"].items()) or "none"
    rows = "\n".join(f"• `{k}` → {v}" for k, v in c["map"].items()) or "none"
    await m.reply_text(f"**Route chat:** `{c['chat'] or 'off'}`\n**Default topic:** `{c['default'] or 'off'}`\n**Keywords:**\n{rows}\n**Sources:**\n{srows}\n\n{HELP}")

@app.on_message(filters.command("route_chat") & filters.private)
async def route_chat(_, m):
    try:
        await save_user_data(m.from_user.id, "route_chat", int(m.command[1]))
        await m.reply_text("✅ Route chat saved. Bot must be admin there (Manage Topics).")
    except Exception:
        await m.reply_text("Usage: /route_chat -100xxxxxxxxxx")

@app.on_message(filters.command("route_off") & filters.private)
async def route_off(_, m):
    await save_user_data(m.from_user.id, "route_chat", 0)
    await m.reply_text("✅ Topic routing off.")

@app.on_message(filters.command("map_topic") & filters.private)
async def map_topic(_, m):
    try:
        kw = norm(" ".join(m.command[1:-1])).strip(); tid = int(m.command[-1])
        assert kw
    except Exception:
        return await m.reply_text("Usage: /map_topic keyword topic_id")
    cur = (await get_cfg(m.from_user.id))["map"]; cur[kw] = tid
    await set_map(m.from_user.id, cur)
    await m.reply_text(f"✅ `{kw}` → topic {tid}")

@app.on_message(filters.command("unmap_topic") & filters.private)
async def unmap_topic(_, m):
    kw = norm(" ".join(m.command[1:])).strip()
    cur = (await get_cfg(m.from_user.id))["map"]
    if cur.pop(kw, None) is None:
        return await m.reply_text("Keyword not found.")
    await set_map(m.from_user.id, cur)
    await m.reply_text("✅ Removed.")

@app.on_message(filters.command("default_topic") & filters.private)
async def default_topic(_, m):
    try:
        await save_user_data(m.from_user.id, "route_default", int(m.command[1]))
        await m.reply_text("✅ Saved.")
    except Exception:
        await m.reply_text("Usage: /default_topic topic_id")

async def wm_settings(uid):
    return {
        "text": await get_user_data_key(uid, "wm_text", WATERMARK_TEXT),
        "video": await get_user_data_key(uid, "wm_video", WATERMARK_VIDEO),
        "pdf": await get_user_data_key(uid, "wm_pdf", WATERMARK_PDF),
    }

@app.on_message(filters.command("wm") & filters.private)
async def wm_cmd(_, m):
    uid = m.from_user.id; a = m.command[1:]
    if len(a) >= 2 and a[0] == "text":
        await save_user_data(uid, "wm_text", " ".join(a[1:]))
    elif len(a) == 2 and a[0] in ("video", "pdf") and a[1] in ("on", "off"):
        await save_user_data(uid, "wm_" + a[0], a[1] == "on")
    s = await wm_settings(uid)
    await m.reply_text(f"**Watermark**\nText: `{s['text']}`\nVideo: {'ON' if s['video'] else 'OFF'}\nPDF: {'ON' if s['pdf'] else 'OFF'}\n\n"
                       "`/wm text YOUR TEXT`\n`/wm video on|off`\n`/wm pdf on|off`\n_Video watermark re-encodes the video, so it is slower._")

def _src_key(x):
    x = x.strip().lower().lstrip("@")
    return x[4:] if x.startswith("-100") else x

@app.on_message(filters.command("map_source") & filters.private)
async def map_source(_, m):
    try:
        key = _src_key(m.command[1]); tid = int(m.command[2])
    except Exception:
        return await m.reply_text("Usage: /map_source -100123456789 12  (or channel_username 12)")
    cur = (await get_cfg(m.from_user.id))["src"]; cur[key] = tid
    await save_user_data(m.from_user.id, "route_src", cur)
    await m.reply_text(f"✅ source `{key}` → topic {tid}")

@app.on_message(filters.command("unmap_source") & filters.private)
async def unmap_source(_, m):
    cur = (await get_cfg(m.from_user.id))["src"]
    if len(m.command) < 2 or cur.pop(_src_key(m.command[1]), None) is None:
        return await m.reply_text("Source not found.")
    await save_user_data(m.from_user.id, "route_src", cur)
    await m.reply_text("✅ Removed.")

@app.on_message(filters.command("mirror") & filters.private)
async def mirror_cmd(_, m):
    if len(m.command) == 2 and m.command[1] in ("on", "off"):
        await save_user_data(m.from_user.id, "route_mirror", m.command[1] == "on")
    st = await get_user_data_key(m.from_user.id, "route_mirror", True)
    await m.reply_text(f"Mirror by topic name: {'ON' if st else 'OFF'}\nUsage: /mirror on|off")

@app.on_message(filters.command("autocreate") & filters.private)
async def autocreate_cmd(_, m):
    if len(m.command) == 2 and m.command[1] in ("on", "off"):
        await save_user_data(m.from_user.id, "route_autocreate", m.command[1] == "on")
    st = await get_user_data_key(m.from_user.id, "route_autocreate", True)
    await m.reply_text(f"Auto-create missing topics: {'ON' if st else 'OFF'}\nUsage: /autocreate on|off")

@app.on_message(filters.command("sync_topics") & filters.private)
async def sync_topics_cmd(_, m):
    from plugins.batch import get_uclient, get_ubot
    from utils.router import sync_dest_topics
    uid = m.from_user.id
    n = await sync_dest_topics(uid, [await get_uclient(uid), await get_ubot(uid), app])
    if n is None:
        return await m.reply_text("Could not read topics. Set /route_chat first and /login (your account must be in that group).")
    await m.reply_text(f"✅ {n} topics saved. New source topics will be created automatically if /autocreate is on.")

@app.on_message(filters.command("clone_topics") & filters.private)
async def clone_topics_cmd(_, m):
    from plugins.batch import get_uclient, get_ubot
    from utils.router import clone_topics
    if len(m.command) < 2:
        return await m.reply_text("Usage: /clone_topics -100123456789  (source forum group id or @username)\nSet /route_chat first.")
    uid = m.from_user.id
    note = await m.reply_text("Reading source topics and creating them...")
    r = await clone_topics(uid, [await get_uclient(uid), await get_ubot(uid), app], m.command[1])
    if r is None:
        return await note.edit_text("Failed. Check: /route_chat set, you are /login-ed, your account is in the source group, bot is admin (Manage Topics) in your group.")
    await note.edit_text(f"✅ Created {r[0]} new topics, {r[1]} already existed.")
