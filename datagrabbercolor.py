#! /usr/bin/python3
# -*- coding: utf-8 -*-

# clovervidia
import csv
import datetime
import glob
import json
import os
import random
import re

try:
    import readline
except ImportError:
    pass
import subprocess
import sys
import time
import urllib.request
from directaccesshelp import help_reader

import requests
from dateutil.relativedelta import relativedelta

# This prepares the Windows terminal to receive ANSI sequences somehow
os.system("")

try:
    with open("config.txt", "r", encoding="utf8") as config_file:
        config_data = json.load(config_file)
        COOKIE = config_data["cookie"]
except IOError:
    print("config.txt not found. Please check file.")
    sys.exit(1)
except ValueError:
    print("Cookie not found in config.txt. Please check file.")
    sys.exit(1)

TIMEZONE_OFFSET = "0"  # Offset is used to print the time on shared images. It's your offset from UTC in minutes.
# For example, EST (-4) is 240 and PST (-8) is 480

UNIQUE_ID = "8386546935489260343"  # Used to order gear from the SplatNet Shop
FRIEND_CODE = "YOUR NSO FC"  # Type "c" at the prompt to print your FC

# API endpoints
URL_API_SHARE_PROFILE = "https://app.splatoon2.nintendo.net/api/share/profile"
URL_API_SHARE_WINLOSS = "https://app.splatoon2.nintendo.net/api/share/results/summary"
URL_API_SHARE_BATTLE = "https://app.splatoon2.nintendo.net/api/share/results/{}"
URL_API_SHARE_CHALLENGE = "https://app.splatoon2.nintendo.net/api/share/challenges/{}"
URL_API_BATTLE_RESULTS = "https://app.splatoon2.nintendo.net/api/results/{}"
URL_API_RESULTS = "https://app.splatoon2.nintendo.net/api/results"
URL_API_RECORDS = "https://app.splatoon2.nintendo.net/api/records"
URL_API_COOP_SCHEDULES = "https://app.splatoon2.nintendo.net/api/coop_schedules"
URL_API_COOP_RESULTS = "https://app.splatoon2.nintendo.net/api/coop_results"
URL_API_DATA_STAGES = "https://app.splatoon2.nintendo.net/api/data/stages"
URL_API_ONLINESHOP_MERCH = "https://app.splatoon2.nintendo.net/api/onlineshop/merchandises"
URL_API_ONLINESHOP_ORDER = "https://app.splatoon2.nintendo.net/api/onlineshop/order/{}"
URL_API_RECORDS_HERO = "https://app.splatoon2.nintendo.net/api/records/hero"
URL_API_SCHEDULES = "https://app.splatoon2.nintendo.net/api/schedules"
URL_API_TIMELINE = "https://app.splatoon2.nintendo.net/api/timeline"
URL_API_FEST_ACTIVE = "https://app.splatoon2.nintendo.net/api/festivals/active"
URL_API_FEST_PASTS = "https://app.splatoon2.nintendo.net/api/festivals/pasts"
URL_API_FEST_RANKINGS = "https://app.splatoon2.nintendo.net/api/festivals/{}/rankings"
URL_API_FEST_RESULT = "https://app.splatoon2.nintendo.net/api/festivals/{}/result"
URL_API_FEST_VOTES = "https://app.splatoon2.nintendo.net/api/festivals/{}/votes"
URL_API_FEST_EVENTS = "https://app.splatoon2.nintendo.net/api/festivals/{}/events"
URL_API_LEAGUE_MATCH_RANKINGS = "https://app.splatoon2.nintendo.net/api/league_match_ranking/{}"
URL_API_NICKNAME_ICON = "https://app.splatoon2.nintendo.net/api/nickname_and_icon"
URL_API_X_POWER_RANKING_SUMMARY = "https://app.splatoon2.nintendo.net/api/x_power_ranking/{}T00_{}T00/summary"
URL_API_X_POWER_RANKING_PAGES = "https://app.splatoon2.nintendo.net/api/x_power_ranking/{}T00_{}T00/{}"
URL_API_BASE = "https://app.splatoon2.nintendo.net{}"
URL_API_SPLATOON2_INK_FEST_DATA = "https://splatoon2.ink/data/festivals.json"

# Folder names
JSON_FOLDER = "jsons"
BATTLES_FOLDER = "battles"
LEAGUE_RANKINGS_FOLDER = "league rankings"
X_RANKINGS_FOLDER = "x power rankings"
SPLATFEST_IMAGES_FOLDER = "splatfest images"
SPLATFEST_STATS_FOLDER = "splatfest stats"
GEAR_IMAGES_FOLDER = "gear images"
WEAPON_IMAGES_FOLDER = "weapon images"
SHARED_IMAGES = "shared images"

# Making sure the folders exist first
for folder in [JSON_FOLDER, os.path.join(JSON_FOLDER, BATTLES_FOLDER),
               os.path.join(JSON_FOLDER, LEAGUE_RANKINGS_FOLDER), os.path.join(JSON_FOLDER, X_RANKINGS_FOLDER),
               SPLATFEST_IMAGES_FOLDER, SPLATFEST_STATS_FOLDER, GEAR_IMAGES_FOLDER, WEAPON_IMAGES_FOLDER,
               SHARED_IMAGES]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Clipboard command
CLIP_CMD = "clip.exe"

# Commonly used headers
app_head_share = {
    "origin": "https://app.splatoon2.nintendo.net",
    "x-unique-id": UNIQUE_ID,
    "x-requested-with": "XMLHttpRequest",
    "x-timezone-offset": TIMEZONE_OFFSET,
    "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://app.splatoon2.nintendo.net/results",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US"
}

app_head_results = {
    "Host": "app.splatoon2.nintendo.net",
    "x-unique-id": UNIQUE_ID,
    "x-requested-with": "XMLHttpRequest",
    "x-timezone-offset": TIMEZONE_OFFSET,
    "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://app.splatoon2.nintendo.net/home",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US"
}

app_head_shop = {
    "origin": "https://app.splatoon2.nintendo.net",
    "x-unique-id": UNIQUE_ID,
    "x-requested-with": "XMLHttpRequest",
    "x-timezone-offset": TIMEZONE_OFFSET,
    "User-Agent": "Mozilla/5.0 (Linux; Android 7.1.2; Pixel Build/NJH47D; wv) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36",
    "Accept": "*/*",
    "Referer": "https://app.splatoon2.nintendo.net/results",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US"
}

# Splatfest IDs
FESTIVALS_NA = {"1": "2050", "2": "5051", "3": "2051", "4": "2052", "5": "2053", "6": "4051", "7": "2054", "8": "5052",
                "9": "2055", "10": "5053", "11": "5054", "12": "5056", "13": "5059", "14": "4052", "15": "2056",
                "16": "5060", "17": "4053", "18": "2057", "19": "4054", "20": "4055", "21": "5061"}
FESTIVALS_JP = {"1": "1051", "2": "1052", "3": "1054", "4": "1055", "5": "1056", "6": "4051", "7": "1057", "8": "1058",
                "9": "1059", "10": "1060", "11": "1061", "12": "1062", "13": "1063", "14": "4052", "15": "1065",
                "16": "1066", "17": "4053", "18": "1067", "19": "4054", "20": "4055", "21": "1068"}
FESTIVALS_EU = {"1": "3050", "2": "5051", "3": "3051", "4": "3052", "5": "3053", "6": "4051", "7": "3054", "8": "5052",
                "9": "3055", "10": "5053", "11": "5054", "12": "5056", "13": "5059", "14": "4052", "15": "3056",
                "16": "5060", "17": "4053", "18": "3057", "19": "4054", "20": "4055", "21": "5061"}

# Splatfest region
FESTIVALS = FESTIVALS_NA


def main():
    menu()


def menu():
    print("SplatNet 2 Shell")

    while True:
        print("\n1 - Profile")
        print("2 - Win/Loss of Last 50 Battles")
        print("3 - Results of a Specific Battle (Image + JSON)")
        print("4 - Results of Latest Battle (Image + JSON)")
        print("5 - Results of Latest Battle (Monitor) (Image + JSON)")
        print("6 - Results of All Battles (Image + JSON)")
        print("\x1b[31;1m{}\x1b[0m".format("0 - Exit"))
        option = input("\nclover@splatnet2:~$ ")

        if option == "1":
            get_profile()
        elif option == "2":
            get_win_loss()
        elif option == "3":
            get_battle_results()
        elif option == "4":
            get_battle_results(True)
        elif option == "5":
            get_battle_results_monitor()
        elif option == "6":
            get_all_battle_results()
        elif option == "0":
            sys.exit(0)
        elif option.lower() in ["c", "cookie"]:
            print(COOKIE)
            if os.name == "nt":
                os.system('set /p="{}" < nul | clip'.format(COOKIE))
            else:
                os.system("echo -n {} | {}".format(COOKIE, CLIP_CMD))
        elif option.lower() == "f":
            script_path = os.path.dirname(os.path.realpath(__file__))
            if os.name == "nt":
                subprocess.Popen("explorer {}".format(script_path))
        elif option.lower() == "fc":
            print(FRIEND_CODE)
            if os.name == "nt":
                os.system('set /p="{}" < nul | clip'.format(FRIEND_CODE))
            else:
                os.system("echo -n {} | {}".format(FRIEND_CODE, CLIP_CMD))
        elif len(re.split(";\s*", option)) > 1:
            for i in re.split(";\s*", option):
                direct_access(i)
        else:
            direct_access(option)


def countdown(timer):
    for i in range(timer, -1, -1):
        sys.stdout.write("Press Ctrl+C to exit. {} ".format(i))
        sys.stdout.flush()
        time.sleep(1)
        sys.stdout.write("\r")


def get_profile(auto=False):
    if not auto:
        profile_map = input("\nEnter the map ID you want in the image: ")  # 0 - 8, 6 included this time
        if profile_map == "":
            profile_map = "0"
        profile_color = input(
            "Enter the color you want for the background: ")  # Can be pink, green, yellow, purple, blue, or sun-yellow
        if profile_color == "":
            profile_color = "pink"
    else:
        profile_map = "0"
        profile_color = "pink"

    settings = {"stage": profile_map, "color": profile_color}
    image_url = get_image(URL_API_SHARE_PROFILE, settings)

    if auto:
        image = "{}/{} profile {}".format(SHARED_IMAGES, time.strftime("%Y-%m-%d %H-%M-%S"), image_url.split("/")[-1])
    else:
        image = "{} profile {}".format(time.strftime("%Y-%m-%d %H-%M-%S"), image_url.split("/")[-1])

    urllib.request.urlretrieve(image_url, image)


def get_win_loss(auto=False):
    image_url = get_image(URL_API_SHARE_WINLOSS)
    if auto:
        image = "{}/{} wl {}".format(SHARED_IMAGES, time.strftime("%Y-%m-%d %H-%M-%S"), image_url.split("/")[-1])
    else:
        image = "{} wl {}".format(time.strftime("%Y-%m-%d %H-%M-%S"), image_url.split("/")[-1])
    urllib.request.urlretrieve(image_url, image)

    get_results(True)


