from mongoengine import connect, Document, StringField, BinaryField, DateTimeField
import mongomock
import uuid
from fhe_crypto import fhe_key_gen, prune_pub_key_dir, fhe_encrypt
from datetime import datetime
from typing import List

# Connect to mongomock
connect('mongoenginetest', mongo_client_class=mongomock.MongoClient)

class KeyPair(Document):
    key_id = StringField(required=True, unique=True)
    principal_id = StringField(required=True)
    name = StringField(required=True)
    created = DateTimeField(required=True)
    expired = DateTimeField(required=True)
    crypto_context = BinaryField(required=True)
    public_key = BinaryField(required=True)
    private_key = BinaryField(required=True)

    
class DAO:
    def generate_keypair(self, name: str, principal_id: str, created: datetime, expired: datetime):
        key_id = f'fhe_{str(uuid.uuid4())}'
        cc, sk, pk = fhe_key_gen(key_id)
        
        key_pair = KeyPair(key_id=key_id, 
            crypto_context = cc,
            public_key=pk, 
            private_key=sk,
            created = created,
            name = name,
            principal_id = principal_id,
            expired = expired)
        key_pair.save()
        self.prune_all_key_ids()
        
        return key_pair

    def remove_keypair(self, key_id: str):
        key_pair = KeyPair.objects(key_id=key_id).first()
        if key_pair:
            key_pair.delete()
            return True
        return False

    def get_all_keypairs(self, principal_id: str):
        return KeyPair.objects(principal_id=principal_id)

    def get_keypair(self, key_id: str, principal_id: str):
        return KeyPair.objects(key_id=key_id, 
                               principal_id=principal_id).first()

    def prune_all_key_ids(self, principal_id):
        key_id_list = [key_pair.key_id 
                       for key_pair in KeyPair.objects(principal_id=principal_id).only('key_id')]
        return prune_pub_key_dir(key_id_list)

    def fhe_encrypt_db(self, key_id: str, principal_id:str, vec: List[float]):
        kp = self.get_keypair(key_id, principal_id)
        e  = fhe_encrypt(vec, kp.crypto_context, kp.public_key)
        return {}
