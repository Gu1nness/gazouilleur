#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MongoDB manager for gazouilleur.
Handles all communications necessary.
"""

import time
import asyncio
from pymongo.errors import OperationFailure
from txmongo import MongoConnection, connection
from txmongo.filter import sort as mongosort, ASCENDING, DESCENDING
from gazouilleur.config import MONGODB
connection._Connection.noisy = False

db_foll_coll = lambda x: "followers.%s" % x.lower().lstrip("@")


def sortasc(field):
    return mongosort(ASCENDING(field))

def sortdesc(field):
    return mongosort(DESCENDING(field))



async def SingleMongo(coll, method, *args, **kwargs):
    conn = MongoConnection(MONGODB['HOST'], MONGODB['PORT'])
    database = conn[MONGODB['DATABASE']]
    await database.authenticate(MONGODB['USER'], MONGODB['PSWD'])
    res = await getattr(database[coll], method)(*args, **kwargs)
    conn.disconnect()
    return res


async def save_lasttweet_id(channel, tweet_id):
    await SingleMongo(
        'lasttweets',
        'update',
        {'channel': channel},
        {'channel': channel, 'tweet_id': tweet_id},
        upsert=True
    )


async def find_stats(query, **kwargs):
    res = await SingleMongo('stats', 'find', query, **kwargs)
    return res


async def count_followers(user):
    res = await SingleMongo(db_foll_coll(user), 'find', {"follows_me": True})
    return len(res)


async def find_last_followers(user):
    res = await SingleMongo(
        db_foll_coll(user),
        'find',
        {"screen_name": {"$exists": True},
         "follows_me": True,
         "last_update": {"$gte": time.time() - 12*3600}}
    )
    return res


async def ensure_indexes(database, retry=True):
    try:
        await database['logs'].ensure_index(sortasc('channel') + sortdesc('timestamp'), background=True)
        await database['logs'].ensure_index(sortasc('channel') + sortasc('user'), background=True)
        await database['logs'].ensure_index(sortasc('channel') + sortasc('user') + sortdesc('timestamp'), background=True)
        await database['tasks'].ensure_index(sortasc('channel') + sortasc('timestamp'), background=True)
        await database['feeds'].ensure_index(sortasc('database') + sortasc('timestamp'), background=True)
        await database['feeds'].ensure_index(sortasc('channel') + sortasc('database'), background=True)
        await database['feeds'].ensure_index(sortasc('channel') + sortasc('database') + sortdesc('timestamp'), background=True)
        await database['filters'].ensure_index(sortasc('channel'), background=True)
        await database['filters'].ensure_index(sortasc('channel') + sortasc('keyword') + sortdesc('timestamp'), background=True)
        await database['news'].ensure_index(sortdesc('_id') + sortasc('channel'), background=True)
        await database['news'].ensure_index(sortasc('channel') + sortdesc('timestamp'), background=True)
        await database['news'].ensure_index(sortasc('channel') + sortasc('source'), background=True)
        await database['news'].ensure_index(sortasc('channel') + sortasc('source') + sortdesc('timestamp'), background=True)
        await database['dms'].ensure_index(sortasc('id') + sortasc('channel'), background=True)
        await database['tweets'].ensure_index(sortasc('id'), background=True)
        await database['tweets'].ensure_index(sortasc('in_reply_to_status_id_str'), background=True)
        await database['tweets'].ensure_index(sortasc('channel') + sortdesc('id'), background=True)
        await database['tweets'].ensure_index(sortasc('channel') + sortdesc('timestamp'), background=True)
        await database['tweets'].ensure_index(sortasc('channel') + sortasc('id') + sortdesc('timestamp'), background=True)
        await database['tweets'].ensure_index(sortasc('channel') + sortasc('user') + sortdesc('timestamp'), background=True)
        await database['tweets'].ensure_index(sortasc('channel') + sortasc('uniq_rt_hash'), background=True)
        await database['tweets'].ensure_index(sortdesc('id') + sortasc('channel') + sortasc('uniq_rt_hash'), background=True)
        await database['stats'].ensure_index(sortdesc('timestamp') + sortasc('user'), background=True)
        await database['lasttweets'].ensure_index(sortasc('channel'), background=True)
    except OperationFailure as error:
        # catch and destroy old indices built with older pymongo versions
        if retry:
            for coll in ["logs", "tasks", "feeds", "filters", "news", "dms", "tweets", "stats", "lasttweets"]:
                await database[coll].drop_indexes()
            await ensure_indexes(database, retry=False)
        else:
            raise error

