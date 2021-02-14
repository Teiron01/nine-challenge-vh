from flask import Flask, jsonify, make_response, request, Response, abort
from flask_restful import Api
from werkzeug.utils import redirect
import json
import pandas as pd

app = Flask(__name__)
app.config["DEBUG"] = True
api = Api(app)
jsonString = {"test":"new"}

@app.route('/filter', methods = ['POST'])
def filter():

  if not request.json or not 'payload' in request.json:
    payload = '{"error":"Could not decode request: JSON parsing failed"}'
    r = Response(payload, mimetype='text/json', status=400)
    return r
  
  #load json body into data
  data = request.json

  #load json into dataframe
  df = pd.json_normalize(data['payload'])

  #Filter drm = True & episode count > 0
  df = df[(df['drm'] == True) & (df['episodeCount'] > 0)]

  #Select desired columns
  df = df[['image.showImage','slug','title']]

  #Rename column image.showImage -> image
  df = df.rename(columns={"image.showImage": "image"})

  #Parse dataframe to json
  result = df.to_json(orient="records")
  result = result.replace("\/","/")
  payload = '{ "response": ' + result + '}'

  r = Response(payload, mimetype='text/json', status=200)
  return r

if __name__ == "__main__":
  app.run()