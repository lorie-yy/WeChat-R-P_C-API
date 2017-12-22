import time
import httplib, urllib
from datetime import datetime,timedelta
from wechatfans.views import updateAllShopProfit


def get_wechatfans_data():
    print "[INFO][get_wechatfans_data] starting ..."
    try:
        hostname ="localhost:8000"
        conn = httplib.HTTPConnection(hostname)
        connnectString = '/wechatfans/sub_detail'
        conn.request("GET",connnectString)
        r1 = conn.getresponse()
        conn.close()
        print "[INFO][get_wechatfans_data] ending ..."
    except Exception, e:
        print "[ERROR][get_wechatfans_data] %s", e


if __name__ == "__main__":

    while True:
        try:
            print datetime.now().strftime("%H:%M"),datetime.now().strftime("%H:%M") == '13:37'
            if datetime.now().strftime("%H:%M") == '13:37':
                print datetime.now().strftime("%H:%M") == '13:37'
                get_wechatfans_data()
                updateAllShopProfit()
            time.sleep(59)
        except:
            print "error"


