# **Module 1**



## **Module 1: User \& Access Management** 

• Role-based login: Supervisor, QA, Manager, Admin 

• Permissions for viewing, editing, and reporting 



### Testuser details:

username: admin@example.com

password: Admin@123



-------------------------------

**User Created by Admin**

{

&nbsp; "email": "qa@example.com",

&nbsp; "full\_name": "QAUser",

&nbsp; "shift": "B",

&nbsp; "role\_id": 1,

&nbsp; "password": "Qa@12345"

}

{

&nbsp; "email": "qa1@example.com",

&nbsp; "full\_name": "QAUser1",

&nbsp; "shift": "A",

&nbsp; "role\_id": 1,

&nbsp; "password": "Qa1@12345"

}



**Users Available**

\[

&nbsp;   {

&nbsp;       "email": "admin@example.com",

&nbsp;       "full\_name": "Admin User",

&nbsp;       "shift": "A",

&nbsp;       "role\_id": 1,

&nbsp;       "id": 1,

&nbsp;       "is\_active": true

&nbsp;   },

&nbsp;   {

&nbsp;       "email": "qa@example.com",

&nbsp;       "full\_name": "QAUser",

&nbsp;       "shift": "B",

&nbsp;       "role\_id": 1,

&nbsp;       "id": 2,

&nbsp;       "is\_active": true

&nbsp;   },

&nbsp;   {

&nbsp;       "email": "qa1@example.com",

&nbsp;       "full\_name": "QAUser1",

&nbsp;       "shift": "A",

&nbsp;       "role\_id": 1,

&nbsp;       "id": 3,

&nbsp;       "is\_active": false

&nbsp;   }

]





**Final Testing users created:**

{

&nbsp; "email": "qa2@example.com",

&nbsp; "full\_name": "QAUser2",

&nbsp; "shift": "A",

&nbsp; "role\_id": 3,

&nbsp; "password": "Qa2@99999"

}



{

&nbsp; "email": "qa3@example.com",

&nbsp; "full\_name": "QAUser3",

&nbsp; "shift": "A",

&nbsp; "role\_id": 3,

&nbsp; "password": "Qa3@12345"

}



### Roles Defining:

Admin

Supervisor

QA

Manager





### Required Packages:

\*\*Python 3.10+\*\*

\- \*\*FastAPI\*\*

\- \*\*SQLite\*\*

\- \*\*SQLAlchemy\*\*

\- \*\*Alembic\*\*

\- \*\*Python-Jose (JWT)\*\*

\- \*\*Passlib (bcrypt)\*\*

\- \*\*Dotenv\*\*

-\*\*starlette\*\*

-\*\*pytest\*\*

-\*\*httpx\*\*



#### Install dependencies

pip install -r requirements.txt



#### Run Alembic migrations

alembic upgrade head



### API Overview

#### Auth

#### Method	Endpoint	Description

POST	      /api/auth/login	           Login with JWT

POST	     /api/auth/logout	           Logs logout session

POST	     /api/auth/change-password	   Change own password



#### User

#### Method	Endpoint	Access	Description

GET	       /api/profile	             All	View logged-in user

GET	      /api/users/	             Admin	List all users

POST	     /api/users/	             Admin	Create user

GET	    /api/users/{id}	             Admin	View specific user

PUT	   /api/users/{id}	            Admin	Update user

DELETE	  /api/users/{id}	            Admin	Soft delete user





