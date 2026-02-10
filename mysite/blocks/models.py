from django.db import models


class Block(models.Model):
    """Represents a single block on the grid."""
    x = models.IntegerField()
    y = models.IntegerField()
    owner = models.CharField(max_length=50, blank=True, null=True)
    color = models.CharField(max_length=7, default="#374151")  # Tailwind gray-700
    claimed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('x', 'y')  # Prevents duplicate blocks
        ordering = ['y', 'x']

    def __str__(self):
        status = f"owned by {self.owner}" if self.owner else "unclaimed"
        return f"Block ({self.x}, {self.y}) - {status}"
