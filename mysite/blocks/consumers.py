import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Block


class BlockConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time block claiming game."""
    
    # All connected users share one room
    ROOM_GROUP = "blocks_game"
    
    # Vibrant colors for users
    COLORS = [
        "#EF4444", "#F97316", "#F59E0B", "#EAB308", "#84CC16",
        "#22C55E", "#10B981", "#14B8A6", "#06B6D4", "#0EA5E9",
        "#3B82F6", "#6366F1", "#8B5CF6", "#A855F7", "#D946EF",
        "#EC4899", "#F43F5E"
    ]
    
    async def connect(self):
        # Generate unique user ID and color
        self.user_id = f"user_{random.randint(10000, 99999)}"
        self.user_color = random.choice(self.COLORS)
        
        # Join the game room
        await self.channel_layer.group_add(
            self.ROOM_GROUP,
            self.channel_name
        )
        await self.accept()
        
        # Send initial state to new user
        blocks = await self.get_all_blocks()
        await self.send(text_data=json.dumps({
            "type": "init",
            "user_id": self.user_id,
            "color": self.user_color,
            "blocks": blocks
        }))
        
        # Notify others about new connection
        await self.channel_layer.group_send(
            self.ROOM_GROUP,
            {
                "type": "user_joined",
                "user_id": self.user_id
            }
        )

    async def disconnect(self, close_code):
        # Free all blocks owned by this user
        freed_coords = await self.free_user_blocks()
        
        # Broadcast freed blocks + user_left BEFORE leaving the group
        if freed_coords:
            await self.channel_layer.group_send(
                self.ROOM_GROUP,
                {
                    "type": "blocks_freed",
                    "user_id": self.user_id,
                    "blocks": freed_coords
                }
            )
        
        await self.channel_layer.group_send(
            self.ROOM_GROUP,
            {
                "type": "user_left",
                "user_id": self.user_id
            }
        )
        
        # Leave the game room
        await self.channel_layer.group_discard(
            self.ROOM_GROUP,
            self.channel_name
        )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        data = json.loads(text_data)
        msg_type = data.get("type")
        
        if msg_type == "claim":
            x = data.get("x")
            y = data.get("y")
            
            # Try to claim the block
            success, block_data = await self.claim_block(x, y)
            
            if success:
                # Broadcast update to all clients
                await self.channel_layer.group_send(
                    self.ROOM_GROUP,
                    {
                        "type": "block_update",
                        "x": x,
                        "y": y,
                        "owner": self.user_id,
                        "color": self.user_color
                    }
                )
            else:
                # Send rejection only to this user
                await self.send(text_data=json.dumps({
                    "type": "claim_rejected",
                    "x": x,
                    "y": y,
                    "reason": "Block already claimed"
                }))

    # === Broadcast handlers ===
    
    async def block_update(self, event):
        """Send block update to client."""
        await self.send(text_data=json.dumps({
            "type": "block_update",
            "x": event["x"],
            "y": event["y"],
            "owner": event["owner"],
            "color": event["color"]
        }))

    async def user_joined(self, event):
        """Notify client about new user."""
        await self.send(text_data=json.dumps({
            "type": "user_joined",
            "user_id": event["user_id"]
        }))

    async def user_left(self, event):
        """Notify client about user leaving."""
        await self.send(text_data=json.dumps({
            "type": "user_left",
            "user_id": event["user_id"]
        }))

    async def blocks_freed(self, event):
        """Notify client about freed blocks."""
        await self.send(text_data=json.dumps({
            "type": "blocks_freed",
            "user_id": event["user_id"],
            "blocks": event["blocks"]
        }))

    # === Database operations ===
    
    @database_sync_to_async
    def get_all_blocks(self):
        """Get all claimed blocks."""
        blocks = Block.objects.exclude(owner__isnull=True).exclude(owner='')
        return [
            {"x": b.x, "y": b.y, "owner": b.owner, "color": b.color}
            for b in blocks
        ]

    @database_sync_to_async
    def claim_block(self, x, y):
        """Try to claim a block. Returns (success, block_data)."""
        # Check if block exists and is already claimed
        block, created = Block.objects.get_or_create(
            x=x, y=y,
            defaults={
                "owner": self.user_id,
                "color": self.user_color,
                "claimed_at": timezone.now()
            }
        )
        
        if created:
            # Successfully claimed new block
            return True, {"x": x, "y": y, "owner": self.user_id, "color": self.user_color}
        elif not block.owner:
            # Block exists but unclaimed, claim it
            block.owner = self.user_id
            block.color = self.user_color
            block.claimed_at = timezone.now()
            block.save()
            return True, {"x": x, "y": y, "owner": self.user_id, "color": self.user_color}
        else:
            # Block already claimed by someone else
            return False, None

    @database_sync_to_async
    def free_user_blocks(self):
        """Clear all blocks owned by this user. Returns list of freed coords."""
        blocks = Block.objects.filter(owner=self.user_id)
        coords = [{"x": b.x, "y": b.y} for b in blocks]
        blocks.update(owner=None, color="#374151", claimed_at=None)
        return coords
