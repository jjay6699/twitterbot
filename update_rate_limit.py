from pathlib import Path

path = Path("fun_fact_poster.py")
lines = path.read_text().splitlines()
insert_index = None
for idx, line in enumerate(lines):
    if line.startswith("def prepare_tweet("):
        end = idx + 1
        while end < len(lines) and (lines[end].startswith("    ") or lines[end] == ""):
            end += 1
        insert_index = end
        break
if insert_index is None:
    raise SystemExit("prepare_tweet not found")
helper_block = """
def compute_rate_limit_delay(error: tweepy.errors.TooManyRequests) -> Optional[int]:
    response = getattr(error, "response", None)
    headers = getattr(response, "headers", None)
    if not headers:
        return None

    retry_after = headers.get("retry-after") or headers.get("Retry-After")
    if retry_after:
        try:
            delay = int(float(retry_after))
            if delay >= 0:
                return delay
        except (TypeError, ValueError):
            pass

    reset_header = headers.get("x-rate-limit-reset") or headers.get("X-Rate-Limit-Reset")
    if reset_header:
        try:
            reset_at = int(float(reset_header))
        except (TypeError, ValueError):
            reset_at = None
        if reset_at:
            delay = reset_at - int(time.time())
            if delay > 0:
                return delay
    return None

def get_rate_limit_backoff_seconds() -> int:
    default_value = 15 * 60
    env_value = os.getenv("TWITTER_RATE_LIMIT_BACKOFF")
    if not env_value:
        return default_value
    try:
        parsed = int(env_value)
    except ValueError:
        logging.warning("Invalid TWITTER_RATE_LIMIT_BACKOFF value '%s'; using default %s", env_value, default_value)
        return default_value
    return max(1, parsed)
"""
helper_lines = helper_block.strip("\n").split("\n") + [""]
lines[insert_index:insert_index] = helper_lines
path.write_text("\n".join(lines) + "\n")
