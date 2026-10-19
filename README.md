# Save Restricted Content Bot (private build)

Based on [Save-Restricted-Content-Bot-v3](https://github.com/devgaganin/Save-Restricted-Content-Bot-V2) by devgagan (GNU AGPL-3.0, see LICENSE).
Modified: own branding, video + PDF watermark, keyword-based topic routing, removed remote start-photo fetch, no default encryption keys.

## Setup
1. `cp .env.example .env` and fill API_ID, API_HASH, BOT_TOKEN, MONGO_DB, MASTER_KEY, IV_KEY (command for keys is inside `.env.example`).
2. `pip install -r requirements.txt` (ffmpeg must be installed; Dockerfile does it).
3. `python3 main.py` (or `docker build` + run).
4. In the bot send `/set` once (owner) to register the command list.

## Added features
- **Watermark**: `/wm`, `/wm text YOUR TEXT`, `/wm video on|off`, `/wm pdf on|off`. Video watermark re-encodes (ffmpeg, veryfast) so it is slower than a plain upload.
- **Auto mirror**: source topic `Physics Dharmendra Sir` -> topic with the same name in your group (`/route_chat`, `/mirror on`; missing topics are auto-created, `/sync_topics` re-reads yours; `/clone_topics <source>` creates all source topics in your group at once).
- **Topic routing** (manual rules, used when mirror finds nothing): `/route_chat -100...`, `/map_topic keyword topic_id`, `/unmap_topic`, `/default_topic`, `/topics`, `/route_off`. Keyword is matched in file name + caption (fancy Unicode fonts too). Bot needs admin + Manage Topics in the supergroup.
- Works for all four sources: private/public channel, private/public group.

## Note
If you let other people use this bot over the network, AGPL-3.0 requires you to offer them the modified source. Keep the copyright headers.
