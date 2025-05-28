"""
Purchase model for Ludora backend shop.
"""
from tortoise.models import Model
from tortoise import fields

class Purchase(Model):
    """
    Purchase model.
    """
    id = fields.IntField(pk=True, generated=True)
    user = fields.ForeignKeyField('models.User', related_name='purchases', on_delete=fields.CASCADE)
    item = fields.ForeignKeyField('models.Item', related_name='purchase_records', on_delete=fields.CASCADE)
    quantity = fields.IntField()
    total_price = fields.IntField(description="Total in-app currency spent")
    purchased_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        # These direct field accesses (user_id, item_id) are generally fine.
        return f"Purchase {self.id} by {self.user_id} for {self.item_id}"
