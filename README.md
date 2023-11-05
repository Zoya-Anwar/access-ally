# access-ally
Durhack 2023

We coded this application in ```Python 3.9``` in the backend and in the frontend it uses ```Next.JS```. Both backend and frontend can work without the retrieval of map data for demo purposes, using data we have already prepared for you. If you wish to retrieve real time data, complete section Getting Map Data.

## Backend 

### Installation and setup
Install Python 3.9 using https://www.python.org/downloads/release/python-390/

In the commandline use:
```pip3 install requirements```

### Running the server locally 
```flask --port 811```

## Frontend 

### Installation and setup
Install Node using [https://www.python.org/downloads/release/python-390/](https://nodejs.org/en)
Install Next.js using https://nextjs.org/docs/getting-started/installation

In the commandline run:
```npm install vite```

### Running the server locally 
```npm dev run```

## Getting Map Data

### Prerequisites 
Install Docker using https://docs.docker.com/engine/install/
Download your required dataset  
Use the docker image for OSRM https://hub.docker.com/r/osrm/osrm-backend/
