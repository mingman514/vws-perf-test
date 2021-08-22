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
server = '10.0.31.2'
base_path = '/freeflow/vws_freeflow'
save_path = '/freeflow/test_result/test3/qp_bw'

SCENARIO_NUM = 2
TEST_NUM = 1        # just in case
SUB_TASK_NUM = 1    # just in case
TESTNAME = 'MultiBW'
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
    bash('kill -9 $(top | pgrep ib_send)')
    bash('kill -9 $(top | pgrep ib_write)')
    bash('kill -9 $(top | pgrep ib_read)')
    print('CLEAN ZOMBIE PROCESSES')

def run(cont, Iam):
    msg_size = MSG_SIZE
    qpnum = QPNUM
    # Option
    """
    notice: -D option not working properly in read&write.
    => measure iteration number by using send/recv
    and use this number as standard
    """
    #default_opt = '-S 3 -Q 1 -n 136257 -s ' + str(MSG_SIZE) # 136257 is near 60 sec
    default_opt = '-S 3 -Q 1 -D 5' # 136257 is near 60 sec
    opt = default_opt

    # CUSTOM DETAIL
    if cont != 'vws_node1':
        qpnum = STD_QPNUM     


    f = name_generator(cont, msg_size, qpnum)
    print('name: ',f)

    if Iam == CLIENT and cont == 'vws_node1':
        opt += ' 10.32.0.2' # it might be a good idea to map all the pairs
        opt += ' > {}/{}'.format(save_path, f)
    elif Iam == CLIENT and cont == 'vws_node2':
        opt += ' 10.32.0.3' # it might be a good idea to map all the pairs
        opt += ' > {}/{}'.format(save_path, f)


    # 4. Run test
    print(opt)
    if Iam == CLIENT:
        print('Sleep for sync')
        time.sleep(3)

    vc.perf_test(cont, test_t, opt, 0)

if __name__ == '__main__':

#    if len(sys.argv) <= 0:
#        print('Need more argument!')
#        exit(-1)

    Iam = SERVER if vc.get_self_ip() == server else CLIENT

# Variables
# MAX_POST_CNT, MSG_SIZE, TEST_TYPE

    test_list = ['wb']
    #test_list = ['sb', 'rb', 'wb']
    containers = ['vws_node1', 'vws_node2']     # chg

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
                proc = Process(target=run, args=(cont, Iam))
                procs.append(proc)
                proc.start()

            for proc in procs:
                proc.join()
            print('--- JOIN COMPLETED ---')
            
        STD_QPNUM *= 2



