import discord, re
from . import config

class UserError(Exception):
    def __init__(self, message="Invalid Input"):
        self.message = message

# The regex used to recognize if a word is an external emoji
parseEmojis = re.compile("^<:.+:\d+>$")

def parse_time_to_seconds(raw_time):
    r"""Parses a time string to seconds. Takes a form such as "6h".
    Returns an integer representing the total time in seconds.
    Parameters
    ----------
    raw_time : string
    Should be in form: \d+[smhd], an integer followed by a unit, either s, m, h, or d.
    """
    units = ("d", "h", "m", "s")
    try:
        minutes = int(raw_time[:-1])
    except ValueError:
        raise UserError("Invalid time duration.")
    unit = raw_time[-1].lower()
    if not unit in units:
        raise UserError("Invalid time unit")
    if unit == "d":
        minutes *= 86400
    elif unit == "h":
        minutes *= 3600
    elif unit == "m":
        minutes *= 60
    return minutes

def parse_bool(in_bool):
    r"""Parses a string to decide if it is true or false.
    Defaults to true unless input matches "false", "0", "no".
    Case insensitive.
    Parameters
    ----------
    in_bool : string
        The string to be parsed to see if it is true or false.
    """
    falseValues = ("false", "0", "no")
    return in_bool.lower() not in falseValues

async def collect_messages(ctx, one_channel, timestamp, stopwords, case_insensitive):
    """Collects messages from a discord server from within a time period.
    Returns a frequency dictionary with its findings.
    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The context that the command is being run from.
        Is used to get the current channel, and server if necessary.
    one_channel : bool
        Determines if only a single channels history should be grabbed,
        or every channel in the server that the bot can access.
    timestamp : datetime.datetime
        The datetime that the bot should look forward from
    stopwords : list[string] or set[string]
        A list of words that should be left out of the word count if matched.
    case_insensitive : bool
        If the messages should be case sensitive or not.
    """
    # Getting the channel's that should be grabbed from
    if one_channel or ctx.guild is None: # If the message isn't in a server just grab current channel
        histories = [ctx.history]
    else:
        histories = [i.history for i in list(filter(
            lambda i:type(i) is discord.TextChannel and i.permissions_for(ctx.me).read_messages,
            ctx.guild.channels))]
    words = dict()
    for hist in histories:
        async for msg in hist(limit=None, after=timestamp):
            if msg.author is not ctx.me:
                # clean_content parses @'s and #'s to be readable names, while content doesn't.
                add_frequency(words, msg.clean_content, stopwords, case_insensitive)
    return words

def add_frequency(freq_dict, text, stopwords, case_insensitive):
    r"""Adds the frequency of words inside the given string to a dict.
    Strips characters at the start and end as defined by
        config.get_config()["commands"]["whatdidimiss"]["strip"]
    Ignores words longer than 20 characters unless they're of the emoji format.
    Parameters
    ----------
    freq_dict : dict
        The dictionary that these values should be added to.
    test : string
        The string that should be parsed
    stopwords : list[string] or set[string]
        A list of words that should be left out of the word count if matched.
    case_insensitive : bool
        If the frequency should be case sensitive or not
    """
    MAXLEN = 20
    # A dictionary of words, each word having an integer value of it's frequency
    # Adds the frequency to an existing set, pass an empty dict() to start with.
    if not text.startswith("."):
        for word in text.split():
            if case_insensitive:
                word = word.lower()
            word = word.strip(config.get_config()["commands"]["whatdidimiss"]["strip"])
            if word not in stopwords and (len(word) <= MAXLEN or parseEmojis.match(word)):
                if word in freq_dict:
                    freq_dict[word] += 1
                else:
                    freq_dict[word] = 1

def check_perms(ctx, perms):
    """Checks if the discord bot has all the required permissions in the given channel.
    Returns true if the bot has all permissions required,
    or if the context takes place within DM's where permissions don't apply.
    Parameters
    ----------
    ctx : discord.ext.commands.Context
        The context that the command is being run in.
        Used to get the channel, and check if the command is being run in a server.
    perms : discord.Permissions
        The set of permissions that the bot requires.
        Only values explicitly defined are checked.
    """
    # Checks that all permissions are present in context's channel, if the channel is part of a guild (server)
    return type(ctx.me) is not discord.Member or ctx.channel.permissions_for(ctx.me).is_superset(perms)

def merge_dicts(dict_one, dict_two):
    """Merges two dicts
    Recursively merges sub-dicts, rather than overwriting them at the top level as update() does.
    Parameters
    ----------
    dict_one : dict
        The dictionary for values to be merged into. This dictionary is written to.
    dict_two : dict
        The dictionary for values to be read from.
    """
    # Merges dict_two into dict_one, merging dicts and only overwriting values with the same name:
    for key, val in dict_two.items():
        if type(val) is dict and key in dict_one and type(dict_one[key]) is dict:
            merge_dicts(dict_one[key], val)
        else:
            dict_one[key] = val
            
            