## Social Networking API
This project is a social networking API built using Django Rest Framework. It provides functionalities for user authentication, searching users, managing friend requests, and listing friends.

## Features
**User Authentication:**

- **Signup:** Users can sign up using their email address.
- **Login:** Users can log in using their email and password.
- **Authentication:** All API endpoints (except signup and login) require the user to be authenticated.

**User Search:**

- Search users by email or name with pagination (up to 10 records per page).
- If the search keyword matches an exact email, the user associated with that email is returned.
- If the search keyword matches any part of a user's name, all matching users are returned.

**Friend Request Management:**

- Send friend requests to other users.
- Accept or reject received friend requests.
- List all friends (users who have accepted your friend requests).
- View a list of pending friend requests (requests you have received but not yet responded to).
- Users cannot send more than 3 friend requests within a minute.
### Setup and Installation:
**Clone the repository:**
- git clone https://github.com/pankajchouhan78/Accuknox_test.git
- cd social-networking-api

**Install the required dependencies:**
- pip install -r requirements.txt
