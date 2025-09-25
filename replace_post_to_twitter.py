from pathlib import Path

path = Path("fun_fact_poster.py")
lines = path.read_text().splitlines()
start = None
end = None
for idx, line in enumerate(lines):
    if line.startswith("def post_to_twitter("):
        start = idx
    if start is not None and idx > start and line.startswith("def "):
        end = idx
        break
if start is None:
    raise SystemExit("post_to_twitter not found")
if end is None:
    end = len(lines)
new_block = """def post_to_twitter(client: tweepy.Client, tweet_text: str) -> None:
    logging.info("Posting news summary to Twitter...")
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            client.create_tweet(text=tweet_text)
        except tweepy.errors.TooManyRequests as error:
            delay = compute_rate_limit_delay(error) or get_rate_limit_backoff_seconds()
            logging.warning(
                "Twitter rate limit hit (attempt %s/%s); sleeping %s seconds before retry.",
                attempt,
                max_attempts,
                delay,
            )
            time.sleep(delay)
            continue
        except tweepy.TweepyException:
            logging.exception("Twitter API error when posting tweet.")
            raise
        logging.info("Tweet posted successfully.")
        return

    raise RuntimeError("Unable to post tweet after handling rate limits.")
"""
lines[start:end] = new_block.strip("\n").split("\n")
path.write_text("\n".join(lines) + "\n")
