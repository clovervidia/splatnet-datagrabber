#! /usr/bin/python3
# -*- coding: utf-8 -*-

# clovervidia

help_legend = ["Help Legend",
               {"function": "What the command does", "options": "How to activate the command\n\t\tMost commands will "
                                                                "prompt you for additional information unless "
                                                                "'directly' is in the description",
                "print": "What gets printed to the terminal", "write": "What files get written"}]

direct_access_help = ["Direct Access Help",
                      {"function": 'Get Salmon Run schedule',
                       "options": '"coop schedules", "coop", "salmon run", "salmon", "s"',
                       "print": 'Current and upcoming Salmon Run schedules',
                       "write": 'Current and upcoming Salmon Run schedules JSON'},
                      {"function": 'Get Salmon Run results', "options": '"coop results"', "print": 'Nothing',
                       "write": 'Salmon Run results JSON'},
                      {"function": 'Get list of current stages',
                       "options": '"data stages", "stages", "stage data", "maps"', "print": 'Nothing',
                       "write": 'JSON of current stages and their pictures'},
                      {"function": 'Get nickname and icon for principal ID', "options": '"nickname", "name", "icon"',
                       "print": "The user's nickname and icon URL", "write": 'Nothing'},
                      {"function": 'Update nickname database', "options": '"update names", "update nicknames"',
                       "print": 'New nicknames found for users in database',
                       "write": 'New nicknames found for users in database to database file'},
                      {"function": 'Get and order available items at the SplatNet Gear Shop',
                       "options": '"onlineshop merchandises", "merchandise", "shop", "store", "annie", "order", '
                                  '"buy gear"',
                       "print": 'Available gear at the shop', "write": 'Available gear at the shop JSON'},
                      {"function": 'Get multiplayer records', "options": '"records"', "print": 'Nothing',
                       "write": 'Multiplayer records JSON'},
                      {"function": 'Get singleplayer records', "options": '"records hero", "hero records", "hero"',
                       "print": 'Nothing', "write": 'Singleplayer records JSON'},
                      {"function": 'Get your stats for all stages', "options": '"stage records", "stage stats"',
                       "print": 'Stats for all stages', "write": 'Nothing'},
                      {"function": 'Get your stats for specific stage',
                       "options": '"stage records <stage ID>", "stage stats <stage ID>"',
                       "print": 'Stats for specified stage', "write": 'Nothing'},
                      {"function": "Get your stats for all weapons you've used",
                       "options": '"weapon records", "weapon stats"', "print": "Stats for all weapons you've used",
                       "write": 'Nothing'},
                      {"function": 'Get your stats for a specific weapon',
                       "options": '"weapon records <weapon ID>", "weapon stats <weapon ID>"',
                       "print": 'Stats for specified weapon', "write": 'Nothing'},
                      {"function": 'Get your league medal count and new medals since last time',
                       "options": "league stats",
                       "print": 'League medal count and new medals since last time you used "records"',
                       "write": 'Nothing'},
                      {"function": 'Get your latest battle results', "options": '"results"', "print": 'Nothing',
                       "write": 'Latest battle results JSON'},
                      {"function": 'Get current and upcoming stage rotations',
                       "options": '"schedules", "schedule", "rotations", "rotation", "r"',
                       "print": 'Current stage and mode rotation and time left until next rotation',
                       "write": 'Stage schedule JSON'},
                      {"function": 'Get next stage rotation', "options": '"rotation next", "next rotation, "next"',
                       "print": "Next rotation's stages and modes and time left until then", "write": 'Nothing'},
                      {"function": 'Get current and next 2 stage rotations',
                       "options": '"now and later", "nnl"',
                       "print": 'Current and next 2 stage and map rotation and time left until the next',
                       "write": 'Nothing'},
                      {"function": 'Get your timeline', "options": "timeline",
                       "print": 'Nothing, unless there is an announcement for new weapons or you changed ranks',
                       "write": 'Timeline JSON'},
                      {"function": 'Go to Splatfest/Festival Direct Access',
                       "options": '"festival", "splatfest", "fes", "fest"',
                       "print": 'Nothing', "write": 'Nothing'},
                      {"function": 'Get the League leaderboards for a specific rotation and region',
                       "options": "league", "print": 'Nothing',
                       "write": 'The League leaderboards for the specified rotation JSON'},
                      {"function": "Get all region's League leaderboards for a specific rotation",
                       "options": '"league all", "l"', "print": 'Nothing',
                       "write": "All region's League leaderboard JSONs for specified rotation"},
                      {"function": "Get all region's League leaderboards for a specific rotation directly",
                       "options": "league all <league code>", "print": 'Nothing',
                       "write": "All region's League leaderboard JSONs for specified rotation"},
                      {"function": 'Get all League leaderboards between two league codes',
                       "options": "league everything <start code> <end code>"
                                  "\n\t\tUse 0 for both to automatically set start and end codes",
                       "print": 'Download progress and any regions that did not have any of a League type',
                       "write": "All region's League leaderboard JSONs between specified league codes"},
                      {"function": "Get X Rankings for a specific season", "options": '"x rank", "rank x", "x"',
                       "print": 'X Rankings for specified season',
                       "write": 'X Rankings for specified season, and final rankings if season is complete'},
                      {"function": 'Get X rankings for a specific season directly',
                       "options": "x rank <4 digit year>-<2 digit month>",
                       "print": 'X Rankings for specified season',
                       "write": 'X Rankings for specified season, and final rankings if season is complete'},
                      {"function": "Open File Explorer to the script's folder (Windows)", "options": "f",
                       "print": 'Nothing', "write": 'Nothing'},
                      {"function": 'Get your profile with ranks, weapon, and gear', "options": '"profile", "ranks"',
                       "print": 'Your nickname, level, ranks, total turf inked, weapon, and gear', "write": 'Nothing'},
                      {"function": 'Get your profile in the same format SquidTracks uses for its profiles',
                       "options": '"profile tracks", "tracks profile"',
                       "print": 'Your nickname, level, ranks, total wins, total losses, and win %', "write": 'Nothing'},
                      {"function": 'Get a link to the latest patch notes', "options": "patch notes",
                       "print": 'Links to Japanese and English patch notes, and copies link to English patch notes to '
                                'clipboard',
                       "write": 'Nothing'}]

