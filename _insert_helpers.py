from pathlib import Path

INSERTION_ANCHOR = 'def pick_unseen_article('  # insert helpers after this block definition

path = Path('fun_fact_poster.py')
text = path.read_text()
anchor_index = text.find(INSERTION_ANCHOR)
if anchor_index == -1:
    raise SystemExit('anchor not found')
# find end of pick_unseen_article block by locating double newline after first occurrence after anchor
subtext = text[anchor_index:]
end_marker = '\n\n\n'
end_index = subtext.find(end_marker)
if end_index == -1:
    raise SystemExit('end marker not found after anchor')
insert_position = anchor_index + end_index + len('\n\n')  # keep single blank line between blocks

helpers = """

def _parse_json_payload(text: str) -> Optional[Dict[str, object]]:
    if not text:
        return None
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1 or end < start:
        logging.warning('OpenAI response missing JSON object: %s', text)
        return None
    snippet = text[start : end + 1]
    try:
        return json.loads(snippet)
    except json.JSONDecodeError:
        logging.warning('Failed to parse JSON from OpenAI response: %s', text)
        return None


def _normalise_hashtag(tag: str) -> Optional[str]:
    cleaned = tag.strip()
    if not cleaned:
        return None
    cleaned = cleaned.replace(' ', '')
    if not cleaned:
        return None
    if not cleaned.startswith('#'):
        cleaned = '#' + cleaned.lstrip('#')
    if len(cleaned) <= 1:
        return None
    return cleaned


def _sanitise_hashtags(tags: Iterable[str]) -> List[str]:
    ordered: List[str] = []
    seen: Set[str] = set()
    for raw in tags:
        if not isinstance(raw, str):
            continue
        normalised = _normalise_hashtag(raw)
        if not normalised or normalised.lower() in seen:
            continue
        seen.add(normalised.lower())
        ordered.append(normalised)
        if len(ordered) >= 3:
            break
    return ordered


def _generate_summary_payload(
    client: OpenAI,
    model: str,
    article: Dict[str, str],
    char_limit: int,
) -> Tuple[str, List[str]]:
    min_length = max(140, char_limit - 40)
    min_length = min(min_length, max(char_limit - 10, 0))
    prompt = (
        'Write a two-sentence Twitter update between '
        f"{min_length} and {char_limit} characters. Highlight the key development, the main actors, and any geographic context. '
        'Maintain a neutral tone and avoid marketing language. '
        'Return a JSON object with keys "summary" (string) and "hashtags" (array of 2-3 relevant Twitter hashtags, including their # prefix). '
        'Do not fabricate details or add URLs.'
    )
    context = (
        f"Title: {article['title']}\n"
        f"Description: {article['description']}\n"
        f"Content: {article['content']}\n"
        f"Source: {article['source']}\n"
        f"URL: {article['url']}"
    )
    response = client.responses.create(
        model=model,
        input=[
            {
                'role': 'system',
                'content': 'You are an assistant who drafts factual social media updates for breaking news.',
            },
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'input_text',
                        'text': f"{prompt}\n\n{context}",
                    }
                ],
            },
        ],
    )
    raw_text = extract_text_from_response(response)
    data = _parse_json_payload(raw_text)
    if not data:
        return '', []
    summary = str(data.get('summary') or '').strip()
    hashtags_raw = data.get('hashtags')
    if isinstance(hashtags_raw, str):
        hashtags_list = [hashtags_raw]
    elif isinstance(hashtags_raw, list):
        hashtags_list = [item for item in hashtags_raw if isinstance(item, str)]
    else:
        hashtags_list = []
    return summary, hashtags_list


"""
new_text = text[:insert_position] + helpers + text[insert_position:]
path.write_text(new_text)
