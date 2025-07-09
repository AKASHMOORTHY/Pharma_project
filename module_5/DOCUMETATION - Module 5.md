# **DOCUMETATION - Module 5**

**Module 5: Inventory \& Warehouse Tracking** 

• Real-time stock updates 

• Material issuance, usage, returns 

• Threshold and reorder alerts 



**Packages used:**
fastapi==0.111.0

uvicorn==0.30.0

sqlalchemy==2.0.30

psycopg2-binary==2.9.9

alembic==1.13.1

pydantic==2.7.3

python-dotenv==1.0.1

pytest==8.2.2



**Available API Endpoints**

**Method**	**Endpoint**	                **Description**

POST	/api/inventory/inward/	        Add new inventory item (GRN)

POST	/api/inventory/transfer/	Move inventory between locations

GET	/api/inventory/{batch\_code}	Get inventory by batch code

POST	/api/inventory/consumption/	Consume inventory using FIFO

POST	/api/inventory/adjust/	        Manager manual stock adjustment



**Core Entities:**

InventoryItem: Tracks material quantity at a location.

StockMovement: Tracks movement from one location to another.



**Relationships:**

InventoryItem → RawMaterial (ForeignKey) — links to Module 2

StockMovement → InventoryItem (ForeignKey)

StockMovement → User (moved\_by, ForeignKey) — links to Module 1





**Proceeded with alembic migrations**

Run in PS C:\\Users\\akash\\Desktop\\pharma\_project\\module\_5\\inventory\_app> uvicorn app.main:app --reload



**Download Required Packages**

pip install -r requirements.txt



**Alembic Migration**

alembic revision --autogenerate -m "Initial inventory tables"

alembic upgrade head



**Open Swagger UI at**

http://localhost:8000/docs

