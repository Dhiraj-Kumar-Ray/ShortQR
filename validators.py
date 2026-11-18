# urlparse splits a URL into parts (scheme, domain, path...)
from urllib.parse import urlparse

MAX_URL_LENGTH = 2000


def validate_url(raw_url):
    """
    Check and clean a URL typed by the user.
    Returns two values: (cleaned_url, error_message).
    If the URL is fine, error_message is None.
    If something is wrong, cleaned_url is None.
    """
    # Remove spaces from the start and end
    url = raw_url.strip()

    # Rule 1: it can't be empty
    if url == "":
        return None, "Please enter a URL."

    # Rule 2: it can't be absurdly long
    if len(url) > MAX_URL_LENGTH:
        return None, "That URL is too long."

    # Rule 3: it can't contain spaces in the middle
    if " " in url:
        return None, "A URL cannot contain spaces."

    # Friendly fix: if the user forgot https://, add it for them
    if "://" not in url:
        url = "https://" + url

    parsed = urlparse(url)

    # Rule 4: only web addresses are allowed
    if parsed.scheme not in ("http", "https"):
        return None, "Only http:// and https:// links are allowed."

    # Rule 5: it needs a real domain name, like example.com
    if parsed.hostname is None or "." not in parsed.hostname:
        return None, "That doesn't look like a valid web address."

    return url, None