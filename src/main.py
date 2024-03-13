# Imports
import asyncio
from tools.functools import periodic, startup
from atproto import AsyncClient, models
from yaml import safe_load
from typing import List
import datetime
from guilded_webhook import AsyncWebhook, Embed
from tools.texttools import (
    convert_hashtags_to_links,
    convert_handles_to_links,
    get_post_url,
)
from colorama import Fore
from tools.logger import Logger
from tools.db import save_posts, load_posts

# Get config
config = safe_load(open("/data/config.yml", "r"))
interval = int(config["interval"])
accounts = config["watch"]

# Define client
client = AsyncClient()
bot_profile: models.AppBskyActorDefs.ProfileViewDetailed = None
hook = AsyncWebhook(
    url=config["webhooks"][0],
)
logger = Logger()


# Load database
db = load_posts()


# This function automatically runs on loop starting
@startup()
async def on_startup():
    """On startup login to Bluesky and run other needed things."""

    # Login and store the logged in profile.
    global bot_profile
    bot_profile = await client.login(
        config["auth"]["handle"],
        config["auth"]["password"],
    )
    config["auth"]["password"] = "[REMOVED]"

    logger.output(
        "INFO",
        Fore.LIGHTCYAN_EX,
        "CLIENT:LOGIN",
        f"Logged in as @{bot_profile.handle}",
    )


# Function to process a profile's feed
async def process(
    feed: List[models.AppBskyFeedDefs.FeedViewPost],
    profile: models.AppBskyActorDefs.ProfileViewDetailed,
):
    """Reads a feed and then sends new posts though the provided webhook(s)."""

    hasUpdated = False

    for post in feed:
        if post.post.cid not in db:

            # Handle reposts
            if post.post.author.did != profile.did and not post.reply:
                # Construct embed
                embed = Embed(
                    title="New Repost!",
                    color=0x1185FE,
                    url=get_post_url(
                        post.post.author.handle,
                        post.post.uri.rsplit("/", 1)[-1],
                    ),
                )
                embed.set_author(
                    name="@" + post.post.author.handle,
                    url=f"https://bsky.app/profile/{post.post.author.handle}",
                )

                # Add description after processing it
                embed._description = post.post.record.text
                embed._description = convert_handles_to_links(embed._description)
                embed._description = convert_hashtags_to_links(embed._description)

                # Add a image if one exists
                if hasattr(post.post.record.embed, "images"):
                    img = post.post.record.embed.images[0]
                    embed.set_image(
                        "https://cdn.bsky.app/img/feed_fullsize/plain/{}/{}@jpeg".format(
                            post.post.author.did, img.image.ref.link
                        )
                    )

                # Get the timestamp and set it
                embed._timestamp = datetime.datetime.fromisoformat(
                    post.post.record.created_at.removesuffix("Z")
                )

                # Send the embed to the hook
                await hook.send(
                    embeds=[embed],
                    avatar=profile.avatar,
                    username=profile.display_name or profile.handle,
                )

                # Add post to database
                db.append(post.post.cid)
                hasUpdated = True

            # Handle replies
            elif post.reply:
                # TODO: Add reply processor, idk what the fuck to do here :P
                pass

            # Handle posts
            else:
                # Construct embed
                embed = Embed(
                    title="New post!",
                    color=0x1185FE,
                    url=get_post_url(
                        post.post.author.handle,
                        post.post.uri.rsplit("/", 1)[-1],
                    ),
                )
                embed.set_author(
                    name="@" + profile.handle,
                    url=f"https://bsky.app/profile/{profile.handle}",
                )

                # Add description after processing it
                embed._description = post.post.record.text
                embed._description = convert_handles_to_links(embed._description)
                embed._description = convert_hashtags_to_links(embed._description)

                # Add a image if one exists
                if hasattr(post.post.record.embed, "images"):
                    img = post.post.record.embed.images[0]
                    embed.set_image(
                        "https://cdn.bsky.app/img/feed_fullsize/plain/{}/{}@jpeg".format(
                            post.post.author.did, img.image.ref.link
                        )
                    )

                # Get the timestamp and set it
                embed._timestamp = datetime.datetime.fromisoformat(
                    post.post.record.created_at.removesuffix("Z")
                )

                # Send the embed to the hook
                await hook.send(
                    embeds=[embed],
                    avatar=profile.avatar,
                    username=profile.display_name or profile.handle,
                )

                # Add post to database
                db.append(post.post.cid)
                hasUpdated = True

    # If a post has been added then update the database
    if hasUpdated:
        save_posts(db)


# Automatically gather feeds
@periodic(interval_seconds=60)
async def gatherer() -> None:
    """Gathers all watched feeds and passes them into the process function."""
    if not bot_profile:
        while not bot_profile:
            await asyncio.sleep(0.1)

    for account in accounts:
        # Get the account feed
        view = await client.get_author_feed(actor=account)

        # Get the profile
        profile = await client.get_profile(actor=account)

        # Define the feed
        feed = view.feed
        feed.reverse()

        # Process the feed
        await process(feed, profile)


# Run the event loop
loop = asyncio.get_event_loop()
try:
    loop.run_forever()
except KeyboardInterrupt:
    logger.output(
        "INFO",
        Fore.LIGHTGREEN_EX,
        "CLIENT:STOP",
        f"Eventloop shutdown, goodbye",
    )

finally:
    loop.close()
