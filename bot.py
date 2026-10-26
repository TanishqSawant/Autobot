from playwright.sync_api import sync_playwright
import time

YOUTUBE_URL = "https://www.twitch.tv/dota2ti"
MESSAGE = "Hello, From this side!!!"

with sync_playwright() as p:
    print("Connecting to Chrome...")

    browser = p.chromium.connect_over_cdp(
        "http://127.0.0.1:9222"
    )

    context = browser.contexts[0]
    page = context.pages[0] 

    print("Connected successfully!")
    print("Opening Live stream...")
    page.goto(YOUTUBE_URL, wait_until="domcontentloaded")

    print("LiveStream opened!")
    print("Waiting for live chat to load...")

    chat_frame = page.frame_locator("#chatframe")
    chat_input = chat_frame.locator("#live-chat-message-input")
    chat_input.wait_for(state="visible", timeout=30000)
    print("chat input found!")
    chat_input.click()

    running = True
    count = 0
    while running:
        page.keyboard.type(MESSAGE)
        page.keyboard.press("Enter")
        time.sleep(15) 
        print("Test message sent")
        count +=1 

        if count == 100:
            running = False

        print("Message typed !")
       

    

    
    print("Title:", page.title())
    print("URL:", page.url)