def get_challenge():
    challenge = input("Which challenge? ")

    image_url = get_image(URL_API_SHARE_CHALLENGE.format(challenge))
    urllib.request.urlretrieve(image_url, "{} {} {}".format(time.strftime("%Y-%m-%d %H-%M-%S"), challenge,
                                                            image_url.split("/")[-1]))


def get_battle_results(latest=False, battle_no=None, auto=False):
    results = get_results(True)

    battle_date = None
    if latest:
        battle_no = results[0]["battle_number"]
        print("Your latest battle was #{}".format(battle_no))
        image_url = get_image(URL_API_SHARE_BATTLE.format(battle_no))
        battle_date = datetime.datetime.fromtimestamp(int(results[0]["start_time"])).strftime("%Y-%m-%d %H-%M-%S")
        image = "{} {} {}".format(battle_date, battle_no, image_url.split("/")[-1])
        urllib.request.urlretrieve(image_url, image)
    else:
        if battle_no is None:
            battle_no = input("\nWhich battle do you want the results for? ")
            if battle_no == "":
                battle_no = results[0]["battle_number"]
                battle_date = datetime.datetime.fromtimestamp(int(results[0]["start_time"])).strftime(
                    "%Y-%m-%d %H-%M-%S")
        for i in range(len(results)):
            if results[i]["battle_number"] == battle_no:
                battle_date = datetime.datetime.fromtimestamp(int(results[i]["start_time"])).strftime(
                    "%Y-%m-%d %H-%M-%S")
                break
        if auto:
            image_url = get_image(URL_API_SHARE_BATTLE.format(battle_no))
            image = "{}/{} {} {}".format(SHARED_IMAGES, battle_date, battle_no, image_url.split("/")[-1])
        else:
            image_url = get_image(URL_API_SHARE_BATTLE.format(battle_no))
            image = "{} {} {}".format(battle_date, battle_no, image_url.split("/")[-1])
        image_url = get_image(URL_API_SHARE_BATTLE.format(battle_no))
        urllib.request.urlretrieve(image_url, image)

    url = URL_API_BATTLE_RESULTS.format(battle_no)
    battle = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
    battle_data = json.loads(battle.text)
    print("{:<5} {:<23} {:<18} {:<15} {}\x1b[0m{:<15}".format(battle_no, battle_data["stage"]["name"],
                                                              battle_data["game_mode"]["name"],
                                                              battle_data["rule"]["name"],
                                                              "\x1b[32m" if battle_data["my_team_result"][
                                                                                "name"] == "VICTORY" else "\x1b[31m",
                                                              battle_data["my_team_result"]["name"]))
    with open(os.path.join(JSON_FOLDER, os.path.join(BATTLES_FOLDER, "{} {}.json".format(battle_date, battle_no))), "w",
              encoding="utf8") as file:
        json.dump(battle_data, file, ensure_ascii=False)


def get_battle_results_monitor():
    results = get_results(True)
    last_battle = int(results[0]["battle_number"])
    first = last_battle + 1
    get_win_loss(True)
    get_profile(True)
    get_records()
    wins = 0
    losses = 0
    splatfest_wins = 0
    splatfest_losses = 0
    splatfest_power = 0
    mirror_matches = 0

    try:
        while True:
            results = get_results(True)
            if int(results[0]["battle_number"]) > last_battle:
                get_battle_results(False, results[0]["battle_number"], True)
                last_battle = int(results[0]["battle_number"])
                get_records()

                if results[0]["my_team_result"]["key"] == "victory":
                    wins += 1
                    if results[0]["game_mode"]["key"] in ["fes_solo", "fes_team"]:
                        if results[0]["my_team_fes_theme"]["key"] == results[0]["other_team_fes_theme"]["key"]:
                            mirror_matches += 1
                        else:
                            splatfest_wins += 1
                else:
                    losses += 1
                    if results[0]["game_mode"]["key"] in ["fes_solo", "fes_team"]:
                        if results[0]["my_team_fes_theme"]["key"] == results[0]["other_team_fes_theme"]["key"]:
                            mirror_matches += 1
                        else:
                            splatfest_losses += 1

                try:
                    if results[0]["fes_power"] != 0:
                        print("{:+4.1f}".format(results[0]["fes_power"] - splatfest_power))
                        splatfest_power = results[0]["fes_power"]
                except Exception as e:
                    print("Encountered exception when parsing Splatfest power:\n{}\n".format(e))
            else:
                pass
            countdown(90)
    except KeyboardInterrupt:
        print("\nDownloading win/loss and profile before stopping.")
        results = get_results(True)
        get_win_loss(True)
        get_profile(True)
        get_records()
        if results[0]["type"] == "league":
            print("Highest power was {}.".format(results[0]["max_league_point"]))
        if results[0]["type"] == "fes":
            if results[0]["max_fes_power"] != 0:
                print("Highest power was {}.".format(results[0]["max_fes_power"]))
            if results[0]["contribution_point_total"] != 0:
                print("Final clout was {}.".format(results[0]["contribution_point_total"]))
        battle_numbers(first, last_battle)
        print("{} win{} and {} loss{}.".format(wins, "s" if wins != 1 else "", losses, "es" if losses != 1 else ""))
        if splatfest_wins != 0 or splatfest_losses != 0:
            print("{} win{} and {} loss{} against the other Splatfest team.".format(splatfest_wins,
                                                                                    "" if splatfest_wins == 1 else "s",
                                                                                    splatfest_losses,
                                                                                    "" if splatfest_losses == 1 else "es"))
            print("{} mirror match{} against your Splatfest team.".format(mirror_matches,
                                                                          "" if mirror_matches == 1 else "es"))
    except Exception as e:
        print("Encountered exception when downloading results from SplatNet:\n{}\nStopping.".format(e))


def get_all_battle_results():
    results = get_results(True)

    for n in range(len(results)):
        battle_no = results[n]["battle_number"]
        get_battle_results(False, battle_no)


def get_results(download=False):
    r = requests.get(URL_API_RESULTS, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
    data = json.loads(r.text)

    try:
        results = data["results"]
    except KeyError:
        print("Bad cookie. Please check config.txt.")
        sys.exit(1)

    if download:
        with open(os.path.join(JSON_FOLDER, "{} results.json").format(
                datetime.datetime.fromtimestamp(int(results[0]["start_time"])).strftime("%Y-%m-%d %H-%M-%S")), "w",
                encoding="utf8") as file:
            json.dump(data, file, ensure_ascii=False)

    return results


def get_image(url, payload=None):
    response = requests.post(url, headers=app_head_share, cookies=dict(iksm_session=COOKIE), data=payload)
    data = json.loads(response.text)

    try:
        image_url = data["url"]
    except KeyError:
        print("Bad cookie. Please check config.txt.")
        sys.exit(1)

    return image_url


def get_records():
    response = requests.get(URL_API_RECORDS, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
    url = JSON_FOLDER
    with open(os.path.join(url, "{} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-1])),
              "w", encoding="utf8") as file:
        json.dump(json.loads(response.text), file, ensure_ascii=False)


def direct_access(option=None):
    if option is None:
        option = input("Type in what you want to retrieve: ")

    if option in ["help", "h", "?"]:
        help_reader()

    elif option in ["coop schedules", "coop", "salmon run", "salmon", "s"]:
        print("\nRetrieving Salmon Run Schedule.")
        url = URL_API_COOP_SCHEDULES
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-1]), "w",
                  encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
        parse_salmon_run_schedule(json.loads(response.text))
    elif option in ["coop results"]:
        print("\nRetrieving Salmon Run Results.")
        url = URL_API_COOP_RESULTS
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-1]), "w",
                  encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
    elif option in ["data stages", "stages", "stage data", "maps"]:
        print("\nRetrieving list of current stages.")
        url = URL_API_DATA_STAGES
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-2], url.split("/")[-1]),
                  "w", encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
    elif option in ["nickname and icon"]:
        pass  # Coming soon(tm)
    elif option in ["nickname", "name", "icon"]:
        nicknames_and_icons()
    elif option in ["update names", "update nicknames"]:
        print("\nUpdating nickname database.")
        update_nicknames()
    elif option in ["onlineshop merchandises", "merchandise", "shop", "store", "annie", "order", "buy gear"]:
        print("\nRetrieving available items at the SplatNet Gear Shop.")
        url = URL_API_ONLINESHOP_MERCH
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-2], url.split("/")[-1]),
                  "w",
                  encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
        parse_gear_images(json.loads(response.text))
        parse_splatnet_shop(json.loads(response.text))
    elif option in ["records"]:
        print("\nRetrieving current records.")
        url = URL_API_RECORDS
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-1]), "w",
                  encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
    elif option in ["records hero", "hero records", "hero"]:
        print("\nRetrieving Hero Mode records.")
        url = URL_API_RECORDS_HERO
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-2], url.split("/")[-1]),
                  "w", encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
    elif option in ["stage records", "stage stats"]:
        url = URL_API_RECORDS
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        parse_records_stages(json.loads(response.text)["records"])
    elif re.search("stage records \d+", option) is not None or re.search("stage stats \d+", option) is not None:
        url = URL_API_RECORDS
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        parse_records_stages(json.loads(response.text)["records"], re.search("\d+", option).group(0))
    elif option in ["weapon records", "weapon stats"]:
        url = URL_API_RECORDS
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        parse_records_weapons(json.loads(response.text)["records"])
    elif re.search("weapon records \d+", option) is not None or re.search("weapon stats \d+", option) is not None:
        url = URL_API_RECORDS
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        parse_records_weapons(json.loads(response.text)["records"], re.search("\d+", option).group(0))
    elif option in ["league stats"]:
        url = URL_API_RECORDS
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        parse_league_stats(json.loads(response.text)["records"])
    elif option in ["results"]:
        print("\nRetrieving latest battle results.")
        url = URL_API_RESULTS
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-1]), "w",
                  encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
    elif option in ["schedules", "schedule", "rotations", "rotation", "r"]:
        print("\nRetrieving current and upcoming stage rotations.")
        url = URL_API_SCHEDULES
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-1]), "w",
                  encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
        rotation = json.loads(response.text)
        parse_schedules(rotation, None)
    elif option in ["rotation next", "next rotation", "next"]:
        print("\nRetrieving upcoming stage rotations.")
        url = URL_API_SCHEDULES
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        rotation = json.loads(response.text)
        parse_schedules(rotation, None, 1)
    elif re.search("next \d+", option) is not None:
        print("\nRetrieving upcoming stage rotations.")
        url = URL_API_SCHEDULES
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        rotation = json.loads(response.text)
        parse_schedules(rotation, None, int(re.search("\d+", option).group(0)))
    elif option in ["now and later", "nnl"]:
        url = URL_API_SCHEDULES
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        rotation = json.loads(response.text)
        print("\x1b[34;1m{}\x1b[0m".format("\nRight now:"))
        parse_schedules(rotation, None)
        print("\x1b[34;1m{}\x1b[0m".format("\nNext:"))
        parse_schedules(rotation, None, 1)
        print("\x1b[34;1m{}\x1b[0m".format("\nLater:"))
        parse_schedules(rotation, None, 2)
    elif option in ["timeline"]:
        print("\nRetrieving your timeline.")
        url = URL_API_TIMELINE
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-1]), "w",
                  encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
        parse_gear_images(json.loads(response.text))
        parse_timeline(json.loads(response.text))
    elif option in ["festival", "splatfest", "fes", "fest"]:
        festival_access()
    elif option in ["league"]:
        league_board_access()
    elif option in ["league all", "l"]:
        league_board_access_all()
    elif re.search("league all \d+", option) is not None:
        league_board_access_all(re.search("\d+", option).group(0))
    elif option in ["league everything"]:
        download_league_everything()
    elif re.search("league everything \d+ \d+", option) is not None:
        download_league_everything(re.search("(\d+) (\d+)", option).group(1), re.search("(\d+) (\d+)", option).group(2))
    elif option in ["x rank", "rank x", "x"]:
        download_x_rankings()
    elif re.search("x rank \d+-\d+", option) is not None:
        download_x_rankings(re.search("\d+-\d+", option).group(0))
    elif option.lower() == "f":
        script_path = os.path.dirname(os.path.realpath(__file__))
        if os.name == "nt":
            subprocess.Popen("explorer {}".format(script_path))
    elif option in ["profile", "ranks"]:
        url = URL_API_RECORDS
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        profile_card(json.loads(response.text))
    elif option in ["profile tracks", "tracks profile"]:
        url = URL_API_RECORDS
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        profile_tracks(json.loads(response.text))
    elif option in ["patch notes"]:
        print("JP Notes: https://support.nintendo.co.jp/app/answers/detail/a_id/34680")
        print("US Notes: http://en-americas-support.nintendo.com/app/answers/detail/a_id/27028")
        print("US History: https://en-americas-support.nintendo.com/app/answers/detail/a_id/28658")
        if os.name == "nt":
            os.system("echo http://en-americas-support.nintendo.com/app/answers/detail/a_id/27028 | clip")
        else:
            os.system("echo http://en-americas-support.nintendo.com/app/answers/detail/a_id/27028 | {}".
                      format(CLIP_CMD))
    elif option in ["challenge"]:
        get_challenge()
    else:
        festival_access(option)


