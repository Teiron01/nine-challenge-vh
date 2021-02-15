from flask import Flask, jsonify, make_response, request, Response
from flask_restful import Api
from werkzeug.exceptions import BadRequest
from werkzeug.utils import redirect
import json
import pandas as pd

app = Flask(__name__)
app.config["DEBUG"] = True
api = Api(app)

#Custom error response for "Bad Requests"
@app.errorhandler(400)
def handle_bad_request(e):
    payload = '{"error":"Could not decode request: JSON parsing failed"}'
    r = Response(payload, mimetype='application/json', status=400, content_type='application/json')
    return r

app.register_error_handler(400, handle_bad_request) 

#Filter JSON body to drm = True and episode count > 0 
#Returns: response body with data fields: image, slug, title
def processData(data):
  try:
    #load json into dataframe
    df = pd.json_normalize(data['payload'])

    #Filter drm = True & episode count > 0
    df = df[(df['drm'] == True) & (df['episodeCount'] > 0)]

    #Select desired columns
    df = df[['image.showImage','slug','title']]

    #Rename column image.showImage -> image
    df = df.rename(columns={"image.showImage": "image"})

    #Parse dataframe to valid json
    result = df.to_json(orient="records")
    result = result.replace("\/","/")
    payload = '{ "response": ' + result + '}'

    resp = Response(payload, mimetype='application/json', status=200, content_type='application/json')
  except KeyError as err: 
    return handle_bad_request(err)
    
  return resp

#Endpoint definition to extract JSON body from API request
@app.route('/filter', methods = ['POST'])
def filter():

  # Check if JSON body is present with "payload"
  if not request.json or not 'payload' in request.json:
    return handle_bad_request(KeyError)
  
  try:
    #load json body into data
    data = request.json
    resp = processData(data)
  except KeyError as err:
    return handle_bad_request(err)

  return resp

if __name__ == "__main__":
  app.run()