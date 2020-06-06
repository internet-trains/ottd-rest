from app import api
import json

with open("api.json", "w") as outfile:
    json.dump(api.spec.to_dict(), outfile)
