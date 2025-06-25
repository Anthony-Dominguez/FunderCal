import os
from dotenv import load_dotenv
import logging
import discord
from discord.ext import commands
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def fetch_calendar_events(days_ahead, currency_pair):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    from bs4 import BeautifulSoup
    from datetime import datetime, timedelta
    import time
    import re

    def parse_event_date(dd_mm_str):
        try:
            day, month = map(int, dd_mm_str.split('.'))
            return datetime(datetime.now().year, month, day)
        except Exception:
            return datetime.max

    username = os.getenv('FUNDERPRO_USERNAME')
    password = os.getenv('FUNDERPRO_PASSWORD')
    if not username or not password:
        return "FUNDERPRO_USERNAME or FUNDERPRO_PASSWORD not set in .env"

    login_url = "https://prop.funderpro.com/login"
    asset_url = "https://prop.funderpro.com/lab/asset-overview"
    threshold = datetime.now() + timedelta(days=days_ahead)

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    try:
        # Step 1: Navigate to login page
        driver.get(login_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Step 2: Login
        username_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        password_field = driver.find_element(By.NAME, "password")
        username_field.send_keys(username)
        password_field.send_keys(password)

        try:
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except NoSuchElementException:
            login_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        login_button.click()
        WebDriverWait(driver, 10).until(EC.url_changes(login_url))

        # Step 3: Go to asset overview and search for the currency pair
        driver.get(asset_url)
        WebDriverWait(driver, 10).until(EC.url_contains("asset-overview"))
        time.sleep(2)

        # Search for the currency pair
        currency_pair = currency_pair.upper()
        try:
            pair_element = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{currency_pair}')]") )
            )
            pair_element.click()
            container_xpath = "//div[contains(@class, 'Calendar__contentContainer__')]"
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, container_xpath)))
            time.sleep(1.5)
        except TimeoutException:
            driver.save_screenshot(f"{currency_pair.replace('/', '_')}_not_found.png")
            return f"Currency pair '{currency_pair}' not found or content did not update."

        # Scrape calendar data
        soup = BeautifulSoup(driver.page_source, "html.parser")
        calendar_divs = soup.find_all(
            "div", class_=lambda x: x and 'Calendar__contentContainer__' in x
        )

        results = []
        for i, calendar_div in enumerate(calendar_divs, 1):
            heads = calendar_div.find_all(
                "div", class_=lambda x: x and 'EconomicTile__tileHead__' in x
            )
            bodies = calendar_div.find_all(
                "div", class_=lambda x: x and 'EconomicTile__tileBody__' in x
            )
            if len(heads) != len(bodies):
                continue

            calendar_data = {"div_index": i, "events": []}
            for j, (head, body) in enumerate(zip(heads, bodies), 1):
                head_text = head.get_text(strip=True)
                parts = head_text.split("Impact")
                impact = parts[0].strip() + " Impact" if len(parts) == 2 else head_text
                region = parts[1].strip() if len(parts) == 2 else "Unknown"

                countdown = body.find_next(
                    "div",
                    class_=lambda x: x and 'EconomicTile__eventTimeCountdown__' in x,
                )
                status = countdown.get_text(strip=True) if countdown else "Unknown"

                text = body.get_text(strip=True)
                match = re.match(
                    r"^(.*?)(?:\d{2}\.\d{2}\s+(?:\d{2}:\d{2}|\d{1,2}[dh]\s+\d{1,2}m))",
                    text,
                )
                event_name = match.group(1).strip() if match else text
                rem = text[len(event_name):].strip() if match else text

                dt_match = re.search(
                    r"(\d{2}\.\d{2})\s+(?:(\d{2}:\d{2})|(\d{1,2}[dh]\s+\d{1,2}m))",
                    rem,
                )
                date_str = dt_match.group(1) if dt_match else "Unknown"
                time_cd = (dt_match.group(2) or dt_match.group(3)) if dt_match else "Unknown"
                rem_after = rem[dt_match.end():].strip() if dt_match else rem

                if countdown is None and "Expired" in rem_after:
                    status = "Expired"
                    info = rem_after.replace("Expired", "").strip()
                else:
                    info = rem_after

                calendar_data["events"].append({
                    "entry": j,
                    "impact": impact,
                    "region": region,
                    "event": event_name,
                    "date": date_str,
                    "time_or_countdown": time_cd,
                    "status": status,
                    "info": info,
                })

            if calendar_data["events"]:
                results.append(calendar_data)

        # Filter out events beyond the threshold date
        filtered_results = []
        for calendar in results:
            upcoming = []
            for ev in calendar["events"]:
                ev_dt = parse_event_date(ev["date"])
                if ev_dt <= threshold:
                    upcoming.append(ev)
            if upcoming:
                calendar["events"] = upcoming
                filtered_results.append(calendar)

        # Build output string
        output_lines = []
        for calendar in filtered_results:
            output_lines.append("\n" + "=" * 60)
            output_lines.append(f"📅 Calendar Section {calendar['div_index']} — Next {days_ahead} days")
            output_lines.append("=" * 60)
            for ev in calendar["events"]:
                now_str = datetime.now().strftime("%d.%m  %H:%M")
                output_lines.append(f"  🕒 CURRENT TIME: {now_str}")
                output_lines.append(f"  {ev['entry']}. {ev['event']}")
                output_lines.append(f"    • Impact:     {ev['impact']}")
                output_lines.append(f"    • Country:    {ev['region']}")
                output_lines.append(f"    • Date:       {ev['date']}")
                output_lines.append(f"    • Time:       {ev['time_or_countdown']}")
                output_lines.append(f"    • Status:     {ev['status']}")
                if ev['info']:
                    output_lines.append(f"    • Info:       {ev['info']}")
                output_lines.append("  " + "-" * 50)
        if not output_lines:
            return f"No upcoming events found for {currency_pair} in the next {days_ahead} days."
        return '\n'.join(output_lines)
    except Exception as e:
        return f"Error: {e}"
    finally:
        driver.quit()

# Discord Bot Setup
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Bot logged in as {bot.user}")

@bot.command(name="calendar")
async def calendar(ctx, days: int, *, currency_pair: str):
    """
    Usage: !calendar 2 XAU/USD
    """
    await ctx.send(f"Fetching events for {currency_pair} for the next {days} days...")
    try:
        result = fetch_calendar_events(days, currency_pair)
        # Split and send in chunks, making sure each message (including backticks) is <= 2000 chars
        max_length = 1994  # 2000 - 6 for the triple backticks
        for i in range(0, len(result), max_length):
            chunk = result[i:i+max_length]
            await ctx.send(f"```{chunk}```")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send("Pong!")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)