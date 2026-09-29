import json
import logging

from flask import current_app
from redis import Redis
from redis.exceptions import RedisError

from app import extensions

logger = logging.getLogger(__name__)

CENTRES_LIST_PREFIX = "centres:list"
CENTRE_TESTS_KEY = "centre:{centre_id}:tests"


def get_redis():
    return extensions.redis_client


def init_redis(app):
    if app.config.get("USE_FAKEREDIS"):
        import fakeredis

        extensions.redis_client = fakeredis.FakeRedis(decode_responses=True)
        return extensions.redis_client

    extensions.redis_client = Redis.from_url(
        app.config["REDIS_URL"],
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1,
    )
    return extensions.redis_client


def _ttl():
    return int(current_app.config.get("CACHE_TTL_SECONDS", 60))


def cache_get(key: str):
    client = get_redis()
    if client is None:
        return None
    try:
        raw = client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except (RedisError, TypeError, json.JSONDecodeError) as exc:
        logger.warning("Redis cache get failed for %s: %s", key, exc)
        return None


def cache_set(key: str, value, ttl: int | None = None) -> None:
    client = get_redis()
    if client is None:
        return
    try:
        client.setex(key, ttl or _ttl(), json.dumps(value))
    except (RedisError, TypeError) as exc:
        logger.warning("Redis cache set failed for %s: %s", key, exc)


def cache_delete(*keys: str) -> None:
    client = get_redis()
    if client is None or not keys:
        return
    try:
        client.delete(*keys)
    except RedisError as exc:
        logger.warning("Redis cache delete failed: %s", exc)


def invalidate_centre_caches(centre_id: int | None = None) -> None:
    client = get_redis()
    if client is None:
        return
    try:
        keys = list(client.keys(f"{CENTRES_LIST_PREFIX}:*"))
        if centre_id is None:
            keys.extend(client.keys("centre:*:tests"))
        else:
            keys.append(CENTRE_TESTS_KEY.format(centre_id=centre_id))
        if keys:
            client.delete(*keys)
    except RedisError as exc:
        logger.warning("Redis cache invalidation failed: %s", exc)


def centres_list_key(page: int, per_page: int) -> str:
    return f"{CENTRES_LIST_PREFIX}:{page}:{per_page}"


def centre_tests_key(centre_id: int) -> str:
    return CENTRE_TESTS_KEY.format(centre_id=centre_id)
