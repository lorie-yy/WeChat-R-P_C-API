import time
import httplib, urllib
from datetime import datetime,timedelta


def get_wechatfans_data(url):
    print "[INFO][get_wechatfans_data] starting ..."
    try:
        hostname ="localhost:8000"
        conn = httplib.HTTPConnection(hostname)
        connnectString = url
        conn.request("GET",connnectString)
        r1 = conn.getresponse()
        conn.close()
        print "[INFO][get_wechatfans_data] ending ..."
    except Exception, e:
        print "[ERROR][get_wechatfans_data] %s", e


if __name__ == "__main__":

    while True:
        try:
            print datetime.now().strftime("%H:%M"),datetime.now().strftime("%H:%M") == '23:58'
            if datetime.now().strftime("%H:%M") == '23:58':
                print datetime.now().strftime("%H:%M") == '23:58'
                get_wechatfans_data('/wechatfans/update_everybodyprofit')
            get_wechatfans_data('/wechatfans/sub_detail')
            get_wechatfans_data('/wechatfans/update_userprice')
            time.sleep(59)
        except:
            print "error"


