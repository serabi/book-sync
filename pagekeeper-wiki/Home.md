# PageKeeper Wiki

Welcome to the PageKeeper wiki.

If you're new here, start with the install guide and you can usually get to a working dashboard going fairly quickly. If you're already running PageKeeper, jump to service setup, alignment behavior, or troubleshooting.

---

## What PageKeeper Is

PageKeeper is a self-hosted reading companion that keeps your progress in sync across audiobook and ebook platforms.

At a high level, it does two jobs:

1. **Reading tracker** — tracks what you’re reading, progress state, and reading lifecycle.
2. **Cross-format sync engine** — converts position formats between services (for example, audiobook time ↔ ebook position) and propagates updates.

You can run it with as many or as few integrations as you want.

---

## Supported Integrations

| Service | Role |
|---|---|
| Audiobookshelf | Currently the primary audiobook source |
| KOReader (via KoSync) | E-reader progress sync |
| Storyteller | Audiobook/EPUB companion platform |
| Booklore | Ebook library and metadata source |
| Calibre-Web Automated (CWA) | Additional ebook source |
| Hardcover | Reading-status and progress destination |
| BookFusion | Ebook library, highlights, and reading progress |
| Telegram | Notifications |

Future possibilities and integrations include Booklore audiobook support and potentially Chaptarr support. I'm always open to other suggestions.

---

## How Sync Works (Short Version)

PageKeeper runs three sync layers:

1. **Instant events** (Socket/KoSync updates)
2. **Per-client polling**
3. **Scheduled full sync**

When a change is detected, PageKeeper normalizes the position and pushes it to other connected services.

To prevent feedback loops, write suppression ignores echoes from updates PageKeeper just sent.

---

## How Alignment Works (Why It Matters)

For linked audiobook + ebook books, PageKeeper needs an alignment map before cross-format conversion is exact.

Alignment source priority:

1. Storyteller native timing data (`wordTimeline`)
2. EPUB SMIL timing data
3. Whisper-based transcript matching

After the alignment map is built, conversions are fast and reused.

---

## Start Here

### New users

1. [Install and First Run](Install-and-First-Run.md)
2. [Service Setup Guide](Service-Setup-Guide.md)
3. [Book Mapping and Sync Workflows](Book-Mapping-and-Sync-Workflows.md)

### Existing users

- [Configuration Reference](Configuration-Reference.md)
- [Deployment and Docker Options](Deployment-and-Docker-Options.md)
- [BookFusion](BookFusion.md)
- [Alignment Methods](Alignment-Methods.md)
- [Suggestions and Discovery](Suggestions-and-Discovery.md)
- [Troubleshooting](Troubleshooting.md)

### Security and remote KOReader access

- [KOSync Split Port and Security](KOSync-Split-Port-and-Security.md)

---

## Documentation Map

- [Home](Home.md)
- [Install and First Run](Install-and-First-Run.md)
- [Service Setup Guide](Service-Setup-Guide.md)
- [Configuration Reference](Configuration-Reference.md)
- [Deployment and Docker Options](Deployment-and-Docker-Options.md)
- [Book Mapping and Sync Workflows](Book-Mapping-and-Sync-Workflows.md)
- [BookFusion](BookFusion.md)
- [Alignment Methods](Alignment-Methods.md)
- [Suggestions and Discovery](Suggestions-and-Discovery.md)
- [KOSync Split Port and Security](KOSync-Split-Port-and-Security.md)
- [Troubleshooting](Troubleshooting.md)
- [FAQ](FAQ.md)
