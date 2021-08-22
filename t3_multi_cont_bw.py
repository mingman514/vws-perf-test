from pybash import bash
import vws_common as vc
import sys
import time
from multiprocessing import Process
"""
Naming Rule:
    
Columns:
    scenario_num | testname | type(VorD) | cont_name | test | msgsize | qpnum | postcnt
"""



################################
## Fill basic info below
## (MUST CHECK BEFORE EXECUTE)
################################
server = '10.0.35.2'
base_path = '/freeflow/vws_freeflow'
save_path = '/freeflow/test_result/test3/cont_bw'

SCENARIO_NUM = 3
TEST_NUM = 1        # just in case
SUB_TASK_NUM = 1    # just in case
TESTNAME = 'MultiCont'
CONT_NAME = ''
TEST_TYPE = ''
MSG_SIZE = 1048576
QPNUM = 4       
STD_CONTNUM = 1

################################
## Global Variables
################################
SERVER = 0
CLIENT = 1

def initialize(target):
    vc.restart_router()
    vc.restart_vwsshm()
    clean_process()
    #for t in target:
    #    clean_process(t)
    time.sleep(5)

def name_generator(cont, msg_size, qpnum):
    return '{}-{}-{}_{}_{}_{}_{}_{}_{}'.format(
            SCENARIO_NUM, TEST_NUM, SUB_TASK_NUM, TESTNAME, cont,
            TEST_TYPE, msg_size, qpnum, STD_CONTNUM
            )

def clean_process():
    bash('echo comnet02 | sudo kill -9 $(top | pgrep ib_send)')
    bash('echo comnet02 | sudo kill -9 $(top | pgrep ib_read)')
    bash('echo comnet02 | sudo kill -9 $(top | pgrep ib_write)')
    print('CLEAN ZOMBIE PROCESSES')

def run(cont, Iam):
    cont_id = int(cont[-1])
    msg_size = MSG_SIZE
    qpnum = QPNUM
       
    # CUSTOM DETAIL

    default_opt = '-S 3 -Q 1 -D 60'
    opt = default_opt
    opt += ' -s ' + str(MSG_SIZE)
    opt += ' -q ' + str(qpnum)


    f = name_generator(cont, msg_size, qpnum)
    print('name: ',f)

    if Iam == CLIENT:
        opt += ' 10.36.0.' + str(cont_id + 1) # it might be a good idea to map all the pairs
        opt += ' > {}/{}'.format(save_path, f)

    # 4. Run test
    print(opt)
    if Iam == CLIENT:
        print('Sleep for sync')
        time.sleep(2)

    vc.perf_test(cont, test_t, opt, 0, False)

if __name__ == '__main__':

#    if len(sys.argv) <= 0:
#        print('Need more argument!')
#        exit(-1)

    Iam = SERVER if vc.get_self_ip() == server else CLIENT

# Variables
# MAX_POST_CNT, MSG_SIZE, TEST_TYPE

    test_list = ['sb', 'rb', 'wb']
    

    while STD_CONTNUM <= 16:
        containers = ['vws_node1']     # chg

        for i in range(STD_CONTNUM):
            s_id = i + 2
            containers.append('vws_node' + str(s_id))


        for test_t in test_list:
            TEST_TYPE = test_t
            # for two different containers...

            # Initialize
            initialize(containers)
            procs = []
            for cont in containers:
                proc = Process(target=run, args=(cont, Iam))
                procs.append(proc)
                proc.start()

            for proc in procs:
                proc.join()
            print('--- JOIN COMPLETED ---')
            
        STD_CONTNUM *= 2