def festival_access(option=None):
    if option is None:
        option = input("What Splatfest data would you like to retrieve? ")

    if option in ["active"]:
        print("\nRetrieving active Splatfests.")
        url = URL_API_FEST_ACTIVE
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-2], url.split("/")[-1]),
                  "w", encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
        parse_active_splatfests(json.loads(response.text))
    elif option in ["pasts"]:
        print("\nRetrieving past Splatfests.")
        url = URL_API_FEST_PASTS
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-2], url.split("/")[-1]),
                  "w", encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
    elif option in ["votes"]:
        festival_id = input("Which Splatfest do you want to retrieve the votes for? ")
        parse_splatfest_votes(festival_id)
    elif re.search("votes \d+", option) is not None:
        festival_id = int(re.search("\d+", option).group(0))
        parse_splatfest_votes(festival_id)
    elif option in {"rankings"}:
        festival_id = input("Which Splatfest do you want to retrieve the rankings for? ")
        if festival_id in FESTIVALS:
            festival_id = FESTIVALS[festival_id]
        elif len(festival_id) != 4 or festival_id == "" or len(re.findall("[\D]", festival_id)) > 0:
            print("Invalid Splatfest ID. Please check it and try again.")
            return
        print("\nRetrieving Splatfest rankings.")
        url = URL_API_FEST_RANKINGS.format(festival_id)
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {} {} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-3], url.split("/")[-2],
                                            url.split("/")[-1]), "w", encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
    elif re.search("rankings \d+", option) is not None:
        festival_id = int(re.search("\d+", option).group(0))
        if str(festival_id) in FESTIVALS:
            festival_id = FESTIVALS[str(festival_id)]
        elif len(str(festival_id)) != 4 or str(festival_id) == "" or len(re.findall("[\D]", str(festival_id))) > 0:
            print("Invalid Splatfest ID. Please check it and try again.")
            return
        print("\nRetrieving Splatfest rankings.")
        url = URL_API_FEST_RANKINGS.format(festival_id)
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        with open("{} {} {} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-3], url.split("/")[-2],
                                            url.split("/")[-1]), "w", encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
    elif option in ["ranking average", "average power", "splatfest power"]:
        festival_id = input("Which Splatfest do you want to calculate statistics for the top 100 players for? ")
        if festival_id in FESTIVALS:
            festival_id = FESTIVALS[festival_id]
        elif len(festival_id) != 4 or festival_id == "" or len(re.findall("[\D]", festival_id)) > 0:
            print("Invalid Splatfest ID. Please check it and try again.")
            return
        url = URL_API_FEST_RANKINGS.format(festival_id)
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        try:
            parse_splatfest_rankings(json.loads(response.text))
        except Exception as e:
            print("Encountered exception when parsing Splatfest rankings:\n{}\n".format(e))
    elif option in ["splatfest power stats", "splatfest stats"]:
        print("Calculating Splatfest Power statistics.\r", end="")
        parse_splatfest_rankings_stats()
    elif option in ["fest results", "results", "result"]:
        parse_splatfest_results()
    elif re.search("fest results \d+", option) is not None:
        festival_id = int(re.search("\d+", option).group(0))
        parse_splatfest_results(festival_id)
    elif option in ["all festivals", "all fest", "all splatfest"]:
        print("\nRetrieving Splatfest data.")
        url = URL_API_SPLATOON2_INK_FEST_DATA
        response = requests.get(url)
        with open("{} {} {} {}".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-3], url.split("/")[-2],
                                       url.split("/")[-1]), "w", encoding="utf8") as file:
            json.dump(json.loads(response.text), file, ensure_ascii=False)
    elif option in ["colors", "splatfest colors"]:
        url = URL_API_FEST_PASTS
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        url = URL_API_FEST_ACTIVE
        response_active = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        try:
            parse_splatfest_colors(json.loads(response_active.text))
        except Exception as e:
            print("Encountered exception when parsing Splatfest colors:\n{}\n".format(e))
        try:
            parse_splatfest_colors(json.loads(response.text))
        except Exception as e:
            print("Encountered exception when parsing Splatfest colors:\n{}\n".format(e))
    elif option in ["na colors", "us colors"]:
        url = URL_API_SPLATOON2_INK_FEST_DATA
        response = requests.get(url)
        try:
            parse_splatfest_colors(json.loads(response.text)["na"])
        except Exception as e:
            print("Encountered exception when parsing Splatfest colors:\n{}\n".format(e))
    elif option in ["eu colors"]:
        url = URL_API_SPLATOON2_INK_FEST_DATA
        response = requests.get(url)
        try:
            parse_splatfest_colors(json.loads(response.text)["eu"])
        except Exception as e:
            print("Encountered exception when parsing Splatfest colors:\n{}\n".format(e))
    elif option in ["jp colors"]:
        url = URL_API_SPLATOON2_INK_FEST_DATA
        response = requests.get(url)
        try:
            parse_splatfest_colors(json.loads(response.text)["jp"])
        except Exception as e:
            print("Encountered exception when parsing Splatfest colors:\n{}\n".format(e))
    elif option in ["team images", "images", "splatfest images", "fest images"]:
        download_all_splatfest_images()
    elif option in ["events", "event battles"]:
        festival_id = input("Which Splatfest do you want to retrieve the events for? ")
        get_splatfest_events(festival_id)
    elif re.search("events \d+", option) is not None:
        festival_id = int(re.search("\d+", option).group(0))
        get_splatfest_events(festival_id)
    else:
        print("That's not an option.")


def league_board_access():
    league_code = input("Enter the date and time code to download: ")
    team_type = None

    if len(league_code) > 9:
        print("Invalid code. Check the URL and try again.")
        return

    if len(league_code) == 8:
        team_type = input("Enter 't' for a team or 'p' for a pair: ")  # How can I support getting both?

        if team_type.lower() != "t" and team_type.lower() != "p":
            print("That's not an option.")
            return

    region = input("Enter the region to retrieve (ALL, JP, US, or EU): ")  # I think ALL should get all 4.
    if region.lower() not in ["all", "jp", "us", "eu"]:
        print("That's not an option.")
        return

    if region.lower() == "all":
        download_league(league_code, team_type, "all")
        download_league(league_code, team_type, "jp")
        download_league(league_code, team_type, "us")
        download_league(league_code, team_type, "eu")

    download_league(league_code, team_type, region)


def league_board_access_all(league_code=None):
    if league_code is None:
        league_code = input("Enter the date and time code to download: ")

    if len(league_code) > 9:
        print("Invalid code. Check the URL and try again.")
        return

    download_league(league_code, "t", "all")
    download_league(league_code, "t", "jp")
    download_league(league_code, "t", "us")
    download_league(league_code, "t", "eu")
    download_league(league_code, "p", "all")
    download_league(league_code, "p", "jp")
    download_league(league_code, "p", "us")
    download_league(league_code, "p", "eu")


def download_league(league_code, team_type, region):
    league_code = league_code + team_type.upper()
    league_code = "{}/{}".format(league_code, region.upper())
    url = URL_API_LEAGUE_MATCH_RANKINGS.format(league_code)

    league_raw_data = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
    league_data = json.loads(league_raw_data.text)

    if "league_id" in league_data:
        league_date = datetime.datetime.fromtimestamp(int(league_data["start_time"])).strftime("%Y-%m-%d %H-%M-%S")
    else:
        print("Something went wrong ({} had no {} squads in League).".format(
            {"all": "all countries", "eu": "Europe", "jp": "Japan", "us": "North America"}.get(region, "some region"),
            {"t": "team", "p": "pair"}.get(team_type)))
        return

    filename = "{} {} {} {}.json".format(league_date, url.split("/")[-3], url.split("/")[-2], url.split("/")[-1])
    if os.path.exists(filename):
        print("{} already exists. Skipping the download.".format(os.path.basename(filename)))
        return

    with open(filename, "w", encoding="utf8") as file:
        json.dump(json.loads(league_raw_data.text), file, ensure_ascii=False)


