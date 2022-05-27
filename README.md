# appointment_chatbot

[![Build status](https://github.com/martialo12/appointment_chatbot/actions/workflows/python-app.yml/badge.svg)](https://github.com/martialo12/appointment_chatbot/actions)

let's have a look at high level design before trying to dive into project code.
![architecture](/img/diagram.png)

## Features

- **FastAPI** with Python 3.9
- Sqlite
- postgresql
- SqlAlchemy
- Docker compose for easier development
- Login with Google oauth2
- DialogFlow ES( one of the best NLP tool available out there)

## Usage demo

That was enough talking, how can you use it:

 - Find [@kwagbot](@kwagbot) or [@kwagMeetinBot](@kwagMeetinBot) on telegram and enjoy!
 - ![/img/demo](/img/demo.gif)



#### backend

Make sure you have [python3.9](https://www.python.org/) installed.

Inside backend directory run: 

```
    pip install -r requiirements.txt
```

after ding so run: 

```
    uvicorn app.application:app --host 0.0.0.0 --port 5000 --reload
```

You can now navigate to `localhost:3000` in your browser and you should be able to see an awesome app page with just three buttons.
At `localhost:5000/docs` or `localhost:5000/redoc` you can inspect the API documentation


since you are going to be running this locally.

### with docker

Start postgresql, the FastApi backend and the React frontend using `docker-compose`.

run this command below inside nudge directory:

for default configuration
```
docker-compose up -f docker-compose.override.yml
```

You can now navigate to `localhost:3000` in your browser and you should be able to see an awesome app page with just three buttons.
At `localhost:5000/docs` or `localhost:5000/redoc` you can inspect the API documentation


To run this to on remote machine(for deployment), run all these commands:

```
docker network create traefik-public 
```

```
docker-compose -f docker-compose.traefik.yml -d
```

```
docker-compose -f docker-compose.yml --env-file up -d
```

At `https://kwagchatbot.xyz/docs` or `https://kwagchatbot.xyz//redoc` you can inspect the API documentation

## Test and Deploy

Edit config.yml file and make your sure that hostname is localhost for postgresql database.

From backend directory use this command below in other to run tests(make sure you've activated your virtual environment):

```
pytest --html=report.html --self-contained-html
```

***

## Project Layout
```
backend
|__ app
    |___api
        |___chatbot
        |    |____endpoints.py
        |    |____repositories.py
        |    |____schemas.py
        |    |____services.py
        |
        |___core
        |    |______config.py
        |    |______custom_lib
        |    |       |_________df_response_lib.py
        |    |
        |    |______client_secrets.json
        |            
        |
        |___containers.py
        |
        |___db
        |    |_____database.py
        |    |_____exceptions.py
        |
        |___tests
        |       |__test_chatbot
        |
        |
        |___application.py
```

## Support
for any king of issue or prolem , please reach me at: `martialo218@gmail.com`

## Contributing
if you want to contribute to this project just clone it and start making your changes right away.

## Authors and acknowledgment
**twitter**: martialo dev [follow me](https://twitter.com/martialobug)

**instagram**: martialo dev [follow me](https://www.instagram.com/martialo_dev/)

## License
MIT

## Project status
this project is still under development
