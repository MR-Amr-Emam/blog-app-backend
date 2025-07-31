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

[auth apis](https://drive.google.com/file/d/1k3xPrgGW7OJV55cqsHrJmbSjF8DQOMki/view?usp=drive_link)

[blogs apis](https://drive.google.com/file/d/1r9i9sAaovZzyqKeqbj20_u0tCjNONha9/view?usp=drive_link)

[groups apis](https://drive.google.com/file/d/1qXpQy_QXRrPCDim4l3Z0MBAq06fHM-Lv/view?usp=drive_link)

APIS EndPoints
