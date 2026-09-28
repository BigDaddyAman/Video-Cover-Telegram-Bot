from aiogram.types import Message, MessageEntity, User


def serialize_caption_entities(message: Message):
    """Convert Telegram caption entities to Python data."""
    if not message.caption_entities:
        return None

    entities = []

    for entity in message.caption_entities:
        data = {
            "offset": entity.offset,
            "length": entity.length,
            "type": entity.type,
            "user": None,
        }

        if entity.type == "text_mention" and entity.user:
            data["user"] = entity.user.model_dump()

        entities.append(data)

    return entities


def restore_caption_entities(data):
    """Convert Python data back to Telegram entities."""
    if not data:
        return None

    result = []

    for entity in data:
        user = None

        if entity.get("user"):
            user = User.model_validate(
                entity["user"]
            )

        result.append(
            MessageEntity(
                type=entity["type"],
                offset=entity["offset"],
                length=entity["length"],
                user=user,
            )
        )

    return result