# Backend for my blog app with Djagno

### apps
the project generally consisted of three apps

1- **Auth App** that is for handling users info, authentication and authorization staffs
2- **Blogs App**
3- **Groups App**

### How to run
there is two options
1-run with django development server integrated with Daphne ASGI server just run in command line in project main directory
```
python manage.py runserver
```
2-run without development server
```
daphne blog_app_backend.asgi:application
```

### Note

*django app is configured with MySQL database

*ASGI server is used for realtime application for websocket communication

*you can look at all Apis endpoint in url http://localhost:8000/swagger/

here is glimpse for these endpoints

<img width="953" height="504" alt="auth-api" src="https://github.com/user-attachments/assets/63d9aec7-c60e-4d55-b8e4-f55fbe2bbecf" />

<img width="714" height="573" alt="blog-api" src="https://github.com/user-attachments/assets/932cafaf-be3b-49c3-a79b-c64f273e2a88" />

<img width="952" height="392" alt="group-api" src="https://github.com/user-attachments/assets/32c09671-4e52-4bc1-9bb2-af2a128315da" />

