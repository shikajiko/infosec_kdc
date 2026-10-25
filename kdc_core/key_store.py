from common.protocol import SEP
from common.utils import KEY_LENGTH

class KeyStore:
    def __init__(self):
        self._keys = {}

    def set_key(self, entity_id, key):
        if not entity_id or SEP in entity_id or not entity_id.isascii():
            raise ValueError("invalid entity ID")
        if len(key) != KEY_LENGTH or not key.isascii():
            raise ValueError(f"key must be {KEY_LENGTH} ASCII characters")
        self._keys[entity_id] = key

    def get_key(self, entity_id):
        return self._keys[entity_id]

    def has_entity(self, entity_id):
        return entity_id in self._keys

    def list_entities(self):
        return sorted(self._keys)