fest_direct_access_help = ["Splatfest Direct Access Help",
                           {"function": "Get active Splatfests", "options": "active",
                            "print": "Whether there's an active Splatfest going on, and how long until it starts, "
                                     "\n\t\tfinishes, or results get released",
                            "write": "Active Splatfest JSON"},
                           {"function": "Get past Splatfests", "options": "pasts", "print": "Nothing",
                            "write": "Past Splatfests JSON"},
                           {"function": "Get votes for a specific Splatfest", "options": "votes",
                            "print": "Votes for the specified splatfest",
                            "write": "Votes JSON for the specified Splatfest"},
                           {"function": "Get votes for a specific Splatfest directly",
                            "options": "votes <splatfest ID>", "print": "Votes for the specified splatfest",
                            "write": "Votes JSON for the specified Splatfest"},
                           {"function": "Get rankings for a specific Splatfest", "options": "rankings",
                            "print": "Nothing", "write": "Rankings JSON for the specified Splatfest"},
                           {"function": "Get rankings for a specific Splatfest directly",
                            "options": "rankings <splatfest ID>", "print": "Nothing",
                            "write": "Rankings JSON for the specified Splatfest"},
                           {"function": "Get Splatfest Power rankings for the top 100 players for a specific Splatfest",
                            "options": '"ranking average", "average power", "splatfest power"',
                            "print": "Average, minimum, and maximum Splatfest Powers for specified Splatest",
                            "write": "Nothing"},
                           {"function": "Get Splatfest Power statistics for all past Splatfests",
                            "options": '"splatfest power stats", "splatfest stats"',
                            "print": "Folder name of output files",
                            "write": "CSVs with Splatfest Top 100 Players and Splatfest Power average/minimum/maximum"},
                           {"function": "Get results of specific Splatfest",
                            "options": '"fest results, "results", "result"', "print": "Results of specified Splatfest",
                            "write": "Results JSON for specified Splatfest"},
                           {"function": "Get results of specific Splatfest directly",
                            "options": "fest results <splatfest ID>", "print": "Results of specified Splatfest",
                            "write": "Results JSON for specified Splatfest"},
                           {"function": "Get data for all Splatfests for Splatoon2.ink",
                            "options": '"all festivals", "all fest", "all splatfest"',
                            "print": "Nothing", "write": "Data JSON for all Splatfests"},
                           {"function": "Get Splatfest ink colors for your region",
                            "options": '"colors", "splatfest colors"',
                            "print": "Splatfest ID, team names, and team colors in RGB and hex", "write": "Nothing"},
                           {"function": "Get Splatfest ink colors for North American Splatfests",
                            "options": '"na colors", "us colors"',
                            "print": "Splatfest ID, team names, and team colors in RGB and hex", "write": "Nothing"},
                           {"function": "Get Splatfest ink colors for European Splatfests",
                            "options": '"na colors", "us colors"',
                            "print": "Splatfest ID, team names, and team colors in RGB and hex", "write": "Nothing"},
                           {"function": "Get Splatfest ink colors for Japanese Splatfests",
                            "options": '"na colors", "us colors"',
                            "print": "Splatfest ID, team names, and team colors in RGB and hex", "write": "Nothing"},
                           {"function": "Get all Splatfest team images for your region",
                            "options": '"team images", "images", "splatfest images", "fest images"', "print": "Nothing",
                            "write": "Team images for all Splatfests in your region"},
                           {"function": "Get a specific Splatfest's events", "options": '"events", "event battles"',
                            "print": "The names of your friends who won a 10x match or players who won a 100x match",
                            "write": "Events JSON for specified Splatfest"},
                           {"function": "Get a specific Splatfest's events directly",
                            "options": "events <splatfest ID>",
                            "print": "The names of your friends who won a 10x match or players who won a 100x match",
                            "write": "Events JSON for specified Splatfest"}]


def help_reader():
    for menu in [help_legend, direct_access_help, fest_direct_access_help]:
        print(menu[0])
        for item in menu[1:]:
            print("Function:\t{}".format(item["function"]))
            print("Options:\t{}".format(item["options"]))
            print("Print:\t\t{}".format(item["print"]))
            print("Write:\t\t{}\n".format(item["write"]))