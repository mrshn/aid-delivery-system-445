import threading
import time

def watchingThread(thread_id, wq):
    def sample_callback(request):
        print(f"Thread {thread_id} : request notified : ", request)
    wq.watch(thread_id, sample_callback)


def sample_callback(request):
    print("request notified : ", request)

class WatchQueue:
    _is_notified = {c : threading.Condition(threading.Lock()) for c in [1,2,3,4,5]}
    _active_requests = {}
    _mutex = threading.Lock()

    # one instance can only watch single campaign object
    def __init__(self, campaign_id):
        self.campaign_id = campaign_id
        self.is_watching = False

    @staticmethod
    def notifyCampaign(campaign_id, request):
        print(f"notifying campaign {campaign_id} ...")
        with WatchQueue._mutex:
            print(f" got lock")
            WatchQueue._active_requests[campaign_id] = request
            cond = WatchQueue._is_notified[campaign_id]
            with cond:
                cond.notify_all()

    def watch(self, thread_id, callback):
        cond = WatchQueue._is_notified[self.campaign_id]
        self.is_watching = True
        with cond:
            while True:
                print(f"Thread {thread_id} is waiting for campaign {self.campaign_id}")
                cond.wait()
                with WatchQueue._mutex:
                    if not self.is_watching:
                        break
                    callback(WatchQueue._active_requests[self.campaign_id])

    def handleClose(self):
        self.is_watching = False

wq1 = WatchQueue(5)
wq2 = WatchQueue(5)
wq3 = WatchQueue(5)

x1 = threading.Thread(target=watchingThread, args=(1, wq1))
x2 = threading.Thread(target=watchingThread, args=(2, wq2))
x3 = threading.Thread(target=watchingThread, args=(3, wq3))

x1.start()
x2.start()
x3.start()

# notify threads for campaign 5
print("first notification for campaign 5")
WatchQueue.notifyCampaign(5, "dummy request for campaign 5")

time.sleep(1)

print("closing thread 2 ...")
print()
# close on thread x2 & re-notify

wq1.handleClose()

time.sleep(1)

print("second notification for campaign 5")
WatchQueue.notifyCampaign(5, "x1 should be closed")


# notify campaign 4
#WatchQueue.notifyCampaign(4, "dummy request for campaign 5")


x1.join()
x2.join()
x3.join()



