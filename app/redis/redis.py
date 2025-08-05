import os
import redis
import json
import logging

logger = logging.getLogger(__name__)


class Rediss:
    @staticmethod
    def publish_new_import(output_path: str):
        r = redis.Redis(
            host=os.getenv("REDIS_HOST"),
            port=os.getenv("REDIS_PORT"),
            db=os.getenv("REDIS_DB"),
        )

        import_data = {"output_path": output_path}

        try:
            message = json.dumps(import_data)
            r.publish("imports", message)
            logger.info(f"Published import: {message} to channel 'imports'")
        except redis.exceptions.ConnectionError as e:
            print(f"Error connecting to Redis: {e}")
