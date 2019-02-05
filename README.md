# SplatNet 2 Data Grabber

I made this script last year to automate saving and parsing JSONs from SplatNet 2 because there's some pretty neat 
information in there that isn't shown in the app.

## Setup

This script uses `requests` for making web requests, `colorama` for terminal text colors, and `python-dateutils` for 
some date calculations. Be sure to install them from `requirements.txt`. 

You'll need your `iksm_session` cookie to authenticate to SplatNet 2. If you've used a program to upload your battles to
stat.ink, like splatnet2statink or SquidTracks, you've likely already used a proxy to get this cookie from your phone or
an emulator.

There is a sample config file in this repo called `config.txt.sample`. It's a JSON formatted file. Rename it to 
`config.txt`, and add your `iksm_session` cookie to the file:

```json
{"cookie": "PUT_YOUR_IKSM_SESSION_HERE"}
```

If you use splatnet2statink, you can copy or symlink your `config.txt` for that into this project's folder and it will 
work just fine.

You can order gear from the SplatNet Gear Shop with the script, but you will have to find your "unique ID" in order to 
do so. You can find this ID in one of two ways: Either record requests from the app using a proxy and look at the 
`x-unique-id` header, or use your `iksm_session` cookie in a browser to log in to SplatNet, and then look at the source 
of the page. It will be in the opening HTML tag:

```html
<html lang="en" data-region="US" data-unique-id="UNIQUE ID HERE" data-nsa-id="PRINCIPAL ID HERE">
...
</html>
```

`data-unique-id` will contain your unique ID, while `data-nsa-id` will contain your principal ID. More on those later.

There are 2 versions of the script: `datagrabber.py` and `datagrabbercolor.py`. They are functionally identical, but the
`color` version takes advantage of ANSI escape commands in certain terminals to show text in specific colors, like the 
ink colors for Splatfest teams. The regular `datagrabber.py` also uses colors, but they are more basic to work on 
terminals that don't support custom text colors.

If you are using Windows, you'll have to use `datagrabber.py`. For 
Linux and Mac, `datagrabbercolor.py` should work, but let me know if it doesn't. I've done my testing using Windows 10 
running Ubuntu 14.04 through WSL, and it's worked for me so far.

Three menu options will copy text to the clipboard:
* `c` or `cookie`: Copies your `iksm_session`
* `fc`: Copies your friend code
* `patch notes`: Copies the link to the US patch notes page

On Windows, these options will use `clip`. Linux and Mac have more options, so you can set your clipboard command in the
`CLIP_CMD` variable near the top. Since I tested using WSL, I've left it set to `clip.exe` since WSL can access Windows 
executables like that.

The folder structure is relatively simple:

```text
    splatnet-datagrabber      Base directory
    ├───gear images           Gear images from the SplatNet Shop and Salmon Run rewards
    │   ├───headgear          Headgear images
    │   ├───clothes           Clothes images
    │   └───shoes             Shoes images
    ├───jsons                 JSONs
    │   ├───battles           Battle result JSONs
    │   ├───league rankings   League ranking JSONs
    │   └───x power rankings  X Power ranking JSONs and CSVs
    ├───shared images         Generated images
    ├───splatfest images      Splatfest team images
    ├───splatfest stats       Splatfest power statistics
    └───weapon images         Main, sub, and special weapon images for new weapons on the timeline
```

These names can be changed near the top of the script, and can, of course, be made to use symlinks to dump files and 
images elsewhere on disk. Most JSONs will be placed in the base `splatnet-datagrabber` directory to make sure they don't
overwrite an existing copy in the `jsons` folder.

There is also an `ids.json.sample` file in the repo that contains a sample principal ID and nicknames for the owner of 
that ID. Principal IDs are 16 character hex IDs that unique identify each player. You can use them to look up the 
player's current nickname and icon. If you rename the file to `ids.json` and add a principal ID to list, you can track 
the nicknames of your friends, or enemies. Just something I thought would be neat to implement.

## Usage

### Main Menu

