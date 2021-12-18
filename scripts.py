
import json


ROLES = ["Marine of Wars", "House of Marines", "Certified Marine Bro", "Event 2069 Survivor",
         "OG Marine", "OG Expeditor"]

ADMIN_ACCESS = ["High Lords of Agartha", "Admin"]

DISABLED_CHANNELS = ["bot-spam", "👣│rollout", "whitelist-enlist"]

RANK_ROLES = ["Guardsman", "Iron Priest", "Hearthguard Sgt",
              "Templar General", "Cardinals", "Arbitrator"]


def is_eligible(roles):
    for i in roles:
        if i.name in ROLES:
            return True
    return False


def is_Admin(roles):
    for i in roles:
        if i.name in ADMIN_ACCESS:
            return True
    return False


def is_correct_channel(Commands, command, channel_id):
    if(Commands[command] == "*" or channel_id == Commands[command]):
        return True
    return False


def is_whitelist_eligible(
        message, Activity_Tracker, Invite_Tracker):
    if message.author.name in Activity_Tracker:
        if Activity_Tracker[message.author.name] >= 1000:
            return True
    if message.author.name in Invite_Tracker:
        sum = invite_sum(Invite_Tracker[message.author.name])
        if sum >= 10:
            return True
    return False


def check_channel(channel):
    if channel in DISABLED_CHANNELS:
        return False
    return True


def update_eth_address(ethaddress):

    with open("ethaddresses.json", "w") as outfile:
        json.dump(ethaddress, outfile)


def update_invite_tracker(invites):
    with open("invite_tracker.json", "w") as outfile:
        json.dump(invites, outfile)


def update_activity_tracker(activities):
    with open("activity_tracker.json", "w") as outfile:
        json.dump(activities, outfile)


def update_commands(commands):
    with open("commands.json", "w") as outfile:
        json.dump(commands, outfile)


def get_rank(activity_tracker, message):
    value = sorted(activity_tracker.values())
    key = sorted(activity_tracker, key=activity_tracker.get)
    value.reverse()
    key.reverse()
    index = 0
    for i in key:
        if i == message.author.name:
            break
        index += 1
    rank = index + 1
    return rank


def get_rank_role(roles, role):  # Roles object and role string, return single role object
    for i in roles:
        if i.name == role:
            return i


def invite_sum(invites):
    sum = 0
    for i in invites.values():
        sum = sum + i["count"]
    return sum


def whitelist_roles(user_roles, whitelist_roles):
    for i in user_roles:
        if i.name in whitelist_roles:
            return True
    return False