def download_league_everything(start_code=None, end_code=None):
    if start_code is None or end_code is None:
        print("\nUsage: league everything <start code> <end code>.")
        print("Use 0 for both to automatically set start and end codes.")
        return

    if start_code == "0":
        try:
            start_code = max(glob.glob(os.path.join(JSON_FOLDER, LEAGUE_RANKINGS_FOLDER, "*")),
                             key=os.path.getctime)[63:71]
        except ValueError:
            start_code = "17072108"
        start_code = datetime.datetime(int("20" + start_code[0:2]), int(start_code[2:4]), int(start_code[4:6]),
                                       int(start_code[6:8]), 00) + datetime.timedelta(hours=2)
        start_code = time.strftime("%y%m%d%H", time.strptime(str(start_code), "%Y-%m-%d %H:%M:%S"))
    elif start_code == "00":
        start_code = "17072108"

    if end_code == "0":
        end_code = datetime.datetime.utcnow()
        if end_code.hour % 2 == 0:
            pass
        else:
            end_code = end_code - datetime.timedelta(hours=1)
            end_code = end_code.replace(minute=15)
        if end_code.minute >= 15:
            pass
        else:
            end_code = end_code - datetime.timedelta(hours=2)
        end_code = time.strftime("%y%m%d%H", time.strptime(str(end_code), "%Y-%m-%d %H:%M:%S.%f"))
    else:
        end_code = datetime.datetime(int("20" + end_code[0:2]), int(end_code[2:4]), int(end_code[4:6]),
                                     int(end_code[6:8]), 00) + datetime.timedelta(hours=2)
        end_code = time.strftime("%y%m%d%H", time.strptime(str(end_code), "%Y-%m-%d %H:%M:%S"))

    if start_code == end_code:
        new_results = datetime.datetime(int("20" + end_code[0:2]), int(end_code[2:4]), int(end_code[4:6]),
                                        int(end_code[6:8]), 15) + datetime.timedelta(
            hours=2) - datetime.datetime.utcnow()
        print("\nNo new league records to retrieve. Next results will be available in {}.".format(
            str(new_results).split(".")[0]))
        return

    if end_code < start_code:
        print("\nSomething went horribly, horribly wrong.")
        print("{} {}".format(end_code, start_code))
        return

    print("\nStarting at {} and stopping at {}.".format(start_code, end_code))

    i = 0
    while True:  # (2017,7,21,4,00) or 2017-07-21 4:00 AM were the first recorded league rankings
        rotation = datetime.timedelta(hours=i)
        current_rotation = datetime.datetime(int("20" + start_code[0:2]), int(start_code[2:4]), int(start_code[4:6]),
                                             int(start_code[6:8]), 00) + rotation
        league_code = time.strftime("%y%m%d%H", time.strptime(str(current_rotation), "%Y-%m-%d %H:%M:%S"))
        if league_code == end_code:
            break
        print(league_code + " " * 17)
        try:
            download_league(league_code, "t", "all")
            time.sleep(random.randint(3, 8))
            download_league(league_code, "t", "jp")
            time.sleep(random.randint(3, 8))
            download_league(league_code, "t", "us")
            time.sleep(random.randint(3, 8))
            download_league(league_code, "t", "eu")
            time.sleep(random.randint(3, 8))
            download_league(league_code, "p", "all")
            time.sleep(random.randint(3, 8))
            download_league(league_code, "p", "jp")
            time.sleep(random.randint(3, 8))
            download_league(league_code, "p", "us")
            time.sleep(random.randint(3, 8))
            download_league(league_code, "p", "eu")
        except KeyboardInterrupt:
            print("And we're up to date!")
            return
        except Exception as e:
            print("Encountered exception when downloading league rankings:\n{}\n".format(e))
            return
        i += 2
        try:
            next_rotation = datetime.timedelta(hours=i)
            next_current_rotation = datetime.datetime(int("20" + start_code[0:2]),
                                                      int(start_code[2:4]), int(start_code[4:6]),
                                                      int(start_code[6:8]), 00) + next_rotation
            next_league_code = time.strftime("%y%m%d%H", time.strptime(str(next_current_rotation), "%Y-%m-%d %H:%M:%S"))
            if next_league_code == end_code:
                break
            countdown(15)
        except KeyboardInterrupt:
            print("Stopping there.        ")
            return
        except Exception as e:
            print("Encountered exception when downloading league rankings:\n{}\n".format(e))
            return
    print("Stopping there.        ")
    return


def parse_salmon_run_schedule(salmon_run):
    for i in range(len(salmon_run["details"])):
        if time.time() > salmon_run["details"][i]["start_time"]:
            time_left = datetime.datetime.fromtimestamp(salmon_run["details"][i]["end_time"]) - datetime.datetime.now()
            print("You have {} left to finish your shift.".format(str(time_left).split(".")[0]))
        else:
            time_to_shift = datetime.datetime.fromtimestamp(
                salmon_run["details"][i]["start_time"]) - datetime.datetime.now()
            print("Next Salmon Run shift starts in {}. It starts at {}.".format(str(time_to_shift).split(".")[0],
                                                                                datetime.datetime.fromtimestamp(
                                                                                    salmon_run["details"][i][
                                                                                        "start_time"])))
            print("* You'll be heading to the \x1b[32m{}\x1b[0m for this one.".format(
                salmon_run["details"][i]["stage"]["name"]))
        print("* Your weapons will include: ", end="")
        weapons = []
        for j in salmon_run["details"][i]["weapons"]:
            if "coop_special_weapon" in j.keys():
                if j["id"] == "-1":
                    weapons.append("\x1b[32;1mRandom weapon\x1b[0m")
                elif j["id"] == "-2":
                    weapons.append("\x1b[33;1mGrizzco weapon\x1b[0m")
                else:
                    weapons.append("\x1b[33;1mRandom weapon\x1b[0m")
            else:
                weapons.append("\x1b[36;1m{}\x1b[0m".format(j["weapon"]["name"]))
        print(", ".join(weapons))


def parse_active_splatfests(active):
    if len(active["festivals"][0]["colors"]) > 0:
        if time.time() < active["festivals"][0]["times"]["start"]:
            print("There is a Splatfest coming soon!")
        elif time.time() < active["festivals"][0]["times"]["end"]:
            print("There is a Splatfest going on!")
        else:
            print("The Splatfest is over, but the results are still to come.")
    else:
        print("No Splatfests going on right now.")
        return

    alpha_name = "\x1b[38;2;{:03d};{:03d};{:03d}m{}\x1b[0m".format(
        round(float(active["festivals"][0]["colors"]["alpha"]["r"]) * 255),
        round(float(active["festivals"][0]["colors"]["alpha"]["g"]) * 255),
        round(float(active["festivals"][0]["colors"]["alpha"]["b"]) * 255),
        active["festivals"][0]["names"]["alpha_short"])
    bravo_name = "\x1b[38;2;{:03d};{:03d};{:03d}m{}\x1b[0m".format(
        round(float(active["festivals"][0]["colors"]["bravo"]["r"]) * 255),
        round(float(active["festivals"][0]["colors"]["bravo"]["g"]) * 255),
        round(float(active["festivals"][0]["colors"]["bravo"]["b"]) * 255),
        active["festivals"][0]["names"]["bravo_short"])

    if time.time() < active["festivals"][0]["times"]["start"]:
        print("The coming Splatfest is between {} and {}.".format(alpha_name, bravo_name))
        time_to_start = datetime.datetime.fromtimestamp(
            active["festivals"][0]["times"]["start"]) - datetime.datetime.now()
        print("Splatfest starts in {}.".format(str(time_to_start).split(".")[0]))
    if active["festivals"][0]["times"]["end"] > time.time() > active["festivals"][0]["times"]["start"]:
        print("The current Splatfest is between {} and {}.".format(alpha_name, bravo_name))
        time_left = datetime.datetime.fromtimestamp(active["festivals"][0]["times"]["end"]) - datetime.datetime.now()
        print("There's {} left in this Splatfest.".format(str(time_left).split(".")[0]))
    if time.time() > active["festivals"][0]["times"]["end"]:
        time_to_results = datetime.datetime.fromtimestamp(
            active["festivals"][0]["times"]["result"]) - datetime.datetime.now()
        print("Results for {} vs {} will be out in {}.".format(alpha_name, bravo_name,
                                                               str(time_to_results).split(".")[0]))

    download_splatfest_images(active)


def download_splatfest_images(splatfest):
    for i in range(len(splatfest["festivals"])):
        splatfest_folder = os.path.join(SPLATFEST_IMAGES_FOLDER, str(splatfest["festivals"][i]["festival_id"]))
        if not os.path.exists(splatfest_folder):
            os.makedirs(splatfest_folder)
        else:
            continue

        urllib.request.urlretrieve(URL_API_BASE.format(splatfest["festivals"][i]["images"]["panel"]),
                                   os.path.join(splatfest_folder,
                                                splatfest["festivals"][i]["images"]["panel"].split("/")[-1]))
        urllib.request.urlretrieve(URL_API_BASE.format(splatfest["festivals"][i]["images"]["alpha"]),
                                   os.path.join(splatfest_folder,
                                                splatfest["festivals"][i]["images"]["alpha"].split("/")[-1]))
        urllib.request.urlretrieve(URL_API_BASE.format(splatfest["festivals"][i]["images"]["bravo"]),
                                   os.path.join(splatfest_folder,
                                                splatfest["festivals"][i]["images"]["bravo"].split("/")[-1]))


def download_all_splatfest_images():
    url = URL_API_FEST_PASTS
    download_splatfest_images(
        json.loads(requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE)).text))


def parse_splatfest_rankings(rankings, auto=False):
    total_alpha = 0
    total_bravo = 0
    max_alpha = 0
    max_bravo = 0
    min_alpha = 3500
    min_bravo = 3500
    for i in range(len(rankings["rankings"]["alpha"])):
        try:
            total_alpha = total_alpha + int(rankings["rankings"]["alpha"][i]["score"])
            max_alpha = int(rankings["rankings"]["alpha"][i]["score"]) if int(
                rankings["rankings"]["alpha"][i]["score"]) > max_alpha else max_alpha
            min_alpha = int(rankings["rankings"]["alpha"][i]["score"]) if int(
                rankings["rankings"]["alpha"][i]["score"]) < min_alpha else min_alpha
        except KeyError:
            pass
        except Exception as e:
            print("Encountered exception when parsing Splatfest rankings for team Alpha:\n{}\n".format(e))
    for i in range(len(rankings["rankings"]["bravo"])):
        try:
            total_bravo = total_bravo + int(rankings["rankings"]["bravo"][i]["score"])
            max_bravo = int(rankings["rankings"]["bravo"][i]["score"]) if int(
                rankings["rankings"]["bravo"][i]["score"]) > max_bravo else max_bravo
            min_bravo = int(rankings["rankings"]["bravo"][i]["score"]) if int(
                rankings["rankings"]["bravo"][i]["score"]) < min_bravo else min_bravo
        except KeyError:
            pass
        except Exception as e:
            print("Encountered exception when parsing Splatfest rankings for team Bravo:\n{}\n".format(e))
    average_alpha = total_alpha / 100
    average_bravo = total_bravo / 100

    if not auto:
        print("Alpha's average was {}".format(average_alpha))
        print("Bravo's average was {}".format(average_bravo))
        print("Alpha ranged from {} to {}.".format(min_alpha, max_alpha))
        print("Bravo ranged from {} to {}.".format(min_bravo, max_bravo))
    else:
        return {"average_alpha": average_alpha, "min_alpha": min_alpha, "max_alpha": max_alpha,
                "average_bravo": average_bravo, "min_bravo": min_bravo, "max_bravo": max_bravo}


