from lib import *
import json
import sys

from client import Client

client1 = Client("localhost", 1423)

client1.call_register("emre", 1234)
client1.call_login("emre", 1234)

client1.call_new_instance("Maras", " Maras description")
client1.call_new_instance("Maras2", " Maras description2")

client1.call_list()

client1.call_open(0)


print("annan")
sys.exit()


client1.send_command({
    "command" : "list",
    "args": []
})



# login


# create 3 new campaigns
client1.send_command({
    "command" : "new",
    "args": ["maraş", "maraş peçete yardımı"]
})

client1.send_command({
    "command" : "list",
    "args": []
})

client1.send_command({
    "command" : "new",
    "args": ["aydın", "vinç yardımı"]
})

client1.send_command({
    "command" : "new",
    "args": ["antep", "yiyecek yardımı"]
})

client1.send_command({
    "command" : "list",
    "args": []
})

# open not existing campaign
client1.send_command({
    "command" : "open",
    "args": [10]
})

# open campaign
client1.send_command({
    "command" : "open",
    "args": [0]
})

# open another
client1.send_command({
    "command" : "open",
    "args": [1]
})

# add request
client1.send_command({
    "command" : "addrequest",
    "args": [1]
})

# add another another
client1.send_command({
    "command" : "addrequest",
    # items, geoloc, urgency
    "args": [[], (0,0), "URGENT"]
})




#client2 = Client("localhost", 1423)

#client2.register("supplier", 1234)
#client2.login("supplier", 1234)




# Below are old test codes

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
