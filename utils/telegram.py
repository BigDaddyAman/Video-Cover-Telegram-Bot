
import logging

from aiogram.types import Message, MessageEntity


logger = logging.getLogger(__name__)


def serialize_caption_entities(message: Message):
    if not message.caption_entities:
        return None

    return [
        entity.model_dump(mode="json", exclude_none=True)
        for entity in message.caption_entities
    ]


def restore_caption_entities(data):
    if not data:
        return None

    return [
        MessageEntity.model_validate(entity)
        for entity in data
    ]


def validate_caption_entities(caption, entities):
    if not caption or not entities:
        return None

    caption_length = len(caption.encode("utf-16-le")) // 2
    valid_entities = []

    for entity in entities:
        start = entity.offset
        end = start + entity.length

        if (
            start < 0
            or entity.length <= 0
            or end > caption_length
        ):
            logger.warning(
                "Skipping invalid caption entity: "
                "type=%s offset=%s length=%s caption_length=%s",
                entity.type,
                start,
                entity.length,
                caption_length,
            )
            continue

        valid_entities.append(entity)

    return valid_entities or None
