import sys
sys.path.insert(0, '/home/saket/requests-new-urllib3-api/requests/packages/')
sys.path.insert(0, '/home/saket/requests-new-urllib3-api')


import requests
from functools import wraps
import tempfile, shutil,time
import os,csv
#__url__="http://mutationassessor.org/?cm=var&var=%s&frm=txt&fts=all"
__url__="http://mutationassessor.org"
def stop_err( msg ):
    sys.stderr.write( '%s\n' % msg )
    sys.exit()

def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):

    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)

        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck, e:
                    #msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    msg = "Retrying in %d seconds..." %  (mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        #print msg
                        pass
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
def main(params):
    with open(params[0],"r") as f:
        for i,sequence in enumerate(f):
            #print sequence
            sequence=sequence.replace("\t",",").replace(" ",",")
            call=requests.get((__url__)%(sequence))
            with open(params[1],"a") as w:
                text = call.content.replace("\\t","\t")
                if i>1:
                    text_split=text.split("\n")
                    text="\t".join(text_split[1])
                w.write(text)
            time.sleep(1)
    return True

def main_web(params):
    tmp_dir = tempfile.mkdtemp()
    path = os.path.join(tmp_dir,"csv_file")
    in_txt = csv.reader(open(params[0],"rb"), delimiter="\t")
    with open(path,"wb") as fp:
        out_csv = csv.writer(fp,delimiter=",")
        out_csv.writerows(in_txt)
    fh = open(path,"rb")
    readfile=fh.read()
    fh.close()
    payload = {"vars":readfile,"tableQ":"","protres":""}
    request = requests.post(__url__,data=payload)
    response = request.text
    temp_file = os.path.join(tmp_dir,"int_file")
    with open(temp_file,"wb") as w:
        w.write(response)

    in_txt = csv.reader(open(temp_file,"rb"), delimiter=",")
    with open(params[1],"wb") as fp:
        out_csv = csv.writer(fp,delimiter="\t")
        out_csv.writerows(in_txt)
    shutil.rmtree(tmp_dir)
    return True
if __name__=="__main__":
    main_web(sys.argv[1:])