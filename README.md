#Backend for my blog app with Djagno

###apps
the project generally consisted of three apps

1- **Auth App** that is for handling users info, authentication and authorization staffs
2- **Blogs App**
3- **Groups App**

###How to run
there is two options
1-run with django development server integrated with Daphne ASGI server just run in command line in project main directory
```
python manage.py runserver
```
2-run without development server
```
daphne blog_app_backend.asgi:application
```
