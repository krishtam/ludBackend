"""
InventoryItem model for Ludora backend.
"""
from tortoise.models import Model
from tortoise import fields

class InventoryItem(Model):
    """
    InventoryItem model.
    """
    id = fields.IntField(pk=True, generated=True)
    user = fields.ForeignKeyField('models.User', related_name='inventory_items', on_delete=fields.CASCADE)
    item = fields.ForeignKeyField('models.Item', related_name='inventory_entries', on_delete=fields.CASCADE)
    quantity = fields.IntField(default=1)
    acquired_at = fields.DatetimeField(auto_now_add=True)
    used_at = fields.DatetimeField(null=True, description="Timestamp when a consumable/ticket was last used")

    class Meta:
        unique_together = ("user", "item")

    def __str__(self):
        # These direct field accesses (user_id, item_id) are generally fine
        # as they are simple ID fields on the model itself.
        # If we were accessing related object properties like self.user.username,
        # we'd need to ensure the related object is fetched.
        return f"{self.user_id}'s {self.item_id} (x{self.quantity})"
