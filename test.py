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
client1.call_logout()
client1.call_logout()
client1.call_login("emre", 1234)

client1.call_add_catalog_item("nameItem",["synm1","synm2"])
client1.call_add_catalog_item("nameItem2",["sss"])
client1.call_update_catalog_item("nameItem","updatednameItem",["synm10","synm20"])
client1.call_add_catalog_item("searchedItem",["synm---","synm---"])
client1.call_search_catalog_item("searchedItem")


client1.call_open(0)
client1.call_close()
client1.call_open(0)
client1.call_add_request([("searchedItem",2)], (0.1, 0.1), 1 )
client1.call_add_request([("searchedItem2",3)], (0.2, 0.8), 2 )
client1.call_update_request(0,[("searchedItem2",2)], (0.9, 0.9), 1 )
client1.handle_delete_request(0 )


sys.exit()
