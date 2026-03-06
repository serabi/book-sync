# Service Setup Guide

This page walks through configuring each integration in PageKeeper.

The goal is to help you get connected quickly, verify each service, and avoid common first-time setup mistakes.

---

## Setup Strategy (Recommended)

Configure one service at a time, test it, then move to the next.

Good order for most setups:

1. Audiobookshelf (if used)
2. Ebook-side service (KoSync, Storyteller, Booklore, or CWA)
3. Optional external book tracking (Hardcover)
4. Optional notifications (Telegram)

This keeps troubleshooting narrow and faster.

---

## Where to Configure Services

In the web UI:

1. Open **Settings**
2. Go to the service section you want
3. Enable the service
4. Enter URL/credentials
5. Click **Save**
6. Click that section's **Test** button

If test passes, move to the next service.

---

## Audiobookshelf

### What it is used for

- Main audiobook source
- Progress read/write for audiobook books
- Real-time event source (Socket.IO) for fast sync and suggestions

### What you need

- ABS server URL
- API token
- Library selection (if relevant to your setup)

### Validate

- Use **Test** in the Audiobookshelf section
- Confirm no auth errors
- Confirm expected library/books are visible in matching flows

### Common issues

- Wrong base URL (missing protocol or bad port)
- Invalid/expired API token
- Container cannot reach ABS host/network

---

## KoSync (KOReader)

### What it is used for

- KOReader progress sync endpoint
- EPUB position exchange for e-reader workflows

### What you need

- KoSync enabled in Settings
- User + key configured
- Correct server/public URL depending on LAN vs remote usage

### Validate

- Use **Test** in KoSync section
- Confirm KOReader can authenticate and push/pull progress

### Common issues

- Public URL mismatch (especially with reverse proxy)
- Missing TLS when exposing sync endpoint externally
- Wrong credentials entered in KOReader

For remote access hardening, follow [KOSync Split Port and Security](KOSync-Split-Port-and-Security.md).

---

## Storyteller

### What it is used for

- Syncing audiobooks and EPUBs together in Storyteller's workflow
- Producing EPUB3-style synced book data that PageKeeper can consume
- Providing native `wordTimeline` timing data for fast, accurate alignment

### What you need

- Storyteller API URL
- Username/password
- Storyteller processing/assets directory mounted into PageKeeper (recommended if you want native alignment)

### Validate

- Use **Test** in Storyteller section
- Confirm connection and auth
- If using native alignment, confirm assets path is mounted and configured correctly

### Common issues

- Wrong API base URL
- Credentials valid in UI but blocked by network/proxy from container
- Assets directory path mismatch between host mount and settings value

For deeper alignment behavior, see [Alignment Methods](Alignment-Methods.md).

---

## Booklore

### What it is used for

- Ebook metadata and files via API
- Ebook progress sync target/source
- Audiobooks (if you use Booklore for audiobooks - better support coming soon in PageKeeper for audiobook sync from Booklore)

### What you need

- Booklore server URL
- Username/password
- Optional shelf/library constraints depending on your organization

Note: You can have two Booklore sources configured at once. 

### Validate

- Use **Test** in Booklore section
- Confirm expected library content appears during matching

### Common issues

- Wrong URL path/base
- Account has auth but insufficient access to target library
- Multiple Booklore sources with overlapping filenames (can cause confusion without careful source mapping)

---

## CWA (Calibre-Web Automated)

### What it is used for

- Additional ebook source via API
- Useful if you are not using local `/books` mount

### What you need

- CWA URL
- Username/password

### Validate

- Use **Test** in CWA section
- Confirm books are discoverable in matching and suggestion flows

### Common issues

- OPDS/API endpoint mismatch
- Credentials accepted in browser but blocked from container network

---

## Hardcover

### What it is used for

- External reading progress/status destination
- Read-tracking ecosystem integration

### What you need

- Hardcover API token

### Validate

- Use **Test** in Hardcover section
- Confirm token has expected access

### Common issues

- Invalid token
- Token copied with whitespace or truncated

---

## BookFusion

### What it is used for

- Ebook highlight sync
- Library catalog and book matching
- Upload ebooks to BookFusion
- Manual reading progress with chain sync to other services

### What you need

- Highlights API key (from BookFusion → Settings → Integrations → Obsidian)
- Upload API key (from BookFusion → Settings → Integrations → Calibre) — optional but recommended

### Validate

- Use **Test** in the BookFusion section for each key
- Sync highlights and confirm they appear on the BookFusion page
- Check Library tab shows your full catalog

### Common issues

- Using the wrong API key in the wrong field (Obsidian key vs Calibre key)
- Only seeing books with highlights in Library tab (upload key not configured)
- Highlights not updating (sync is incremental — only new highlights since last cursor)

For detailed behavior including chain sync and highlight features, see [BookFusion](BookFusion.md).

---

## Telegram

### What it is used for

- Notification sink for selected log levels/events

### What you need

- Bot token
- Chat ID
- Preferred log threshold

### Validate

- Use **Test** in Telegram section
- Confirm message arrives in the target chat

### Common issues

- Wrong chat ID
- Bot not added to target chat/channel
- Log threshold too high so expected messages are suppressed

---

## After All Services Are Configured

Run this quick checklist:

- Every enabled service passes **Test**
- You can create at least one mapping from **Single Match**
- A progress update in one client appears in mapped client(s)
- Logs show sync activity without repeating auth failures

Then continue to [Book Mapping and Sync Workflows](Book-Mapping-and-Sync-Workflows.md).

---

## Related Pages

- [Install and First Run](Install-and-First-Run.md)
- [Configuration Reference](Configuration-Reference.md)
- [Alignment Methods](Alignment-Methods.md)
- [Troubleshooting](Troubleshooting.md)
