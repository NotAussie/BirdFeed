import re


def convert_handles_to_links(text):
    """
    Converts handles in the format "@something.something" to clickable links.
    Example: "@user123" becomes "(@user123)"
    """

    def handle_to_link(match):
        handle = match.group(0)  # Get the matched handle
        username = handle[1:]  # Remove the "@" symbol
        link = f"[{handle}](https://bsky.app/profile/{username})"
        return link

    # Define the regex pattern for handles (modify as needed)
    handle_pattern = r"@\w+\.\w+(?:\.\w+)?"

    # Replace handles with links
    result = re.sub(handle_pattern, handle_to_link, text)
    return result


def convert_hashtags_to_links(text):
    # Define the regex pattern for hashtags
    pattern = r"#(\w+)"

    # Replace hashtags with the desired format
    def replace(match):
        hashtag = match.group(0)
        hashtagText = hashtag[1:]
        link = f"[{hashtag}](https://bsky.app/hashtag/{hashtagText})"
        return link

    # Apply the regex substitution to the input text
    result = re.sub(pattern, replace, text)
    return result


def get_post_url(handle, postID):
    return "https://bsky.app/profile/{}/post/{}".format(handle, postID)
