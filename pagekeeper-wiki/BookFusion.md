# BookFusion

BookFusion is an ebook platform that supports reading, highlights, and library management. PageKeeper integrates with it for highlight sync, library catalog access, and reading progress tracking.

---

## Two API Keys

BookFusion uses two separate integration protocols, each with its own API key:

### Highlights API Key (`BOOKFUSION_API_KEY`)

Uses the BookFusion Obsidian sync protocol to fetch highlights and book metadata.

**Where to get it:** BookFusion → Settings → Integrations → Obsidian

This key enables:
- Highlight sync (incremental, cursor-based)
- Book metadata from highlighted books (title, author, tags, series)

### Upload API Key (`BOOKFUSION_UPLOAD_API_KEY`)

Uses the BookFusion Calibre plugin protocol to upload ebooks and fetch the full library catalog.

**Where to get it:** BookFusion → Settings → Integrations → Calibre

This key enables:
- Full library catalog (including books without highlights)
- Ebook uploads to BookFusion

Both keys are optional — you can configure one or both depending on what you need. The Highlights key is required for highlight sync; the Upload key is required for the full library catalog and uploads.

---

## Setup

1. Open **Settings** in the PageKeeper web UI
2. Find the **BookFusion** section
3. Enter one or both API keys
4. Click **Save**
5. Use **Test** for each key to verify connectivity

For general setup strategy, see [Service Setup Guide](Service-Setup-Guide.md).

---

## Highlight Sync

### How it works

- Uses BookFusion's Obsidian sync API with cursor-based pagination
- First sync fetches all highlights; subsequent syncs are incremental (only new or changed highlights since the last cursor)
- Each highlight includes book metadata (title, author, tags, series) which populates the library catalog

### What you see

Highlights appear on:
- The **BookFusion page** under the Highlights tab
- The **book detail page** in a collapsible highlights section, showing quote text, chapter heading, and date

### Incremental behavior

After the initial full sync, only new or modified highlights are fetched. To re-sync everything, the sync cursor would need to be reset.

---

## Library Catalog

The library catalog combines two sources:

1. **Highlights API** — books that have highlights (automatic with highlight sync)
2. **Calibre API** — full library including books without highlights (requires the Upload API key)

If only the Highlights key is configured, the Library tab will only show books that have at least one highlight.

---

## Manual Progress and Chain Sync

This is the key integration behavior for BookFusion-linked books.

### Setting progress

On the book detail page, BookFusion-linked books always show a percentage input. When you set a percentage:

1. Saves a `manual` progress state in PageKeeper
2. Marks the book as "active" with today's start date (if not already started)
3. Directly pushes the percentage to percentage-based services (Hardcover, Booklore)

### The chain to audiobook position

On the next sync cycle, if the book has both an ebook link and an alignment map:

4. The sync engine reads Booklore's updated position
5. Extracts the ebook text at that percentage via `get_text_at_percentage`
6. Runs the text through the alignment pipeline to find the corresponding audiobook timestamp
7. Updates Audiobookshelf to that timestamp

**Result:** BookFusion % → Booklore → (alignment map) → ABS audiobook position

### Requirements for full chain

- The book must have an ebook linked in a service that supports percentage (Booklore)
- An alignment map must be built for the book (see [Alignment Methods](Alignment-Methods.md))
- Services that accept percentage directly (Hardcover, Booklore) update immediately
- ABS updates on the next sync cycle after the chain completes

---

## Dashboard Integration

The dashboard card menu shows BookFusion status for each book:

- **Linked with highlights** — shows the highlight count
- **Linked without highlights** — shows linked status
- **"+" icon** — click to link the book; opens the BookFusion page on the Library tab with the book title pre-filled in search

---

## Book Detail Page

For BookFusion-linked books, the detail page shows:

- **Highlights** — collapsible section with quote text, chapter heading, and date
- **Tags and series** — from BookFusion, shown in the metadata panel
- **Service link** — BookFusion icon in the service links row
- **Manual progress** — percentage input for chain sync (see above)

---

## Linking Books

There are two approaches on the BookFusion page:

### Match to Book

Link a BookFusion catalog entry to an existing book on the dashboard. Use this when the book is already tracked in PageKeeper from another service.

### Add to Dashboard

Create a new dashboard entry for a BookFusion-only book. These entries are prefixed with `bf-` in the internal ID. Use this when the book isn't tracked anywhere else yet.

---

## Limitations

- Manual percentage cannot directly convert to an audiobook timestamp without the chain through an ebook service with an alignment map
- Highlight sync is incremental — to re-sync everything, the sync cursor would need to be reset
- The Calibre API library fetch requires the Upload API key to be configured
- BookFusion does not currently provide real-time events, so sync relies on polling and manual triggers

---

## Related Pages

- [Service Setup Guide](Service-Setup-Guide.md)
- [Alignment Methods](Alignment-Methods.md)
- [Book Mapping and Sync Workflows](Book-Mapping-and-Sync-Workflows.md)
- [Troubleshooting](Troubleshooting.md)
