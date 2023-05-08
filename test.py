from lib import *
import json
import sys
import time

from client import Client

client1 = Client("localhost", 1423)

client1.call_register("emre", 1234)
time.sleep(0.1)

client1.call_login("emre", 1234)
time.sleep(0.1)

client1.call_login("emre", 1234)
time.sleep(0.1)


client1.call_new_instance("Maras", " Maras description")

time.sleep(0.1)

client1.call_new_instance("Maras2", " Maras description2")

time.sleep(0.1)

client1.call_list()

#time.sleep(0.1)
#client1.call_logout()

#time.sleep(0.1)
#client1.call_logout()

#time.sleep(0.1)
# logouttan sonra client recceive threadi kapanmazsa, 
# loginin bunun cevabunu o consume ettiği için logining recv'i bekliyor
# login yaparken yeni client instancesi oluşturulursa sorun çözülür
#client1.call_login("emre", 1234)

time.sleep(0.1)

client1.call_add_catalog_item("nameItem",["synm1","synm2"])
time.sleep(0.1)
client1.call_add_catalog_item("nameItem2",["sss"])

time.sleep(0.1)
client1.call_update_catalog_item("nameItem","updatednameItem",["synm10","synm20"])

time.sleep(0.1)
client1.call_add_catalog_item("searchedItem",["synm---","synm---"])

time.sleep(0.1)
client1.call_search_catalog_item("searchedItem")

time.sleep(0.1)
client1.call_open(0)

time.sleep(0.1)
client1.call_close()

print("HERE IT BREAKS 1")

time.sleep(0.1)
client1.call_open(0)

time.sleep(0.1)
client1.call_add_request([("searchedItem",2)], (0.1, 0.1), 1 )

time.sleep(0.1)
client1.call_add_request([("searchedItem2",3)], (0.2, 0.8), 2 )

print("HERE IT BREAKS 2")

time.sleep(0.1)
client1.call_update_request(0,[("searchedItem2",2)], (0.9, 0.9), 1 )

time.sleep(0.1)
client1.call_delete_request(0)

print("HERE IT BREAKS 3")

time.sleep(0.1)
client1.call_watch("nameItem", (0.0, 0.0))

print("HERE IT BREAKS 4")

time.sleep(0.1)
client1.call_add_request([("nameItem", 7)], (0.2, 0.8), 2 )

time.sleep(0.1)

print("HERE IT BREAKS 5")
client1.call_mark_available_request(2, [("nameItem", 3)], 1, (0.2, 0.8), "supply comments")
time.sleep(0.3)
print("HERE IT BREAKS 6")
client1.call_pick_request(2,client1.call_get_supply_ids())
time.sleep(0.1)
print("HERE IT BREAKS 7")
client1.call_arrived_request(2,0)
time.sleep(0.1)



time.sleep(0.5)
client1.call_logout()


#client1.call_pick_request(2, [("nameItem", 3)], 1, (0.2, 0.8), "supply comments")
#client1.call_arrived_request(2, [("nameItem", 3)], 1, (0.2, 0.8), "supply comments")


#time.sleep(0.1)
#client1.call_close()

#time.sleep(0.1)
#client1.call_watch("nameItem", (0.0, 0.0))


sys.exit()