def parse_splatfest_rankings_stats():
    splatfest_folder = os.path.join(SPLATFEST_STATS_FOLDER, time.strftime("%Y-%m-%d %H-%M-%S"))

    try:
        os.makedirs(splatfest_folder)
    except IOError:
        print("Couldn't make a folder for the stats.")
        return

    stats_file_name = os.path.join(splatfest_folder, "splatfest-stats.csv")

    stats_array = []
    try:
        stats_array.append(["Alpha", "Alpha", "Alpha", "Alpha", "", "Bravo", "Bravo", "Bravo", "Bravo"])
        stats_array.append(["", "Min", "Max", "Average", "", "", "Min", "Max", "Average"])
    except IOError:
        print("Can't access the file. Make sure it's not open in Excel.")
        return

    url = URL_API_FEST_PASTS
    response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
    festival_pasts = json.loads(response.text)

    for i in FESTIVALS:
        url = URL_API_FEST_RANKINGS.format(FESTIVALS[i])
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
        if response.status_code == 404:
            continue
        rankings = json.loads(response.text)

        stats = parse_splatfest_rankings(rankings, True)

        for j in festival_pasts["festivals"]:
            if str(j["festival_id"]) == FESTIVALS[i]:
                alpha_name = j["names"]["alpha_short"]
                bravo_name = j["names"]["bravo_short"]
                break
        for k in festival_pasts["results"]:
            if str(k["festival_id"]) == FESTIVALS[i]:
                if k["summary"]["total"] == 0:
                    alpha_name += " (Won)"
                    break
                else:
                    bravo_name += " (Won)"
                    break

        rankings_array = [["Placement", alpha_name, "", "", "", bravo_name, ""]]
        for l in range(len(rankings["rankings"]["alpha"])):
            try:
                alpha_order = rankings["rankings"]["alpha"][l]["order"]
            except KeyError:
                alpha_order = ""
            try:
                alpha_score = rankings["rankings"]["alpha"][l]["score"]
                alpha_nickname = rankings["rankings"]["alpha"][l]["info"]["nickname"]
                alpha_weapon = rankings["rankings"]["alpha"][l]["info"]["weapon"]["name"]
            # This is to prevent Excel from attempting to calculate the value. Prepending a tab to the front
            # stops this from happening, and it looks fine in the spreadsheet, but the cell itself
            # will contain a tab, which isn't that great. Will have to investigate alternatives.
            # if alpha_nickname[0] in ["+","=","-"]:
            # alpha_nickname = "\t" + alpha_nickname
            except KeyError:
                alpha_score = "-"
                alpha_nickname = "-"
                alpha_weapon = "-"
            try:
                bravo_score = rankings["rankings"]["bravo"][l]["score"]
                bravo_nickname = rankings["rankings"]["bravo"][l]["info"]["nickname"]
                bravo_weapon = rankings["rankings"]["bravo"][l]["info"]["weapon"]["name"]
            # if bravo_nickname[0] in ["+","=","-"]:
            # bravo_nickname = "\t" + bravo_nickname
            except KeyError:
                bravo_score = "-"
                bravo_nickname = "-"
                bravo_weapon = "-"
            rankings_array.append(
                [alpha_order, alpha_score, alpha_nickname, alpha_weapon, "", bravo_score, bravo_nickname, bravo_weapon])

        with open(os.path.join(splatfest_folder, "splatfest rankings {} {}.csv".format(i, FESTIVALS[i])), "w",
                  newline="", encoding="utf8") as rankings_file:
            rankings_file.write("\ufeff")
            for ranking in rankings_array:
                csv.writer(rankings_file, quoting=csv.QUOTE_ALL).writerow(ranking)

        stats_array.append([alpha_name, stats["min_alpha"], stats["max_alpha"], stats["average_alpha"], "", bravo_name,
                            stats["min_bravo"], stats["max_bravo"], stats["average_bravo"]])

    with open(stats_file_name, "w", newline="", encoding="utf8") as rankings_file:
        for i in stats_array:
            csv.writer(rankings_file).writerow(i)

    print("See {} for CSV-formatted data.".format(stats_file_name))
    print("The top 100 rankings for each Splatfest are in '{}'.".format("splatfest # #### rankings.json"))
    if os.name == "nt":
        subprocess.Popen("explorer /select,{}".format(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                                   stats_file_name)))


def parse_splatfest_results(festival_id=None):
    if festival_id is None:
        festival_id = input("Which Splatfest do you want to retrieve the results for? ")

    if str(festival_id) in FESTIVALS:
        festival_id = FESTIVALS[str(festival_id)]
    elif len(str(festival_id)) != 4 or str(festival_id) == "" or len(re.findall("[\D]", str(festival_id))) > 0:
        print("Invalid Splatfest ID. Please check it and try again.")
        return

    url = URL_API_FEST_RESULT.format(festival_id)
    response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
    with open("{} {} {} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-3], url.split("/")[-2],
                                        url.split("/")[-1]), "w", encoding="utf8") as file:
        json.dump(json.loads(response.text), file, ensure_ascii=False)

    results = json.loads(response.text)

    alpha_name = "\x1b[38;2;{:03d};{:03d};{:03d}m{}\x1b[0m".format(
        round(float(results["festivals"][0]["colors"]["alpha"]["r"]) * 255),
        round(float(results["festivals"][0]["colors"]["alpha"]["g"]) * 255),
        round(float(results["festivals"][0]["colors"]["alpha"]["b"]) * 255),
        results["festivals"][0]["names"]["alpha_short"])
    bravo_name = "\x1b[38;2;{:03d};{:03d};{:03d}m{}\x1b[0m".format(
        round(float(results["festivals"][0]["colors"]["bravo"]["r"]) * 255),
        round(float(results["festivals"][0]["colors"]["bravo"]["g"]) * 255),
        round(float(results["festivals"][0]["colors"]["bravo"]["b"]) * 255),
        results["festivals"][0]["names"]["bravo_short"])

    if results["results"][0]["festival_version"] == 1:
        solo_key = "solo"
        solo_string = "Solo %      {:<12}{:<12}"
        team_key = "team"
        team_string = "Team %      {:<12}{:<12}"
    else:
        solo_key = "regular"
        solo_string = "Regular %   {:<12}{:<12}"
        team_key = "challenge"
        team_string = "Challenge % {:<12}{:<12}"

    alpha_votes = str(float(results["results"][0]["rates"]["vote"]["alpha"] / 100))
    alpha_votes += "0" if len(alpha_votes) < 5 else ""
    alpha_solo = str(float(results["results"][0]["rates"][team_key]["alpha"] / 100))
    alpha_solo += "0" if len(alpha_solo) < 5 else ""
    alpha_team = str(float(results["results"][0]["rates"][solo_key]["alpha"] / 100))
    alpha_team += "0" if len(alpha_team) < 5 else ""
    bravo_votes = str(float(results["results"][0]["rates"]["vote"]["bravo"] / 100))
    bravo_votes += "0" if len(bravo_votes) < 5 else ""
    bravo_solo = str(float(results["results"][0]["rates"][team_key]["bravo"] / 100))
    bravo_solo += "0" if len(bravo_solo) < 5 else ""
    bravo_team = str(float(results["results"][0]["rates"][solo_key]["bravo"] / 100))
    bravo_team += "0" if len(bravo_team) < 5 else ""

    if float(alpha_votes) > float(bravo_votes):
        alpha_votes = alpha_votes + "<"
        bravo_votes = " " + bravo_votes
    else:
        bravo_votes = ">" + bravo_votes

    if float(alpha_solo) > float(bravo_solo):
        alpha_solo = alpha_solo + "<"
        bravo_solo = " " + bravo_solo
    else:
        bravo_solo = ">" + bravo_solo

    if float(alpha_team) > float(bravo_team):
        alpha_team = alpha_team + "<"
        bravo_team = " " + bravo_team
    else:
        bravo_team = ">" + bravo_team

    alpha_total = 0
    bravo_total = 0

    print("\nSplatfest ID {} was between {} and {}.".format(results["festivals"][0]["festival_id"], alpha_name,
                                                            bravo_name))
    print("            {:<35} {:<12}".format(alpha_name, bravo_name))
    print("Votes       {:<12}{:<12}".format(alpha_votes, bravo_votes))
    print(solo_string.format(alpha_solo, bravo_solo))
    print(team_string.format(alpha_team, bravo_team))
    print("-" * 30)

    alpha_total = alpha_total + 1 if results["results"][0]["summary"]["vote"] == 0 else alpha_total
    bravo_total = bravo_total + 1 if results["results"][0]["summary"]["vote"] == 1 else bravo_total
    alpha_total = alpha_total + 1 if results["results"][0]["summary"][team_key] == 0 else alpha_total
    bravo_total = bravo_total + 1 if results["results"][0]["summary"][team_key] == 1 else bravo_total
    alpha_total = alpha_total + 1 if results["results"][0]["summary"][solo_key] == 0 else alpha_total
    bravo_total = bravo_total + 1 if results["results"][0]["summary"][solo_key] == 1 else bravo_total
    print("            {:<12} {:<12}".format(alpha_total, bravo_total))

    winner = alpha_name if results["results"][0]["summary"]["total"] == 0 else bravo_name
    winner_color = alpha_name[0:19] if results["results"][0]["summary"]["total"] == 0 else bravo_name[0:19]
    print("This Splatfest's winner was {}Team {}.".format(winner_color, winner))

    if alpha_total == 3 or bravo_total == 3:
        print("\x1b[1m{}\x1b[0m".format("And it was a sweep!"))


def parse_schedules(schedule, splatfest_active, rotation=0):
    if rotation < 0 or rotation > 11:
        rotation = 0

    colors = {"Regular Battle": "\x1b[38;2;025;215;025mRegular Battle\x1b[0m",
              "Ranked Battle": "\x1b[38;2;245;073;016mRanked Battle\x1b[0m",
              "League Battle": "\x1b[38;2;240;045;125mLeague Battle\x1b[0m"}

    if rotation == 0:
        print("{:<41}{:<17}\x1b[32m{}\x1b[0m and \x1b[32m{}\x1b[0m".format(
            colors.get(schedule["regular"][0]["game_mode"]["name"]), schedule["regular"][0]["rule"]["name"],
            schedule["regular"][0]["stage_a"]["name"], schedule["regular"][0]["stage_b"]["name"]))
        print("{:<41}{:<17}\x1b[32m{}\x1b[0m and \x1b[32m{}\x1b[0m".format(
            colors.get(schedule["gachi"][0]["game_mode"]["name"]), schedule["gachi"][0]["rule"]["name"],
            schedule["gachi"][0]["stage_a"]["name"], schedule["gachi"][0]["stage_b"]["name"]))
        print("{:<41}{:<17}\x1b[32m{}\x1b[0m and \x1b[32m{}\x1b[0m".format(
            colors.get(schedule["league"][0]["game_mode"]["name"]), schedule["league"][0]["rule"]["name"],
            schedule["league"][0]["stage_a"]["name"], schedule["league"][0]["stage_b"]["name"]))
        time_left = datetime.datetime.fromtimestamp(schedule["regular"][0]["end_time"]) - datetime.datetime.now()
        print("There's {} left in this rotation.".format(str(time_left).split(".")[0]))
    else:
        print("{:<41}{:<17}\x1b[32m{}\x1b[0m and \x1b[32m{}\x1b[0m".format(
            colors.get(schedule["regular"][rotation]["game_mode"]["name"]),
            schedule["regular"][rotation]["rule"]["name"], schedule["regular"][rotation]["stage_a"]["name"],
            schedule["regular"][rotation]["stage_b"]["name"]))
        print("{:<41}{:<17}\x1b[32m{}\x1b[0m and \x1b[32m{}\x1b[0m".format(
            colors.get(schedule["gachi"][rotation]["game_mode"]["name"]), schedule["gachi"][rotation]["rule"]["name"],
            schedule["gachi"][rotation]["stage_a"]["name"], schedule["gachi"][rotation]["stage_b"]["name"]))
        print("{:<41}{:<17}\x1b[32m{}\x1b[0m and \x1b[32m{}\x1b[0m".format(
            colors.get(schedule["league"][rotation]["game_mode"]["name"]), schedule["league"][rotation]["rule"]["name"],
            schedule["league"][rotation]["stage_a"]["name"], schedule["league"][rotation]["stage_b"]["name"]))
        time_till_start = datetime.datetime.fromtimestamp(
            schedule["regular"][rotation]["start_time"]) - datetime.datetime.now()
        print("There's {} until this rotation. It starts at {}.".format(str(time_till_start).split(".")[0],
                                                                        datetime.datetime.fromtimestamp(
                                                                            schedule["regular"][rotation][
                                                                                "start_time"]).time()))


