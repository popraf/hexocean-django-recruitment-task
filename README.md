# hexocean-django-recruitment

API that allows any user to upload an image in PNG or JPG format followed by processing to thumbnail. Solution uses Django REST, Celery, Redis, Postgres.

#### Running the project
Git clone the repository, then use `docker-compose up`. Once docker builds the images, API is served on local machine via `http://localhost:8000/`.

This solution comes with pre-defined `.env` variables and Celery on the same container as Django, without NGINX and S3, therefore it is a development build.

#### Features
- Asynchronous images processing to thumbnails using Celery and Redis
- Easy user accounts tier and thumbnails height management using admin panel
- This project comes with fixtures, initial data is loaded once image is built (but w/o images, thumbnails)
  - Available users in initial data (account tier: login/password):
    - SU: test_user/test_user_password
    - Basic: test_user_basic/test_user_password
    - Premium: test_user_premium/test_user_password
    - Enterprise: test_user_enterprise/test_user_password

#### Endpoints
- admin/ - Manage thumbnail heights, user tiers, and accounts.
- images/upload/ - Upload image
- images/view/ - View image (if accessible)
- thumbnails/view/`<int:height>`/ - View thumbnails in requested height if user account tier has access to
- expiring_link/new/ - Generate expiring link for uploaded image or thumbnail
- expiring_link/`<str:linkUUID>`/ - View uploaded image or thumbnail by generated UUID
