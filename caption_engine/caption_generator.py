import logging
import random
import re
from caption_engine.hashtag_generator import generate_hashtags
import logging
import random
import re
from caption_engine.hashtag_generator import generate_hashtags
from modules.gemini_safe import gemini_call
from caption_engine.description_generator import generate_affiliate_description

REQUIRED_PREFIX = "(Ad)(#CommissionEarned)"

CATCHY_WORDS = [
    "Snag It!", "Grab It!", "Pick It!", "Spot It!", "DealSnag!",
    "TrendGrab!", "QuickGrab!", "HotPick!", "ClickSnag!"
]


def generate_affiliate_caption(product_name, link):
    logger = logging.getLogger(__name__)
    catchy = random.choice(CATCHY_WORDS)

    hashtags = generate_hashtags(product_name)

    # Model guidance prompt (still used for future improvements)
    prompt = f"""
Start with:
{REQUIRED_PREFIX}

Catchy word:
{catchy}

Product:
{product_name}

Link:
{link}

Rules:
- DO NOT include nicknames
- DO NOT include descriptions
- ONLY return the required structured caption
- Keep link EXACT
- Use emojis only if natural
    """

    result = gemini_call(prompt)

    # We still clean model output, but we will IGNORE nickname + description anyway
    if result:
        content = result.strip()

        # Remove leading prefix (if model echoed it)
        if content.startswith(REQUIRED_PREFIX):
            content = content[len(REQUIRED_PREFIX):].strip()

        # Extract link (if model tried to modify — we ignore!)
        link_in_content = None
        m = re.search(r"https?://\S+", content)
        if m:
            link_in_content = m.group(0)

        # Remove hashtags model inserts (we override)
        hashtags_in_content = re.findall(r"#\w+", content)
        if hashtags_in_content:
            for t in set(hashtags_in_content):
                content = content.replace(t, "")

        # Remove any accidental text lines (we do NOT use them anyway)
        content = "\n".join([l.strip() for l in content.splitlines() if l.strip()])

    # Always use explicit link
    final_link = link if link else link_in_content

    # Always use deterministic hashtags
    final_hashtags = hashtags

    # FINAL MINIMAL REQUIRED OUTPUT (NO nickname, NO description)
    header_parts = [
        REQUIRED_PREFIX,
        catchy,
        product_name
    ]

    header = "\n".join(header_parts).strip()

    # Blank line before and after the link
    if final_link:
        link_block = f"\n\n👉 {final_link}\n\n"
    else:
        link_block = "\n\n"

    final_content = f"{header}{link_block}{final_hashtags}".strip()
    return final_content
    # Always use deterministic hashtags