def parse_gear_images(data):
    if "coop" in data:
        download_gear_image(data["coop"]["reward_gear"]["gear"]["image"])

    if "merchandises" in data:
        for i in range(len(data["merchandises"])):
            download_gear_image(data["merchandises"][i]["gear"])


def download_gear_image(gear_data):
    headgear_folder = os.path.join(GEAR_IMAGES_FOLDER, "headgear")
    clothes_folder = os.path.join(GEAR_IMAGES_FOLDER, "clothes")
    shoes_folder = os.path.join(GEAR_IMAGES_FOLDER, "shoes")
    filename = "{} - {} - {}".format(gear_data["id"], gear_data["name"], gear_data["image"].split('/')[-1])

    for gear_folder in [headgear_folder, clothes_folder, shoes_folder]:
        if not os.path.exists(gear_folder):
            os.makedirs(gear_folder)

    if gear_data["kind"] == "head":
        full_filename = os.path.join(headgear_folder, filename)
    elif gear_data["kind"] == "clothes":
        full_filename = os.path.join(clothes_folder, filename)
    elif gear_data["kind"] == "shoes":
        full_filename = os.path.join(shoes_folder, filename)
    else:
        full_filename = os.path.join(GEAR_IMAGES_FOLDER, "{} - {}".format(gear_data["kind"], filename))

    image_url = URL_API_BASE.format(gear_data["image"])

    try:
        urllib.request.urlretrieve(image_url, full_filename)
    except:
        print("This is an old battle with obsolete gear URLs.")
        return


def battle_numbers(begin, end):
    numbers = []
    for i in range(begin, end + 1):
        numbers.append(i)
    print("#", end="")
    print(", ".join(map(str, numbers)))


def parse_splatfest_colors(colors):
    for i in range(len(colors["festivals"])):
        colored_string = "\x1b[38;2;{};{};{}m{}\x1b[0m"

        alpha_color = colored_string.format(round(float(colors["festivals"][i]["colors"]["alpha"]["r"]) * 255),
                                            round(float(colors["festivals"][i]["colors"]["alpha"]["g"]) * 255),
                                            round(float(colors["festivals"][i]["colors"]["alpha"]["b"]) * 255), "{}")
        alpha_named_color = alpha_color.format(colors["festivals"][i]["names"]["alpha_short"])
        alpha_block = alpha_color.format("█" * 30)

        bravo_color = colored_string.format(round(float(colors["festivals"][i]["colors"]["bravo"]["r"]) * 255),
                                            round(float(colors["festivals"][i]["colors"]["bravo"]["g"]) * 255),
                                            round(float(colors["festivals"][i]["colors"]["bravo"]["b"]) * 255), "{}")
        bravo_named_color = bravo_color.format(colors["festivals"][i]["names"]["bravo_short"])
        bravo_block = bravo_color.format("█" * 30)

        neutral_color = colored_string.format(round(float(colors["festivals"][i]["colors"]["middle"]["r"]) * 255),
                                              round(float(colors["festivals"][i]["colors"]["middle"]["g"]) * 255),
                                              round(float(colors["festivals"][i]["colors"]["middle"]["b"]) * 255), "{}")
        neutral_named_color = neutral_color.format("Neutral")
        neutral_block = neutral_color.format("█" * 30)

        if len(colors["festivals"]) > 1:
            print("\nSplatfest #{} [\x1b[34;1m{}\x1b[0m] ({} vs {})".format(len(colors["festivals"]) - i,
                                                                            colors["festivals"][i]["festival_id"],
                                                                            alpha_named_color, bravo_named_color))
        else:
            print("\nLatest Splatfest [\x1b[34;1m{}\x1b[0m] ({} vs {})".format(colors["festivals"][i]["festival_id"],
                                                                               alpha_named_color, bravo_named_color))

        for j in [("alpha", alpha_named_color, alpha_block), ("bravo", bravo_named_color, bravo_block),
                  ("middle", neutral_named_color, neutral_block)]:
            print("{}'s colors:".format(j[1]))
            print("{}, {}, {}".format(int(round(float(colors["festivals"][i]["colors"][j[0]]["r"]) * 255)),
                                      int(round(float(colors["festivals"][i]["colors"][j[0]]["g"]) * 255)),
                                      int(round(float(colors["festivals"][i]["colors"][j[0]]["b"]) * 255))))
            print('#{:02X}{:02X}{:02X} {}'.format(int(round(float(colors["festivals"][i]["colors"][j[0]]["r"]) * 255)),
                                                  int(round(float(colors["festivals"][i]["colors"][j[0]]["g"]) * 255)),
                                                  int(round(float(colors["festivals"][i]["colors"][j[0]]["b"]) * 255)),
                                                  j[2]))


def parse_splatfest_votes(festival_id):
    if str(festival_id) in FESTIVALS:
        festival_id = FESTIVALS[str(festival_id)]
    elif len(str(festival_id)) != 4 or str(festival_id) == "" or len(re.findall("[\D]", str(festival_id))) > 0:
        print("\nInvalid Splatfest ID. Please check it and try again.")
        return

    url = URL_API_FEST_VOTES.format(festival_id)
    response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
    with open("{} {} {} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-3], url.split("/")[-2],
                                        url.split("/")[-1]), "w", encoding="utf8") as file:
        votes = json.loads(response.text)
        json.dump(votes, file, ensure_ascii=False)
    if "votes" in votes:
        print("\n{} vote{} for Alpha and {} vote{} for Bravo.".format(len(votes["votes"]["alpha"]),
                                                                      "" if len(votes["votes"]["alpha"]) == 1 else "s",
                                                                      len(votes["votes"]["bravo"]),
                                                                      "" if len(votes["votes"]["bravo"]) == 1 else "s"))
    else:
        print("\nDid not receive votes from SplatNet. Got this instead:\n{}\n".format(votes))


def parse_splatnet_shop(items):
    print("Here are the items in the store right now:")
    for idx, i in enumerate(items["merchandises"], start=1):
        if idx != 1:
            print("-" * 30)
        print("[\x1b[33;1m{}\x1b[0m] {} by {} ({})".format(idx, i["gear"]["name"], i["gear"]["brand"]["name"],
                                                           i["gear"]["kind"]))
        print("{} with \x1b[32m{}\x1b[0m slot{}. ({}).".format(i["skill"]["name"], i["gear"]["rarity"] + 1,
                                                               "s" if i["gear"]["rarity"] + 1 > 1 else "",
                                                               i["gear"]["brand"]["frequent_skill"]["name"]))
        print("{} coins. {} left.".format(i["price"], str(
            datetime.datetime.fromtimestamp(i["end_time"]) - datetime.datetime.now()).split(".")[0]))

    if len(items) > 1:
        print("\nHere's the item you've ordered:")
        print("{} by {} ({})".format(items["ordered_info"]["gear"]["name"],
                                     items["ordered_info"]["gear"]["brand"]["name"],
                                     items["ordered_info"]["gear"]["kind"]))
        print("{} with {} slot{}.".format(items["ordered_info"]["skill"]["name"],
                                          items["ordered_info"]["gear"]["rarity"] + 1,
                                          "s" if items["ordered_info"]["gear"]["rarity"] + 1 > 1 else ""))
        print("{} coins.".format(items["ordered_info"]["price"]))

    item_number = input("\nWant to order something? (1 - 6, or 0 to exit) ")
    if item_number == "0":
        return
    elif item_number in ["1", "2", "3", "4", "5", "6"]:
        try:
            print("{} with {}".format(items["merchandises"][int(item_number) - 1]["gear"]["name"],
                                      items["merchandises"][int(item_number) - 1]["skill"]["name"]))
        except Exception as e:
            print("Encountered exception when parsing SplatNet Shop data:\n{}\n".format(e))
            return
        confirm_order = input("Is that right? (Y/n) ")
        if len(confirm_order) == 0 or confirm_order[0].lower() != "n":
            print("Ordering that.")
            item = items["merchandises"][int(item_number) - 1]
            url = URL_API_ONLINESHOP_ORDER.format(item["id"])
            response = requests.post(url, headers=app_head_shop, cookies=dict(iksm_session=COOKIE))
        else:
            print("Canceled the order.")
            return

        if json.loads(response.text)["code"] == "ONLINE_SHOP_ALREADY_ORDERED":
            print("You already have the following item ordered:")
            print(
                "{} with {}".format(items["ordered_info"]["gear"]["name"], items["ordered_info"]["skill"]["name"]))
            confirm_override = input("Would you like to order anyway and replace that? (y/N) ")
            if len(confirm_override) == 0 or confirm_override[0].lower() != "y":
                print("Canceled the order.")
                return
            else:
                print("Ordering with override.")
                url = URL_API_ONLINESHOP_ORDER.format(item["id"])
                payload = {"override": 1}
                requests.post(url, headers=app_head_shop, cookies=dict(iksm_session=COOKIE), data=payload)
        else:
            print("Order placed successfully.")
    else:
        print("That's not an option.")


