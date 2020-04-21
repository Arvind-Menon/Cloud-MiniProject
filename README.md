# About Awesome Weather App

This README file is a rundown of my Cloud Computing module's (EC781P) Mini-Project's.

This is a simple app to display the weather conditions of a place. It utilized two api's to do so, namely the weather api from Breezometer ([API documentation](https://docs.breezometer.com/weather-api/v1/)) and LocationIQ's Geocoding API ([API documentation](https://locationiq.com/docs)) 

## App in a Nutshell:

The user is shown a html page where he/she is prompted to end the "Place" for which he'd like to see the weather conditions.
The "Place" field's input is the passed on a search query in locationiq's api to retrieve the co-ordinates.
The co-ordinates received are then passed as search query in breezometer's api, to retrieve the weather information.
This information is then flashed to the user in the HTML page.
The history of queries is stored in a cassandra database.

## How the app run's:

The app's HTML page ustilises bootstrap.
At the back-end, the code for the app's functionality is written in python. 
Flask being python's micro framework, is used.
Cassandra is used for the database since it is easy and robust to use.
The app is run on an AWS EC2 instance server. Cassandra's latest image is pulled in this instance and the app is run on this container.
The source code for the app is the app.py file
The app also utilizes a Self-Signed Certificate.
Load Balancing is implemented using Kubernetes.

## Overview

Application demo

![img](/demo.PNG)

## Cassandra 

Apache Cassandra is a database management system that replicates large amounts of data across many servers, avoiding a single point of failure and reducing latency.[Learn More.](https://cassandra.apache.org/)

To build image
```
sudo docker build . --tag=cassandrarest:v1
```
To run it as a service, exposing the deploment to get an external IP:
```
sudo docker run -p 80:80 cassandrarest:v1
```
```
sudo docker run -p 443:443 cassandrarest:v1 for https
```

## Creating RESTful Services

Please note: this REST API uses a self signed certificate for SSL encryption. The curl command doesn't like self signed certificates and will not allow any requests to be made. Therefore, in order be able to make a request run all the below commands using sudo and the command parameter -k.

To implement methods like GET,POST,PUT,DELETE.

1. GET method

The GET method is for retrieving information.Here to get the list of countries.
##### Request
```GET /
https://ec2-18-232-97-191.compute-1.amazonaws.com/places
```
##### Response
```
['Ukraine', 'East Ham', 'statue of liberty', 'west ham'] <--on the browser
```
2. POST method

To add a new entry.

##### Request
```POST /
curl -kiH "Content-Type: application/json" -X POST -d '{"Place":"Ukraine","Dew":66.55, "Temperature":15.5, "Wind": 10.6, "Humidity":56.7}' https://ec2-18-232-97-191.compute-1.amazonaws.com
```
##### Response
```
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 42
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Tue, 21 Apr 2020 08:34:49 GMT

{
  "message": "deleted: /places/Ukraine"
}
```
3. PUT method

To update an entry.
##### Request
```PUT /
curl -kiH "Content-Type: application/json" -X PUT -d '{"Place":"Ukraine","Dew":56.55, "Temperature":5.5, "Wind": 10.6, "Humidity":56.7}' https://ec2-18-232-97-191.compute-1.amazonaws.com
```
##### Response
```
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 42
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Tue, 21 Apr 2020 08:31:15 GMT

{
  "message": "deleted: /places/Ukraine"
}
```
4. DELETE method

To delete an entry.
##### Request
```DELETE/
curl -k -i -H "Content-Type: application/json" -X DELETE -d '{"Place":"Haiti"}' https://ec2-18-232-97-191.compute-1.amazonaws.com/places
```
##### Response
```
HTTP/1.0 200 OK
Content-Type: application/json
Content-Length: 42
Server: Werkzeug/1.0.1 Python/3.7.7
Date: Tue, 21 Apr 2020 08:29:05 GMT

{
  "message": "deleted: /places/Haiti"
}
```
## Creating a Home page

Index.html is created inside a templates folder. Flash uses this folder and file to render the HTML page to the user

![img](/home.PNG)

## Running Flask Application Over HTTPS

Self signed certificates are generated in the command line.
```
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
Generating a 4096 bit RSA private key
......................++
.............++
writing new private key to 'key.pem'
-----
About to be asked to enter information that will be incorporated
into the certificate request.This is called a Distinguished Name or a DN.
There are quite a few fields which can be leftblank
For some fields there will be a default value, enter '.', the field will be left blank.
-----
Country Name (2 letter code) [AU]:UK
State or Province Name (full name) [Some-State]:London
Locality Name (eg, city) []:East Ham
Organization Name (eg, company) [Internet Widgits Pty Ltd]:Mini Project
Organizational Unit Name (eg, section) []: QMUL
Common Name (e.g. server FQDN or YOUR name) []:Funny
Email Address []:a.menon@se19.qmul.ac.uk
```

This command writes a new certificate in cert.pem with its corresponding private key in key.pem, with a validity period of 365 days.
To use this new self-signed certificate in Flask application,ssl_context argument in app.run() is set with a tuple consisting of the certificate and private key files along with port=443.
[Learn more](https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https)

## Kuberenetes Load Balancing Implementation

In computing, load balancing refers to the process of distributing a set of tasks over a set of resources, with the aim of making their overall processing more efficient. Load balancing techniques can optimise the response time for each task, avoiding unevenly overloading compute nodes while other compute nodes are left idle

To create an External Load Balancer,following steps are required:

Install Kubernetes
```
sudo snap install microk8s --classic
```

  1.cassandra-image need to be build and push to registry
  ```
  sudo microk8s enable registry #To install registry
  sudo docker build . -t localhost:32000/cassandra-test:registry #To build and tag
  sudo docker push localhost:32000/cassandra-test # To push it to the registry
  ```

  2.restart and start docker again

  ````
  sudo systemctl restart docker 
  sudo docker start cassandra-test
  ````
  3.Configure the deployment.yaml file

  4.Deploy docker container image present in the registry 

  ```
  sudo microk8s.kubectl apply -f ./dev.yaml # To deploy
  sudo microk8s kubectl expose deployment app-deployment --type=LoadBalancer --port=443 --target-port=443
```
Handy:

 To see all the services and pods
 ```
 sudo microk8s.kubectl get all
 ```
 To delete 
 ```
 sudo microk8s.kubectl delete deployment app-deployment
 sudo microk8s.kubectl delete services app-deployment
 ```

To learn more about creating external load balancer.[link](https://kubernetes.io/docs/tasks/access-application-cluster/create-external-load-balancer/)
