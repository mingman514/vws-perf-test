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
save_path = '/freeflow/test_result/test3/qp_lat'

SCENARIO_NUM = 2
TEST_NUM = 1        # just in case
SUB_TASK_NUM = 1    # just in case
TESTNAME = 'MultiQP'
CONT_NAME = ''
TEST_TYPE = ''
MSG_SIZE = 1048576
QPNUM = 1       
STD_QPNUM = 1

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
            TEST_TYPE, msg_size, qpnum, STD_QPNUM
            )

def clean_process():
#    vc.kill_cont_process(cont, 'ib_send')
#    vc.kill_cont_process(cont, 'ib_write')
#    vc.kill_cont_process(cont, 'ib_read')
    bash('echo comnet02 | sudo kill -9 $(top | pgrep ib_send)')
    bash('echo comnet02 | sudo kill -9 $(top | pgrep ib_read)')
    bash('echo comnet02 | sudo kill -9 $(top | pgrep ib_write)')
    print('CLEAN ZOMBIE PROCESSES')

def run(cont, Iam, test_t):
    cont_id = int(cont[-1])
    msg_size = MSG_SIZE
    qpnum = QPNUM
       
    default_opt = '-S 3'
    # CUSTOM DETAIL
    if cont_id != 1:
        qpnum = STD_QPNUM
        default_opt += ' -Q 1 --run_infinitely -q ' + str(qpnum)
    if cont_id == 1:
        msg_size = 64
        default_opt += ' -n 1000000'
        # wait until traffic flourishes
        time.sleep(5)

    opt = default_opt
    opt += ' -s ' + str(msg_size)


    f = name_generator(cont, msg_size, qpnum)
    print('name: ',f)

    if Iam == CLIENT and cont_id == 1:
        opt += ' 10.36.0.2'
        opt += ' > {}/{}'.format(save_path, f)
    elif Iam == CLIENT and cont_id == 2:
        opt += ' 10.36.0.3'
        #opt += ' > {}/{}'.format(save_path, f)


    # 4. Run test
    print(opt)
    if Iam == CLIENT:
        print('Sleep for sync')
        time.sleep(3)
   
    if cont_id != 1:
        test_t = test_t[0] + 'b'
        vc.perf_test_gen_traffic(cont, test_t, opt, 0, False)
    else: 
        vc.perf_test(cont, test_t, opt, 0, False)

if __name__ == '__main__':

#    if len(sys.argv) <= 0:
#        print('Need more argument!')
#        exit(-1)

    Iam = SERVER if vc.get_self_ip() == server else CLIENT

# Variables
# MAX_POST_CNT, MSG_SIZE, TEST_TYPE

    test_list = ['sl', 'rl', 'wl']
    containers = ['vws_node1']     # chg

    SERVER_NUM = 1
    for i in range(SERVER_NUM):
        s_id = i + 2
        containers.append('vws_node' + str(s_id))

    """
    Filter by STD_QPNUM!
    """
    while(STD_QPNUM <= 256):

        for test_t in test_list:
            TEST_TYPE = test_t
            # for two different containers...

            # Initialize
            initialize(containers)
            procs = []
            for cont in containers:
                proc = Process(target=run, args=(cont, Iam, test_t))
                procs.append(proc)
                proc.start()

            for proc in procs:
                proc.join()
            print('--- JOIN COMPLETED ---')
            
        STD_QPNUM *= 2