def parse_timeline(timeline):
    try:
        if len(timeline["weapon_availability"]["availabilities"]) > 0:
            print("\nThere are new weapons available!")
            for idx, i in enumerate(timeline["weapon_availability"]["availabilities"]):
                if idx != 0:
                    print("{}".format("-" * 30))
                print(i["weapon"]["name"])
                print("Sub: {}, Special: {}".format(i["weapon"]["sub"]["name"], i["weapon"]["special"]["name"]))
                print("Weapon ID #{}".format(i["weapon"]["id"]))
                print("Officially released {}".format(str(datetime.datetime.fromtimestamp(i["release_time"]))))
                filename = os.path.join(os.path.join(WEAPON_IMAGES_FOLDER, "main"),
                                        "{} - {} - {}".format(i["weapon"]["id"], i["weapon"]["name"],
                                                              i["weapon"]["image"].split("/")[-1]))
                image_url = URL_API_BASE.format(i["weapon"]["image"])
                urllib.request.urlretrieve(image_url, filename)
    except Exception as e:
        print("Encountered exception when parsing timeline:\n{}\n".format(e))
    try:
        if timeline["udemae"]["importance"] > -1:
            print("\nCongratulations on your new rank in \x1b[33;1m{}\x1b[0m!".format(
                timeline["udemae"]["stat"]["rule"]["name"]))
            print("You went from {}{} to {}{}!".format(
                timeline["udemae"]["stat"]["player_result"]["player"]["udemae"]["name"],
                timeline["udemae"]["stat"]["player_result"]["player"]["udemae"]["s_plus_number"] if
                timeline["udemae"]["stat"]["player_result"]["player"]["udemae"]["s_plus_number"] is not None else "",
                timeline["udemae"]["stat"]["udemae"]["name"],
                timeline["udemae"]["stat"]["udemae"]["s_plus_number"] if timeline["udemae"]["stat"]["udemae"][
                                                                             "s_plus_number"] is not None else ""))
    except Exception as e:
        print("Encountered exception when parsing timeline:\n{}\n".format(e))


def nicknames_and_icons():
    principal_id = input("\nWhat's the principal ID? ")
    principal_ids = principal_id.split(" ")

    for i in principal_ids:
        if len(i) != 16:
            print("Invalid principal ID.")
            return

    url = URL_API_NICKNAME_ICON
    response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE),
                            params={"id": principal_ids})
    nickname_and_icons = json.loads(response.text)
    for i in nickname_and_icons["nickname_and_icons"]:
        if len(principal_ids) > 1:
            print("{} belongs to {}.".format(i["nsa_id"], i["nickname"]))
        else:
            print("That ID belongs to {}.".format(i["nickname"]))
        print("Here's their picture: {}".format(i["thumbnail_url"]))


def update_nicknames():
    for names in ["ids.json"]:
        with open(names, "r+", encoding="utf8") as id_file:
            id_data = json.load(id_file)["users"]

        principal_ids = list(id_data)

        url = URL_API_NICKNAME_ICON
        response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE),
                                params={"id": principal_ids})
        nickname_and_icons = json.loads(response.text)

        for i in nickname_and_icons["nickname_and_icons"]:
            if i["nickname"] not in id_data[i["nsa_id"]]["names"]:
                print("Found a new name for {}. ({})".format(id_data[i["nsa_id"]]["nickname"], i["nickname"]))
                id_data[i["nsa_id"]]["names"].append(i["nickname"])

        with open(names, "r+", encoding="utf8") as id_file:
            json.dump({"users": id_data}, id_file, indent=4, ensure_ascii=False)


def parse_records_stages(records, stage=None):
    sz_wins = 0
    sz_losses = 0
    sz_percent = 0.0
    tc_wins = 0
    tc_losses = 0
    tc_percent = 0.0
    rm_wins = 0
    rm_losses = 0
    rm_percent = 0.0
    cb_wins = 0
    cb_losses = 0
    cb_percent = 0.0

    stage_records = records["stage_stats"]

    print("")
    if stage is not None:
        try:
            print_record_stage(stage_records[stage])
        except KeyError:
            print("You haven't played on that stage, or it doesn't exist.")
    else:
        for idx, i in enumerate(sorted(stage_records, key=int)):
            sz_wins = sz_wins + stage_records[i]["area_win"]
            sz_losses = sz_losses + stage_records[i]["area_lose"]
            if stage_records[i]["area_win"] == 0 and stage_records[i]["area_lose"] == 0:
                sz_percent = -1.0
            else:
                sz_percent = stage_records[i]["area_win"] / (
                        stage_records[i]["area_win"] + stage_records[i]["area_lose"])

            tc_wins = tc_wins + stage_records[i]["yagura_win"]
            tc_losses = tc_losses + stage_records[i]["yagura_lose"]
            if stage_records[i]["yagura_win"] == 0 and stage_records[i]["yagura_lose"] == 0:
                tc_percent = -1.0
            else:
                tc_percent = stage_records[i]["yagura_win"] / (
                        stage_records[i]["yagura_win"] + stage_records[i]["yagura_lose"])

            rm_wins = rm_wins + stage_records[i]["hoko_win"]
            rm_losses = rm_losses + stage_records[i]["hoko_lose"]
            if stage_records[i]["hoko_win"] == 0 and stage_records[i]["hoko_lose"] == 0:
                rm_percent = -1.0
            else:
                rm_percent = stage_records[i]["hoko_win"] / (
                        stage_records[i]["hoko_win"] + stage_records[i]["hoko_lose"])

            cb_wins = cb_wins + stage_records[i]["asari_win"]
            cb_losses = cb_losses + stage_records[i]["asari_lose"]
            if stage_records[i]["asari_win"] == 0 and stage_records[i]["asari_lose"] == 0:
                cb_percent = -1.0
            else:
                cb_percent = stage_records[i]["asari_win"] / (
                        stage_records[i]["asari_win"] + stage_records[i]["asari_lose"])

            print_record_stage(stage_records[i])
            print("{}".format("-" * 32))

        print("Totals:")
        print("SZ Wins: {:<4} Losses: {:<4}".format(sz_wins, sz_losses))
        print("TC Wins: {:<4} Losses: {:<4}".format(tc_wins, tc_losses))
        print("RM Wins: {:<4} Losses: {:<4}".format(rm_wins, rm_losses))
        print("CB Wins: {:<4} Losses: {:<4}".format(cb_wins, cb_losses))
        print("Wins: {:<7} Losses: {:<}".format(records["win_count"], records["lose_count"]))


def print_record_stage(stage_stats):
    print("\x1b[34;1m{}\x1b[0m (#{})".format(stage_stats["stage"]["name"], stage_stats["stage"]["id"]))
    print("SZ Wins: {:<4} Losses: {:<4}".format(stage_stats["area_win"], stage_stats["area_lose"]))
    print("TC Wins: {:<4} Losses: {:<4}".format(stage_stats["yagura_win"], stage_stats["yagura_lose"]))
    print("RM Wins: {:<4} Losses: {:<4}".format(stage_stats["hoko_win"], stage_stats["hoko_lose"]))
    print("CB Wins: {:<4} Losses: {:<4}".format(stage_stats["asari_win"], stage_stats["asari_lose"]))
    print("Last played {}".format(str(datetime.datetime.fromtimestamp(stage_stats["last_play_time"]))))


def profile_card(records):
    max_rank = -1
    max_rank_name = {0: "C-", 1: "C", 2: "C+", 3: "B-", 4: "B", 5: "B+", 6: "A-", 7: "A", 8: "A+", 9: "S", 10: "S+"}
    for mode in ["clam", "rainmaker", "tower", "zones"]:
        if records["records"]["player"]["udemae_" + mode]["number"] > max_rank:
            max_rank = records["records"]["player"]["udemae_" + mode]["number"]

    sz_rank = "-" if records["records"]["player"]["udemae_zones"]["name"] is None else \
        records["records"]["player"]["udemae_zones"]["name"]
    sz_rank_number = "" if records["records"]["player"]["udemae_zones"]["s_plus_number"] is None else \
        records["records"]["player"]["udemae_zones"]["s_plus_number"]
    tc_rank = "-" if records["records"]["player"]["udemae_tower"]["name"] is None else \
        records["records"]["player"]["udemae_tower"]["name"]
    tc_rank_number = "" if records["records"]["player"]["udemae_tower"]["s_plus_number"] is None else \
        records["records"]["player"]["udemae_tower"]["s_plus_number"]
    rm_rank = "-" if records["records"]["player"]["udemae_rainmaker"]["name"] is None else \
        records["records"]["player"]["udemae_rainmaker"]["name"]
    rm_rank_number = "" if records["records"]["player"]["udemae_rainmaker"]["s_plus_number"] is None else \
        records["records"]["player"]["udemae_rainmaker"]["s_plus_number"]
    cb_rank = "-" if records["records"]["player"]["udemae_clam"]["name"] is None else \
        records["records"]["player"]["udemae_clam"]["name"]
    cb_rank_number = "" if records["records"]["player"]["udemae_clam"]["s_plus_number"] is None else \
        records["records"]["player"]["udemae_clam"]["s_plus_number"]

    # Will I ever get far enough to have to deal with star ranks? Who knows.
    print("\n{} - Level {} - Rank {}".format(records["records"]["player"]["nickname"],
                                             records["records"]["player"]["player_rank"], max_rank_name.get(max_rank)))
    print("Splat Zones:    {} {}".format(sz_rank, sz_rank_number))
    print("Tower Control:  {} {}".format(tc_rank, tc_rank_number))
    print("Rainmaker:      {} {}".format(rm_rank, rm_rank_number))
    print("Clam Blitz:     {} {}".format(cb_rank, cb_rank_number))
    print("Turf Inked: {}p - {}".format(records["challenges"]["total_paint_point"],
                                        records["challenges"]["archived_challenges"][-1]["name"]))
    print("{}/{}/{}/{}p".format(records["records"]["player"]["weapon"]["name"],
                                records["records"]["player"]["weapon"]["sub"]["name"],
                                records["records"]["player"]["weapon"]["special"]["name"],
                                records["records"]["weapon_stats"][records["records"]["player"]["weapon"]["id"]][
                                    "total_paint_point"]))

    head_subs = []
    clothes_subs = []
    shoes_subs = []
    for ability in records["records"]["player"]["head_skills"]["subs"]:
        head_subs.append(ability["name"])
    for ability in records["records"]["player"]["clothes_skills"]["subs"]:
        clothes_subs.append(ability["name"])
    for ability in records["records"]["player"]["shoes_skills"]["subs"]:
        shoes_subs.append(ability["name"])

    print("{}/{} + {}".format(records["records"]["player"]["head"]["name"],
                              records["records"]["player"]["head_skills"]["main"]["name"], "/".join(head_subs)))
    print("{}/{} + {}".format(records["records"]["player"]["clothes"]["name"],
                              records["records"]["player"]["clothes_skills"]["main"]["name"], "/".join(clothes_subs)))
    print("{}/{} + {}".format(records["records"]["player"]["shoes"]["name"],
                              records["records"]["player"]["shoes_skills"]["main"]["name"], "/".join(shoes_subs)))


def profile_tracks(records):
    level = records["records"]["player"]["player_rank"]
    if records["records"]["player"]["star_rank"] > 0:
        level += "★{}".format(records["records"]["player"]["star_rank"])

    modes = ["_zones", "_tower", "_rainmaker", "_clam"]
    ranks = ["", "", "", ""]

    for i in range(4):
        ranks[i] = records["records"]["player"]["udemae" + modes[i]]["name"]

        if ranks[i] == "S+":
            ranks[i] += str(records["records"]["player"]["udemae" + modes[i]]["s_plus_number"])

        if ranks[i] is None:
            ranks[i] = "-"

    print("\nNickname: {}".format(records["records"]["player"]["nickname"]))
    print("Level: {}".format(level))
    print("SZ: {}".format(ranks[0]))
    print("TC: {}".format(ranks[1]))
    print("RM: {}".format(ranks[2]))
    print("CB: {}".format(ranks[3]))
    print("Wins: {}".format(records["records"]["win_count"]))
    print("Losses: {}".format(records["records"]["lose_count"]))
    print("Win %: {:02.2f}%".format(
        records["records"]["win_count"] / (records["records"]["win_count"] + records["records"]["lose_count"]) * 100))


