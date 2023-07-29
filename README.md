# CK-API

CK-API is a backend built with Python, FastAPI, MongoDB, and motor to make a fast, scalable, and non-io blocking API that can handle many requests at one time.
This API is paired with the CK-Client you can view more of that project [here](https://github.com/DutsAndrew/ck-client). CK is a employee organization tool that helps users stay organized by keeping the many apps that we all use day-to-day in one interface.

## Task List

### App Setup
- [X] Setup MongoDB for data storage
- [X] Initialize non I/O blocking with async/await
- [X] Setup FastAPI Framework for fast building and performance
- [X] Organize App into MVC architecture with Models, Views, Controllers, and Models all siloed into their own modules
- [X] Keep virtualenv dependencies stored in requirements.txt and in the local files

### Data Modeling
- [X] Silo models in "Models" folder and use them in controllers as needed to validate and maintain data according to schemas
- [X] Build User, Team, Task, Sub_task, Note, Note_Edit, Message, Event, Color_Scheme, Chat, Calendar, and Announcement models
- [X] Setup Validation for User

### Routing
- [X] Silo Routes into "Route" folder and import them into main.py for use
- [X] Create route files that match their prefixes
- [X] Keep all routes as "async" to maintain non I/O blocking functionality
- [X] Link routes to appropriate controllers

### Controllers
- [X] Setup default "app" api request controllers to send default static data to user
- [X] Setup sign_up() controller to validate user auth request, create user instance, hash password for privacy and security, save user to db
- [ ] Create controller for users to login, accompany it with necessary routes and validation
- [ ] Create JWT Token auth for users to maintain auth while using the app
- [ ] Setup remaining controllers for users performing CRUD operations on the following:
  - [ ] Calendar
  - [ ] JenkinsAI
  - [ ] Messaging
  - [ ] Notes
  - [ ] Pages
  - [ ] Tasks
  - [ ] Teams

### Performance
- [ ] Stress test system to make sure it can handle traffic
- [ ] Optimize data intensive tasks make sure they're isn't a better solution for high-touch operations
- [ ] Ensure data responses are in the ms range and can be sent quickly to the user

### Security
- [ ] Setup middleware and other functions to protect app when ready for Production deployment
- [ ] Add compliance configurations to keep API private and only accessible to authenticated users
- [ ] Double check what the most up-to-date approaches are to keeping API's secure

### Production Env
- [ ] Setup production MongoDB env
- [ ] Convert app to Production ready env and separate dev env