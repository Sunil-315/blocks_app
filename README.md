<img width="1563" height="918" alt="image" src="https://github.com/user-attachments/assets/4feae74e-0355-449b-bf22-5d0aebb71708" />


## Techstack used:

* **Django** - Serves HTML page via standard views
* **Django Channels** - Routes WebSocket Connections
* **Redis** - Channel layer that broadcasts messages between consumer instances
* **PostgreSQL** - Primary database that stores who owns the block
* **Alpine.js** - Handles the frontend. Renders the grid and processes WebSocket messages

---

<img width="1560" height="907" alt="image" src="https://github.com/user-attachments/assets/f81d820a-23a6-480a-8386-f398aa705461" />


## How it works?

1.  **Browser gives a Get request** to Django URL router. Then django serves `views.py` of the blocks app and renders `game.html`.
2.  **WebSocket connection is established** by `routing.py` and `consumer.connect()`.
3.  **random user_id and random color** is generated for each user
4.  **user is added to Redis channel layer**
5.  **user's info** like which blocks are claimed is being broadcast to all other players.

<img width="1537" height="916" alt="image" src="https://github.com/user-attachments/assets/43a18fbd-0bba-4b60-a0ec-0ce539432db4" />


### Claiming a Block:
* Through Client-side client claims block at (x,y). (user,x,y) is sent to `consumers.py`
* `consumers.py` checks through db if block available or occupied. if available send (block, owner, color) to client else claim rejected.
* if block as new owner it is reflected in redis layer as well and is being broadcast to others.

### Disconnect:
When a player exits the site `BlockConsumer.disconnect()` is called to broadcast the blocks freed. All blocks claimed by that user are made unclaimed and colored grey.
