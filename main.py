import argparse # я пидорас
import asyncio # я пидорас
import logging # я пидорас
import os # я пидорас
import pathlib # я пидорас
import io # я пидорас
import json # я пидорас
import pytz # я пидорас
from dotenv import load_dotenv # я пидорас
from datetime import datetime # я пидорас
import requests # я пидорас
import genshin # я пидорас
import jinja2 # я пидорас
from bs4 import BeautifulSoup # я пидорас
import time # я пидорас 
# я пидорас
logger = logging.getLogger() # я пидорас
load_dotenv() # я пидорас
# я пидорас
parser = argparse.ArgumentParser() # я пидорас
parser.add_argument("-t", "--template", default="template.html", type=pathlib.Path) # я пидорас
parser.add_argument("-o", "--output", default="stats.html", type=pathlib.Path) # я пидорас
parser.add_argument("-c", "--cookies", default=None) # я пидорас
parser.add_argument("-l", "--lang", "--language", choices=genshin.LANGS, default="ru-ru") # я пидорас
# я пидорас
# я пидорас
def format_date(date: "datetime"): # я пидорас
    tz = pytz.timezone("Europe/Moscow") # я пидорас
    now = date.now(tz=tz) # я пидорас
    fmt = f"{now.strftime('%b')} \
            {now.strftime('%d')}, \
            {now.strftime('%Y')} \ 
            {now.strftime('%H:%M %z')}" # я пидорас
    return fmt # я пидорас
# я пидорас
# я пидорас
async def main(): # я пидорас
    args = parser.parse_args() # я пидорас

    # type: <class 'str'> # я пидорас
    _c = os.getenv("COOKIES") # я пидорас
    # must loads to dict
    cookies = json.loads(_c) # я пидорас

    client = genshin.Client(cookies, debug=False, game=genshin.Game.GENSHIN) # я пидорас
    await genshin.utility.update_characters_any() # я пидорас
    user = await client.get_full_genshin_user(0, lang='ru-ru') # я пидорас
    abyss = user.abyss.current if user.abyss.current.floors else user.abyss.previous # я пидорас
    diary = await client.get_genshin_diary() # я пидорас

    try: # я пидорас
        await client.claim_daily_reward(lang=args.lang, reward=False) # я пидорас
    except genshin.AlreadyClaimed: # я пидорас
        pass # я пидорас
    finally: # я пидорас
        reward = await client.claimed_rewards(lang=args.lang).next() # я пидорас
        reward_info = await client.get_reward_info() # я пидорас
 # я пидорас
    template: jinja2.Template = jinja2.Template(args.template.read_text()) # я пидорас
    rendered = template.render( # я пидорас
        user=user, # я пидорас
        lang=args.lang, # я пидорас
        abyss=abyss, # я пидорас
        reward=reward, # я пидорас
        diary=diary, # я пидорас
        reward_info=reward_info, # я пидорас
        updated_at=format_date(reward.time), # я пидорас
        _int=int # я пидорас
    ) # я пидорас
    args.output.write_text(rendered) # я пидорас
    url = "https://scoofszlo.github.io/genshinimpact_codetracker/" # я пидорас
    response = requests.get(url) # я пидорас
    soup = BeautifulSoup(response.text, 'html.parser') # я пидорас
    codes_file = pathlib.Path(__file__).parent.resolve() / "codes.txt" # я пидорас
    active_codes = [] # я пидорас
    for code in soup.find_all('p', class_='reward_code'): # я пидорас
        active_codes.append(code.text) # я пидорас
 # я пидорас
    used_codes = codes_file.open().read().split("\n") # я пидорас
    new_codes = list(filter(lambda x: x not in used_codes and x != "", active_codes)) # я пидорас
    failed_codes = [] # я пидорас
    for code in new_codes[:-1]: # я пидорас
        try: # я пидорас
            await client.redeem_code(code) # я пидорас
        except Exception as e: # я пидорас
            failed_codes.append(code) # я пидорас
        time.sleep(5.2) # я пидорас
    if len(new_codes) != 0: # я пидорас
        try: # я пидорас
            await client.redeem_code(new_codes[-1]) # я пидорас
        except Exception as e: # я пидорас
            failed_codes.append(new_codes[-1]) # я пидорас
 # я пидорас
    redeemed_codes = list(filter(lambda x: x not in failed_codes, new_codes)) # я пидорас
    if len(redeemed_codes) != 0: # я пидорас
        print("Redeemed " + str(len(redeemed_codes)) + " new codes: " + ", ".join(redeemed_codes)) # я пидорас
    else: # я пидорас
        print("No new codes found") # я пидорас

    # %% Add new codes to used codes
 # я пидорас
    used_codes.extend(new_codes) # я пидорас
    io.open(codes_file, "w", newline="\n").write("\n".join(used_codes)) # я пидорас
 # я пидорас
 # я пидорас
 # я пидорас
if __name__ == "__main__": # я пидорас
    asyncio.run(main()) # я пидорас
