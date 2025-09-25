# News Summary Twitter Bot

This automation polls the latest headlines via NewsAPI, summarises an unseen story with OpenAI, and tweets the update with a short summary, article link, and auto-selected hashtags on whatever cadence you choose.

## Prerequisites
- Python 3.9+
- Twitter developer app with OAuth 1.0a user-context keys that have **Read and Write** permissions
- [NewsAPI](https://newsapi.org/) key (free tier works for top headlines)
- OpenAI API key

## Setup
1. Clone or download this repository.
2. Create and activate a virtual environment, then install dependencies:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your credentials:
   ```powershell
   Copy-Item .env.example .env
   ```

   | Variable | Description |
   | --- | --- |
   | `OPENAI_API_KEY` | OpenAI API key |
   | `OPENAI_MODEL` | (Optional) Model name, defaults to `gpt-4.1-mini` |
   | `NEWSAPI_KEY` | NewsAPI key used to fetch headlines |
   | `NEWS_COUNTRY` | (Optional) Comma-separated ISO codes or regions, e.g. `us,gb,europe,asia` |
   | `NEWS_CATEGORY` | (Optional) Comma-separated categories, e.g. `business,technology` |
   | `NEWS_LANGUAGE` | (Optional) Language code (used only when no country is set); defaults to `en` |
   | `TWITTER_API_KEY` | Twitter/X API key (consumer key) |
   | `TWITTER_API_SECRET` | Twitter/X API secret |
   | `TWITTER_ACCESS_TOKEN` | OAuth1 access token (must show "Read and Write") |
   | `TWITTER_ACCESS_TOKEN_SECRET` | OAuth1 access token secret |
   | `FACT_STORAGE_PATH` | (Optional) History file path, defaults to `news_post_history.jsonl` |

   > Tip: When both `NEWS_COUNTRY` and `NEWS_CATEGORY` list multiple values, the bot cycles through every combination until it finds an unseen article. NewsAPI ignores `NEWS_LANGUAGE` when `NEWS_COUNTRY` is present-the country's default language is used automatically.
   > Hashtags are picked automatically from the story's category (tech, business, sport, etc.), and a regional tag like `#USNews` is added when a country filter is used.

4. Test a single post (this tweets immediately-use a staging account if needed):
   ```powershell
   python fun_fact_poster.py --once
   ```

## Continuous Posting
Run the bot in a long-lived shell (defaults to a ~90-minute interval (~16 posts/day); pass `--interval 60` for quick tests):
```powershell
python fun_fact_poster.py
```
The script fetches up to ten headlines per query, picks the first URL you haven't posted, asks OpenAI for a concise summary, then posts the summary, the article link, and 2-3 category-aware hashtags (adding a country tag when available) before sleeping for 1,800 seconds by default. Override the cadence with --interval (increase/decrease as needed) or widen the article pool with --page-size.

### Windows Task Scheduler (optional)
1. Open **Task Scheduler** -> **Create Task**.
2. Add a trigger (e.g. "At log on" or a repeating schedule).
3. Add an action:
   - Program/script: `powershell`
   - Add arguments: `-NoProfile -ExecutionPolicy Bypass -Command "cd /d <path-to-project>; .\.venv\Scripts\Activate; python fun_fact_poster.py"`
4. Enable **Run whether user is logged on or not** if you want it detached.

## Deduplication & History
- Tweets are logged in `news_post_history.jsonl` along with article metadata and the generated summary.
- On startup the bot reads this file and skips URLs it's already posted.
- If the history file becomes corrupt, delete or fix it-the bot will recreate it.

## Troubleshooting
- **401/403 errors**: Regenerate the OAuth1 access token + secret and confirm the app permissions are set to Read & Write.
- **NewsAPI quota**: Free plans allow 100 requests/day. Slow down the interval or upgrade if you hit the limit.
- **Long tweets**: The summariser retries with tighter limits, but some stories with very long titles/descriptions may still need manual editing.
