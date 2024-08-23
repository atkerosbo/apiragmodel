import requests
import json

url = "127.0.0.1:8000/summerize"

payload = json.dumps({
  "querry": "At the age of twenty-one, Pierre - that was the name he gave the winegrower - had been sent by his father to spend some time with his uncle in Madagascar. Within two weeks he had fallen for a local girl called Faniry, or Desire in Malagasy. You could not blame him. At seventeen she was ravishing. In the Malagasy sunlight her skin was golden. Her black, waist-length hair, which hung straight beside her cheeks, framed large, fathomless eyes. It was a genuine coup de foudre, for both of them. Within five months they were married. Faniry had no family, but Pierre's parents came out from France for the wedding, even though they did not strictly approve of it, and for three years the young couple lived very happily on the island of Madagascar. Then, one day, a telegram came from France. Pierre's parents and his only brother had been killed in a car crash. Pierre took the next flight home to attend the funeral and manage the vineyard left by his father."
})
headers = {
  'x-key': 'fake-super-secret-key',
  'x-token': 'fake-super-secret-token',
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)