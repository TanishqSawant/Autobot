import os
import time
import requests

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright


# ============================================================
# SETTINGS
# ============================================================

CHANNEL_NAME = input("Enter the Twitch channel: ").strip()

TWITCH_STREAM_URL = f"https://www.twitch.tv/{CHANNEL_NAME}"

YOUTUBE_URL = "https://www.youtube.com/live/hwG3bvxkSJQ?si=zQaGBvnyLjlZujAU"

MESSAGE = "Follow this link to get 10% OFF on boosting service of any game: https :// s.skycoach.gg/ NIGHTMARE"

DELAY = 15
MAX_MESSAGES = 5

# This must be the Twitch account that owns the access token
TWITCH_SENDER_ID = "1533491568"

TWITCH_USERS_URL = "https://api.twitch.tv/helix/users"
TWITCH_CHAT_URL = "https://api.twitch.tv/helix/chat/messages"


# ============================================================
# LOAD TWITCH CREDENTIALS
# ============================================================

load_dotenv()

client_id = os.getenv("TWITCH_CLIENT_ID")
token = os.getenv("TWITCH_ACCESS_TOKEN")

if not client_id or not token:
    raise RuntimeError(
        "TWITCH_CLIENT_ID or TWITCH_ACCESS_TOKEN was not found in .env"
    )


twitch_headers = {
    "Client-Id": client_id,
    "Authorization": "Bearer " + token,
    "Content-Type": "application/json"
}


# ============================================================
# GET BROADCASTER ID AUTOMATICALLY
# ============================================================

print("\nLooking up Twitch channel...")

response = requests.get(
    TWITCH_USERS_URL,
    headers=twitch_headers,
    params={
        "login": CHANNEL_NAME
    }
)

if response.status_code != 200:
    print("Could not find Twitch channel.")
    print("Status:", response.status_code)
    print(response.text)
    raise SystemExit


data = response.json()

if not data.get("data"):
    print(f"Channel '{CHANNEL_NAME}' was not found.")
    raise SystemExit


TWITCH_BROADCASTER_ID = data["data"][0]["id"]

print("Channel:", CHANNEL_NAME)
print("Broadcaster ID:", TWITCH_BROADCASTER_ID)


# ============================================================
# TWITCH FUNCTION
# ============================================================

def send_twitch_message():

    message_data = {
        "broadcaster_id": TWITCH_BROADCASTER_ID,
        "sender_id": TWITCH_SENDER_ID,
        "message": MESSAGE
    }

    response = requests.post(
        TWITCH_CHAT_URL,
        headers=twitch_headers,
        json=message_data
    )

    print("Twitch API status:", response.status_code)

    if response.status_code != 200:
        print("Twitch: request failed")
        print(response.text)
        return False

    data = response.json()

    result = data["data"][0]

    print("Twitch message ID:", result.get("message_id"))
    print("Twitch is_sent:", result.get("is_sent"))

    if result.get("is_sent") is True:
        print("Twitch: message ACTUALLY SENT")
        return True

    drop_reason = result.get("drop_reason")

    print("Twitch: message was DROPPED")
    print("Drop reason:", drop_reason)

    return False


# ============================================================
# YOUTUBE FUNCTION
# ============================================================

def send_youtube_message(page):

    print("Looking for YouTube chat...")

    chat_frame = page.frame_locator("#chatframe")

    chat_box = chat_frame.locator(
        "#live-chat-message-input"
    )

    chat_box.wait_for(
        state="visible",
        timeout=30000
    )

    print("YouTube chat found!")

    chat_box.click()

    page.keyboard.type(MESSAGE)

    page.keyboard.press("Enter")

    print("YouTube: message sent")

    return True


# ============================================================
# MAIN PROGRAM
# ============================================================

with sync_playwright() as p:

    print("\nConnecting to Chrome...")

    browser = p.chromium.connect_over_cdp(
        "http://127.0.0.1:9222"
    )

    context = browser.contexts[0]

    print("Connected to Chrome.")


    # ========================================================
    # OPEN TWITCH STREAM
    # ========================================================

    print("\nOpening Twitch stream...")

    twitch_page = context.new_page()

    twitch_page.goto(
        TWITCH_STREAM_URL,
        wait_until="domcontentloaded"
    )

    print("Twitch stream opened.")


    # ========================================================
    # OPEN YOUTUBE STREAM
    # ========================================================

    print("\nOpening YouTube stream...")

    youtube_page = context.new_page()

    youtube_page.goto(
        YOUTUBE_URL,
        wait_until="domcontentloaded"
    )

    print("YouTube stream opened.")


    # ========================================================
    # MESSAGE LOOP
    # ========================================================

    count = 0

    try:

        while count < MAX_MESSAGES:

            print("\n==============================")
            print(f"Starting cycle {count + 1}")
            print("==============================")


            # ------------------------------------------------
            # YOUTUBE
            # ------------------------------------------------

            youtube_success = False

            try:

                youtube_success = send_youtube_message(
                    youtube_page
                )

            except Exception as error:

                print("YouTube error:")
                print(error)


            # ------------------------------------------------
            # TWITCH
            # ------------------------------------------------

            twitch_success = False

            try:

                twitch_success = send_twitch_message()

            except Exception as error:

                print("Twitch error:")
                print(error)


            # ------------------------------------------------
            # COUNT
            # ------------------------------------------------

            if youtube_success or twitch_success:

                count += 1

                print(
                    f"\nCycle {count}/{MAX_MESSAGES} completed."
                )

            else:

                print("\nNeither message was sent.")


            # ------------------------------------------------
            # WAIT
            # ------------------------------------------------

            if count < MAX_MESSAGES:

                print(
                    f"Waiting {DELAY} seconds..."
                )

                time.sleep(DELAY)


    except KeyboardInterrupt:

        print("\nBot stopped by user.")


    print("\nBot finished.")