def parse_records_weapons(records, weapon=None):
    print("")
    if weapon is None:
        for idx, i in enumerate(sorted(records["weapon_stats"], key=int)):
            if idx != 0:
                print("{}".format("-" * 30))
            print_record_weapon(records["weapon_stats"][i])
    else:
        try:
            print_record_weapon(records["weapon_stats"][weapon])
        except KeyError:
            print("You haven't played with that weapon, or it doesn't exist.")


def print_record_weapon(weapon_record):
    print("\x1b[34;1m{}\x1b[0m (#{})".format(weapon_record["weapon"]["name"], weapon_record["weapon"]["id"]))
    print("{}/{}".format(weapon_record["weapon"]["sub"]["name"], weapon_record["weapon"]["special"]["name"]))
    print("Wins: {:<8} Losses: {:<5}".format(weapon_record["win_count"], weapon_record["lose_count"]))
    print("Freshness: {:<6} Max: {:<6}".format(weapon_record["win_meter"], weapon_record["max_win_meter"]))
    print("{}p turf inked".format(weapon_record["total_paint_point"]))
    print("Last used {}".format(str(datetime.datetime.fromtimestamp(weapon_record["last_use_time"]))))


def download_x_rankings(season=None):
    if season is None:
        season = input("Enter the season's start date like YYYY-MM: ")

    if len(season) != 7:
        print("Invalid code. Check the URL and try again.")
        return

    season_code_begin = time.strftime("%y%m%d", time.gmtime(time.mktime(
        time.strptime(str(datetime.datetime(year=int(season[0:4]), month=int(season[5:7]), day=1)),
                      "%Y-%m-%d %H:%M:%S"))))
    end_delta = relativedelta(months=+1)
    season_code_end = time.strftime("%y%m%d", time.gmtime(time.mktime(
        time.strptime(str(datetime.datetime(year=int(season[0:4]), month=int(season[5:7]), day=1) + end_delta),
                      "%Y-%m-%d %H:%M:%S"))))

    url = URL_API_X_POWER_RANKING_SUMMARY.format(season_code_begin, season_code_end)

    response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
    season_data = json.loads(response.text)

    mode_time = time.strftime("%Y-%m-%d %H-%M-%S")
    base_directory = os.path.join(JSON_FOLDER, X_RANKINGS_FOLDER)
    rankings_folder = os.path.join(base_directory, "{} {}".format(mode_time, url.split("/")[-2]))
    try:
        os.makedirs(rankings_folder)
    except IOError:
        print("Couldn't make a folder for the stats.")
        return

    try:
        datetime.datetime.fromtimestamp(int(season_data["rainmaker"]["start_time"])).strftime("%Y-%m-%d %H-%M-%S")
    except ValueError:
        print("Something bad happened.")
        return
    with open(os.path.join(rankings_folder,
                           "{} {} {} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-3],
                                                     url.split("/")[-2], url.split("/")[-1])), "w",
              encoding="utf8") as file:
        json.dump(season_data, file, ensure_ascii=False)

    print("")
    for i in ["splat_zones", "tower_control", "rainmaker", "clam_blitz"]:
        try:
            print("{}".format(season_data[i]["rule"]["name"]))
            print("#1 - \x1b[34;1m{}\x1b[0m @ \x1b[33;1m{}\x1b[0m with the \x1b[32;1m{}\x1b[0m ".format(
                season_data[i]["top_rankings"][0]["name"], str(season_data[i]["top_rankings"][0]["x_power"]),
                season_data[i]["top_rankings"][0]["weapon"]["name"]))
        except (IndexError, KeyError):
            print("No data yet.")

    rankings = [[], [], [], []]

    if season_data["rainmaker"]["status"] == "calculated":
        for idx, i in enumerate(["splat_zones", "tower_control", "rainmaker", "clam_blitz"]):
            for j in range(1, 6):
                url = URL_API_X_POWER_RANKING_PAGES.format(season_code_begin, season_code_end, i)
                response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE),
                                        params={"page": j})
                page_data = json.loads(response.text)
                with open(os.path.join(rankings_folder,
                                       "{} {} {} {} {}.json".format(mode_time, url.split("/")[-3], url.split("/")[-2],
                                                                    i, j)), "w", encoding="utf8") as file:
                    json.dump(page_data, file, ensure_ascii=False)
                rankings[idx] += page_data["top_rankings"]
    else:
        return

    formatted_rankings = [
        ["", "Splat Zones", "", "", "", "Tower Control", "", "", "", "Rainmaker", "", "", "", "Clam Blitz"],
        ["Rank", "Name", "Power", "Weapon", "", "Name", "Power", "Weapon", "", "Name", "Power", "Weapon", "", "Name",
         "Power", "Weapon"]]
    sz_rankings = rankings[0]
    tc_rankings = rankings[1]
    rm_rankings = rankings[2]
    cb_rankings = rankings[3]

    for i in range(0, 500):
        formatted_rankings.append([sz_rankings[i]["rank"], sz_rankings[i]["name"], sz_rankings[i]["x_power"],
                                   sz_rankings[i]["weapon"]["name"], "",
                                   tc_rankings[i]["name"], tc_rankings[i]["x_power"], tc_rankings[i]["weapon"]["name"],
                                   "",
                                   rm_rankings[i]["name"], rm_rankings[i]["x_power"], rm_rankings[i]["weapon"]["name"],
                                   "",
                                   cb_rankings[i]["name"], cb_rankings[i]["x_power"], cb_rankings[i]["weapon"]["name"]])

    with open(os.path.join(rankings_folder,
                           "{} {} {} summary.csv".format(mode_time, url.split("/")[-3], url.split("/")[-2])), "w",
              newline="", encoding="utf8") as rankings_file:
        rankings_file.write("\ufeff")
        for i in formatted_rankings:
            csv.writer(rankings_file, quoting=csv.QUOTE_ALL).writerow(i)

    print("Statistics files have been written in '{}'.".format(os.path.basename(rankings_folder)))
    if os.name == "nt":
        subprocess.Popen("explorer /select,{}".format(os.path.join(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), rankings_folder),
            "{} {} {} summary.csv".format(mode_time, url.split("/")[-3], url.split("/")[-2]))))


def parse_league_stats(records):
    league_data = records["league_stats"]
    player_data = records["player"]

    medals = {"gold_count": "\x1b[38;2;248;231;65mgold\x1b[0m", "silver_count": "\x1b[38;2;236;239;243msilver\x1b[0m",
              "bronze_count": "\x1b[38;2;253;136;44mbronze\x1b[0m", "no_medal_count": "no"}

    print("\nYou've earned these medals from playing League:")
    print("\t\x1b[38;2;{:03d};{:03d};{:03d}m{}\x1b[0m\t\x1b[38;2;{:03d};{:03d};{:03d}m{}\x1b[0m".format(165, 30, 225,
                                                                                                        "Team", 25, 215,
                                                                                                        25, "Pair"))
    print("\x1b[38;2;{:03d};{:03d};{:03d}m{}\x1b[0m\t{:<8}{}".format(248, 231, 65, "Gold",
                                                                     league_data["team"]["gold_count"],
                                                                     league_data["pair"]["gold_count"]))
    print("\x1b[38;2;{:03d};{:03d};{:03d}m{}\x1b[0m\t{:<8}{}".format(236, 239, 243, "Silver",
                                                                     league_data["team"]["silver_count"],
                                                                     league_data["pair"]["bronze_count"]))
    print("\x1b[38;2;{:03d};{:03d};{:03d}m{}\x1b[0m\t{:<8}{}".format(253, 136, 44, "Bronze",
                                                                     league_data["team"]["bronze_count"],
                                                                     league_data["pair"]["bronze_count"]))
    print("None\t{:<8}{}".format(league_data["team"]["no_medal_count"], league_data["pair"]["no_medal_count"]))
    print("Power\t{:<8}{}".format(player_data["max_league_point_team"], player_data["max_league_point_pair"]))
    print("Total\t{:<8}{}".format(
        league_data["team"]["gold_count"] + league_data["team"]["silver_count"] + league_data["team"]["bronze_count"] +
        league_data["team"]["no_medal_count"],
        league_data["pair"]["gold_count"] + league_data["pair"]["silver_count"] + league_data["pair"]["bronze_count"] +
        league_data["pair"]["no_medal_count"]))

    try:
        with open(max(glob.glob(os.path.join(JSON_FOLDER, "*records*")), key=os.path.getctime),
                  encoding="utf8") as latest_results_file:
            latest_results = json.load(latest_results_file)
            latest_medals = latest_results["records"]["league_stats"]
    except ValueError:
        return  # Couldn't find any matching JSONs, probably because none were downloaded yet

    for i in ["pair", "team"]:
        for j in ["no_medal_count", "bronze_count", "silver_count", "gold_count"]:
            if league_data[i][j] > latest_medals[i][j]:
                medal_diff = league_data[i][j] - latest_medals[i][j]
                print("Earned {} new {} {} medal{}.".format(medal_diff, medals[j], i, "s" if medal_diff != 1 else ""))


def get_splatfest_events(festival_id):
    if str(festival_id) in FESTIVALS:
        festival_id = FESTIVALS[str(festival_id)]
    elif len(str(festival_id)) != 4 or str(festival_id) == "" or len(re.findall("[\D]", str(festival_id))) > 0:
        print("\nInvalid Splatfest ID. Please check it and try again.")
        return

    url = URL_API_FEST_EVENTS.format(festival_id)
    response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
    with open("{} {} {} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-3], url.split("/")[-2],
                                        url.split("/")[-1]), "w", encoding="utf8") as file:
        events = json.loads(response.text)
        json.dump(events, file, ensure_ascii=False)

    friends = []
    hundred = []
    try:
        for i in events["events"]:
            if i["event_type"]["key"] == "10_x_match":
                for j in i["members"]:
                    friends.append(j["name"])
            if i["event_type"]["key"] == "100_x_match":
                for j in i["members"]:
                    hundred.append(j["name"])
    except KeyError:
        print("\nSplatfest is not active.")
        return

    if friends:
        print("\nYour friends {}, {}, {}, and {} won a 10x Battle!".format(friends[0], friends[1], friends[2],
                                                                           friends[3]))

    url = URL_API_TIMELINE
    response = requests.get(url, headers=app_head_results, cookies=dict(iksm_session=COOKIE))
    with open("{} {}.json".format(time.strftime("%Y-%m-%d %H-%M-%S"), url.split("/")[-1]), "w",
              encoding="utf8") as file:
        json.dump(json.loads(response.text), file, ensure_ascii=False)


if __name__ == "__main__":
    main()
