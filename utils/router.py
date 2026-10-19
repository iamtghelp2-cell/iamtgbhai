# Topic routing (added): keyword in filename/caption -> topic of a supergroup.
import unicodedata
from config import ROUTE_CHAT
from utils.func import get_user_data_key, save_user_data

def norm(t):
    # NFKC folds fancy unicode fonts (𝗕𝗼𝗹𝗱, ｆｕｌｌｗｉｄｔｈ ...) to plain letters
    return unicodedata.normalize("NFKC", t or "").casefold()

async def get_cfg(uid):
    return {
        "chat": await get_user_data_key(uid, "route_chat", ROUTE_CHAT) or 0,
        "map": await get_user_data_key(uid, "route_map", {}) or {},
        "default": await get_user_data_key(uid, "route_default", 0) or 0,
        "src": await get_user_data_key(uid, "route_src", {}) or {},
    }

async def resolve(uid, *texts, src=None):
    """Return (chat_id, topic_id) or None. Longest matching keyword wins."""
    cfg = await get_cfg(uid)
    if not cfg["chat"]:
        return None
    hay = norm(" ".join(t for t in texts if t))
    best = None
    for kw, topic in cfg["map"].items():
        if kw in hay and (best is None or len(kw) > len(best[0])):
            best = (kw, topic)
    if best:
        return int(cfg["chat"]), int(best[1])
    if src is not None:
        key = str(src).lower().lstrip("@")
        key100 = key[4:] if key.startswith("-100") else key
        for k, topic in cfg["src"].items():
            if k in (key, key100):
                return int(cfg["chat"]), int(topic)
    if cfg["default"]:
        return int(cfg["chat"]), int(cfg["default"])
    return None

async def set_map(uid, m):
    await save_user_data(uid, "route_map", m)

# ───────────────────────── mirror mode: same topic NAME in your group ─────────────────────────
import asyncio
from pyrogram import raw

_src_titles = {}          # (source chat, topic id) -> title
_mirror_lock = asyncio.Lock()

def tkey(title):
    """Compare topic names ignoring case, spaces, emoji, punctuation and fancy fonts."""
    t = unicodedata.normalize("NFKC", title or "").casefold()
    return "".join(ch for ch in t if unicodedata.category(ch)[0] in "LMN")

def _cid(x):
    s = str(x)
    return int(s) if s.lstrip("-").isdigit() else s

async def get_source_title(clients, src, tid):
    k = (str(src), tid)
    if k in _src_titles:
        return _src_titles[k]
    for cl in clients:
        if cl is None:
            continue
        try:
            t = await cl.get_forum_topics_by_id(_cid(src), tid)
            if t and getattr(t, "title", None):
                _src_titles[k] = t.title
                return t.title
        except Exception as e:
            print(f"topic title fetch failed: {e}")
    return None

async def _create_topic(clients, chat, title):
    for cl in clients:
        if cl is None:
            continue
        try:
            r = await cl.invoke(raw.functions.channels.CreateForumTopic(
                channel=await cl.resolve_peer(chat), title=title[:128], random_id=cl.rnd_id()))
            for upd in r.updates:
                if isinstance(upd, raw.types.UpdateNewChannelMessage):
                    return upd.message.id
        except Exception as e:
            print(f"create topic failed: {e}")
    return None

async def sync_dest_topics(uid, clients):
    """Read all topics of your destination group and remember name -> id. Returns count or None."""
    chat = (await get_cfg(uid))["chat"]
    if not chat:
        return None
    for cl in clients:
        if cl is None:
            continue
        try:
            mp = {}
            async for t in cl.get_forum_topics(int(chat)):
                if t.id != 1:
                    mp[tkey(t.title)] = t.id
            await save_user_data(uid, "route_mirror_map", mp)
            return len(mp)
        except Exception as e:
            print(f"sync topics failed: {e}")
    return None

async def mirror_resolve(uid, u, c, src, m):
    """Message from topic 'X' of the source group -> topic 'X' of your group (created if missing)."""
    cfg = await get_cfg(uid)
    if not cfg["chat"] or not await get_user_data_key(uid, "route_mirror", True):
        return None
    tid = getattr(m, "message_thread_id", None)
    if not tid or tid == 1:          # not a topic message / General
        return None
    title = await get_source_title([u, c], src, tid)
    if not title:
        return None
    key = tkey(title)
    if not key:
        return None
    async with _mirror_lock:
        mp = await get_user_data_key(uid, "route_mirror_map", {}) or {}
        if key not in mp:
            await sync_dest_topics(uid, [u, c])
            mp = await get_user_data_key(uid, "route_mirror_map", {}) or {}
        if key not in mp and await get_user_data_key(uid, "route_autocreate", True):
            new_id = await _create_topic([c, u], int(cfg["chat"]), title)
            if new_id:
                mp[key] = new_id
                await save_user_data(uid, "route_mirror_map", mp)
        if key in mp:
            return int(cfg["chat"]), int(mp[key])
    return None

async def clone_topics(uid, clients, src):
    """Create in your group every topic that exists in the source group. Returns (created, existing) or None."""
    chat = (await get_cfg(uid))["chat"]
    if not chat:
        return None
    titles = None
    for cl in clients:
        if cl is None:
            continue
        try:
            titles = [t.title async for t in cl.get_forum_topics(_cid(src)) if t.id != 1]
            break
        except Exception as e:
            print(f"read source topics failed: {e}")
    if titles is None:
        return None
    await sync_dest_topics(uid, clients)
    created = existing = 0
    async with _mirror_lock:
        mp = await get_user_data_key(uid, "route_mirror_map", {}) or {}
        for title in titles:
            key = tkey(title)
            if not key or key in mp:
                existing += 1
                continue
            new_id = await _create_topic(clients, int(chat), title)
            if new_id:
                mp[key] = new_id; created += 1
                await asyncio.sleep(1.5)     # avoid flood limits
        await save_user_data(uid, "route_mirror_map", mp)
    return created, existing
