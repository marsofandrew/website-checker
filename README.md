# Website checker

This application is designed to check availability of websites.

## How to start configure and application

User should create file `resources/security/creds.env` that should look like
```
DB_USER=db_user
DB_PASSWORD=Apassword
```

### How to run application
```
docker-compose up 
```

## How to interact
User could create regular expressions (regexp) by sending `POST /regexp`.
If user needs they may use that regexp in creation of website_checker (`POST /website_checker`).

User could also `DELETE` and `GET` that resources.

User can access metrics by following REST requests
* `GET /metric` - all checks
* `GET /metric/{website_checker_id}` - metrics that are filtered by website_checker_id

### How to interact with website_checker

After website_checker is created it immediately starts.
User is able to stop specified website checker (`POST /website_checker/{id}/stop`)
or to stop  all website checkers (`POST /website_checker/stop`).

If website_checker stopped it could be started (`POST /website_checker/{id}/start`).

## REST API ##
OpenAPI 3.0 spec is available on /openapi.json

Swagger UI: /swaggerui

## Developer guide

Server part (src/server) is responsible for:
* creating website_checkers
* creating regexps that are used in website_checkers
* providing metrics to user via REST API
* executing website_checkers

Writer or consumer part (src/writer) is responsible for:
* Writing metrics to DB
* Removing website_checkers from DB