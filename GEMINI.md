# Project: Re-archive (AI-Driven Document Pipeline)

## Overview
This project manages reconstruction data and automatically generates a public archive site using AI-driven summarization.

- **Private Repo (Current):** `rearchive2026/re-archive-data` (Raw documents and AI processing scripts)
- **Public Repo:** `rearchive2026/re-archive` (Cleaned/summarized data and static site)

## 📁 Directory Structure
Add your raw documents to these folders:
- `raw_data/Notices/`: PDF, PPTX, or text files for official notices.
- `raw_data/FAQ/`: FAQ documents.
- `raw_data/Guides/`: Guidelines and manuals.
- `raw_data/URLs/`: Text files containing external links.
- `raw_data/*.json`: Structured data (fields starting with `_` are automatically masked).

## ⚙️ AI Processing Pipeline
The `scripts/process.py` script automatically:
1. Extracts text from PDF and PPTX files.
2. Uses the **Gemini AI API** to generate titles, summaries, and tags.
3. Creates Jekyll-ready Markdown files in `dist/_posts/`.
4. Copies original documents to `dist/assets/raw_docs/` for download.

## Required Setup
1. **GitHub PAT:** Ensure `PUBLIC_REPO_TOKEN` is set in Private Repo Secrets.
2. **AI API Key:** Create a `.env` file in the root with `GEMINI_API_KEY=your_key_here`.
3. **Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## How to Run Locally
1. Place your raw files in the appropriate `raw_data/` subfolder.
2. Run the processing script:
   ```bash
   ./venv/bin/python3 scripts/process.py
   ```
3. Check the `dist/` folder for the generated content.
