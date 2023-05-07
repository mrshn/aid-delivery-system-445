from lib import *
import json

from client import Client


client = Client("localhost", 1423)


client.register("emre", 1234)
client.login("emre", 1234)


# Below are old test codes
""""

User("tekmen0", "tekmen0@gmail.com", "tekmen tekmen", "secret")
user = User.search_user("tekmen0")

print("auth : ", user.auth("secret"))

for i in range(3):
    Item(str(i*5))

print("Items : ", Item._Item__all_items)

user.login()

campaign = Campaign("mycapmaign", "description of my capmaign")
req_ids = []
for i in range(2):
    req_ids.append(campaign.addrequest(Request(user.username, [("5",i*100),("10", i*200)], (0.1, 0.1), Urgency.SOON)))

print("request1 : ", campaign.getrequest(req_ids[1]))
campaign.updaterequest(user, req_ids[1], {"geoloc": (0.3,0.3)})
print("request1 : ", campaign.getrequest(req_ids[1]))
campaign.removerequest(user, req_ids[1])

req = Request._Request__all_requests[req_ids[0]]

supplier = User("supplier", "supplier@gmail.com", "s s", "secret")

supply_id = req.markavailable(supplier, ["5", 24], 1, (0.1,0.1), "comments")

req.pick(supply_id, ["5", 13])


user.logout()

"""