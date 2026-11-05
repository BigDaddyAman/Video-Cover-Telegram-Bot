from aiogram.types import Message, MessageEntity, User

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