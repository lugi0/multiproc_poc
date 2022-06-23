import os
import time
import requests
import json
import pickle
import multiprocessing as mp
from datetime import datetime
#from multiprocessing import multiprocessing, Process, Manager, Pool

def plot_availability(data):
    import matplotlib.pyplot as plt

    plt.style.use('_mpl-gallery')
    x = data.keys()
    y = [0 if x>=500 else 1 for x in data.values()]

    # plot
    fig, ax = plt.subplots()
    ax.plot(x, y, linewidth=2.0)
    ax.set(xticks=[_ for _ in range(len(x))], title='Dashboard uptime',
       ylim=(-1, 2), yticks=[0,1], xlabel='time',
       ylabel='availability')

    plt.tight_layout()
    plt.show()
    plt.savefig('test.png', bbox_inches='tight')

def f_delete():
    os.system("oc delete Pod rhods-dashboard-589cb84c6c-2nxxx -n redhat-ods-applications")
    os.system("oc delete Pod rhods-dashboard-589cb84c6c-x4b4n -n redhat-ods-applications")

def f2(d,endpoint):
    timestamp=datetime.now()
    t=requests.get(endpoint)
    d[str(timestamp)]=t.status_code
    print(timestamp, t.status_code)

def f(d, endpoint, q):
    while True:
        p=mp.Process(target=f2, args=(d,endpoint))
        p.start()
        time.sleep(1)
        if not q.empty(): break

if __name__ == '__main__':
    endpoint = 'https://rhods-dashboard-redhat-ods-applications.apps.qeaisrhods-nsu.3o7d.s1.devshift.org/'
    mp.set_start_method('spawn')
    with mp.Manager() as manager:
        d = manager.dict()
        q = mp.Queue()
        p=mp.Process(target=f, args=(d,endpoint,q))
        p.start()
        time.sleep(5)
        p2=mp.Process(target=f_delete)
        p2.start()
        time.sleep(15)
        while True:
            if d.values()[-1]!=503: break
        time.sleep(5)
        q.put('STOP')
        print("Waiting for process to terminate")
        p.join()
        print(d)
        plot_availability(d)
        with open('temp_log.pkl', 'wb') as f:
            pickle.dump(d, f)
