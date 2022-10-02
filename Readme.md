<h1>Getting this Repo up and Ready</h1>
To run this repo, simply run the following command.

```
git clone 
docker-compose up --build
```
Then, the demo API is accessible via <a href="http://localhost:7071">http://localhost:7071</a>.

<h1>Requesting to the API </h1>
Requesting to the API is possible using 2 ways:
<ul>
    <li> Requesting via web
    <li> Requesting via a script
</ul>
Example for each alternatives will be presented below. <br><br>

<h2> 1. Requesting via Web </h2> <hr> </hr>
Open the FastAPI Swagger UI using the following steps
<ol>
    <li> Open <a href="http://localhost:7071/docs">http://localhost:7071/docs</a>.
    <li> Click the /api/mfcc window under the <b> api </b> tab.
    <li> Make your request
</ol>

This request will output the following response (given it is successful).

```
{"mfcc_features": list,
 "total_time": integer}
```
Below are the explanation of the response.
<ul>
    <li> mfcc_features: The MFCC features that are extracted using the algorithm
    <li> total_time: Time needed to compute the MFCC features
</ul> <br>

<h2> 2. Requesting via a Script </h2> <hr> </hr>
Simply make a <b> POST </b> request to <a href="http://localhost:7071/api/mfcc"> http://localhost:7071/api/mfcc </a> with the following parameters:
<ul>
    <li> audio_file: Audio file to be uploaded, should be in a form of Blob.
    <li> frame_ms: How many miliseconds are there in a frame, should be float.
    <li> hop_ms: The duration of hop in miliseconds, should be float.
    <li> n_mels: How many mel filter banks will be created, should be integer.
    <li> num_ceps: How many cepstral features will be extracted from DCT, should be integer.
</ul> 
<br>
This request will output the following response (given it is successful).

```
{"mfcc_features": list,
 "total_time": integer}
```
Below are the explanation of the response.
<ul>
    <li> mfcc_features: The MFCC features that are extracted using the algorithm
    <li> total_time: Time needed to compute the MFCC features
</ul> <br>
Below is an example implementation using Python.

```python
import requests

with open("audio_sample.wav", "rb") as file:
    data = {
        "audio_file" : open("audio_sample.wav", "rb"),
        "frame_ms": 25.0,
        "hop_ms": 10.0,
        "n_mels": 128,
        "num_ceps": 13,
    }
    response = requests.post("http://localhost:7071/api/mfcc", data=data)
print(response.json())
```
However testing using this method is not advised due to the heavy number of response that is submitted back since the mfcc_features is not compressed in any way 