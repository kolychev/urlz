URLs exchange service for quick-sharing links between browsers / mobile devices.

# Building and publishing docker image

`docker build -t kolychevoleg/urlz . && docker push kolychevoleg/urlz`

# Running docker image

Start container:

`docker run -it --rm -p 8080:80 kolychevoleg/urlz`

Then open in browser:

http://localhost:8080/
