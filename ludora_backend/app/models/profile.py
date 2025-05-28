"""
UserProfile model for Ludora backend.
"""
from tortoise.models import Model
from tortoise import fields

class UserProfile(Model):
    """
    UserProfile model.
    """
    id = fields.IntField(pk=True, generated=True) # Clarified generated=True as per common practice for pk IntFields
    user = fields.OneToOneField('models.User', related_name='profile', on_delete=fields.CASCADE)
    first_name = fields.CharField(max_length=100, null=True)
    last_name = fields.CharField(max_length=100, null=True)
    avatar_url = fields.CharField(max_length=255, null=True)
    bio = fields.TextField(null=True)
    current_streak = fields.IntField(default=0)
    max_streak = fields.IntField(default=0)
    in_app_currency = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        # Accessing user_id directly might not be loaded by default,
        # and could cause an error if the user object isn't fetched.
        # A safer approach is to ensure the user object is loaded,
        # or handle the case where it might not be (though for __str__ it's often assumed).
        # For simplicity here, we'll assume user_id is available.
        # In async contexts, this might be more complex.
        # return f"{self.user_id}'s Profile" # This would require self.user_id to be loaded
        return f"Profile for User ID: {self.user_id if hasattr(self, 'user_id') else 'N/A'}"