There are a few different types of commands you can use. The first type are accessed with a number. You'll see a list of
options when you first start the script:

```text
1 - Profile
2 - Win/Loss of Last 50 Battles
3 - Results of a Specific Battle (Image + JSON)
4 - Results of Latest Battle (Image + JSON)
5 - Results of Latest Battle (Monitor) (Image + JSON)
6 - Results of All Battles (Image + JSON)
0 - Exit
```

These commands will get images and JSONs relating to your profile or recent battles. After picking an option, you will 
likely be prompted with additional options, like the map and ink color for the profile image, or the battle number for a
battle's result image.

Option 5 will put the script into monitoring mode. Every 90 seconds, it will check to see if a new battle was added to 
your results,  and will download the image and JSON for that battle's results once it detects it. It will also print the 
details of the battle to the console window:

```text
1490  Musselforge Fitness     League Battle      Tower Control   DEFEAT
```

You can exit monitoring mode by pressing Ctrl-C. It will take a few seconds to get an image of your profile, your 
win/loss over the last 50 games, and your records JSON, after which it will return to the menu for regular use.

### Direct Access

The more interesting commands are accessed by typing in their names and arguments, somewhat like a terminal. 
For more information, take a look at the `direct_access` function in the script, or enter `?` at the prompt to view the 
help documentation for each command. For example, here is what the documentation looks like:

```
Help Legend
Function:       What the command does
Options:        How to activate the command
                Most commands will prompt you for additional information unless 'directly' is in the description
Print:          What gets printed to the terminal
Write:          What files get written

...

Function:       Get X Rankings for a specific season
Options:        "x rank", "rank x", "x"
Print:          X Rankings for specified season
Write:          X Rankings for specified season, and final rankings if season is complete
```

Here are a few of the commands I use regularly.

`league everything 0 0` checks your `league rankinkgs` folder to find the last set of league JSONs that were downloaded,
then determines the next rotation that occurred after that, as well as the most recent rotation, and downloads those 
JSONs from SplatNet. These league JSONs don't contain the player's nicknames, but does contain their weapons and league 
power, so you could gather some data and and look at trends in weapon usages over time.  
If you don't have any league rankings downloaded yet, the script will automatically start at the first league record 
from July 2017 and work its way up to the latest. This may take a while.

`update nicknames` checks your `ids.json` file and updates the nicknames. You can set a "friendly name" in the 
`nickname` field, and any names from SplatNet are added to the `names` array.

`x rank 2018-12` gets the top X Rank players from all four modes from 2018-12. If the season is done and calculations 
are finished, running this command will also create a `.CSV` with the top 500 players from all four modes along with 
their weapons and final powers. 

`votes 19` gets you the votes for Splatfest #19. There is a dictionary of the Splatfest numbers and their IDs for North 
America so that you can say `votes 19`, `rankings 19`, or `fest results 19` instead of `votes 4054`, where `4054` is the 
internal ID for Splatfest #19. The default dictionary refers to the dictionary of NA Splatfests, but you can switch it 
to match your account's region:

```python
FESTIVALS = FESTIVALS_NA  # Default setting for NA accounts
FESTIVALS = FESTIVALS_JP  # Use this for JP accounts
FESTIVALS = FESTIVALS_EU  # Use this for EU accounts
```

Note that you will not be able to access the votes, rankings, or results for another region's Splatfests. You can only 
see those for Splatfests from your account's region.

You can, however, view their ink colors using `na colors`, `jp colors`, and `eu colors`, all of which use 
Splatoon2.ink's API.

A few other possibly useful commands are `salmon`, which shows the upcoming Salmon Run rotations, complete with timing, 
stage, and weapon information; `next`, which will show you next rotation's stages and modes, and can take an optional 
number of rotations, like `next 2` will show you information for the rotation after next rotation; and `records`, which 
downloads your records JSON, which includes interesting things like your total wins and losses on each stage and with 
each weapon, and your powers/clout and max rank from past Splatfests.

There are many more commands available in `direct_access`. Take a look and let me know what you think.
