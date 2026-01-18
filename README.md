graph LR
    User(User/Client) -- POST /analyze --> API[FastAPI Server]
    API -- Returns Task ID --> User
    API -- Pushes Job --> Redis[(Redis Queue)]
    
    subgraph Worker Nodes
    Redis -- Pulls Job --> Worker[Celery Worker]
    Worker -- Loads Model --> HuggingFace[HuggingFace Transformers]
    Worker -- Saves Result --> DB[(PostgreSQL DB)]
    end
    
    User -- GET /status --> API
    API -- Reads Status --> DB