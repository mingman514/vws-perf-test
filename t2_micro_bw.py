from pybash import bash
import vws_common as vc
import sys
import time

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
save_path = '/freeflow/test_result/test2/bw'

SCENARIO_NUM = 2
TEST_NUM = 1        # just in case
SUB_TASK_NUM = 1    # just in case
TESTNAME = 'MicroBW'
CONT_NAME = 'vws_node1'
TEST_TYPE = ''
MSG_SIZE = 1    # No use because of -a option
QPNUM = 4       # default 4
#POST_CNT = 1


################################
## Global Variables
################################
SERVER = 0
CLIENT = 1

def initialize(target):
    vc.restart_router()
    vc.restart_vwsshm()
    clean_process(target)
    time.sleep(5)

def name_generator():
    return '{}-{}-{}_{}_{}_{}_{}_{}'.format(
            SCENARIO_NUM, TEST_NUM, SUB_TASK_NUM, TESTNAME, CONT_NAME,
            TEST_TYPE, MSG_SIZE, QPNUM
            )

def clean_process(cont):
    vc.kill_cont_process(cont, 'ib_send')
    vc.kill_cont_process(cont, 'ib_write')
    vc.kill_cont_process(cont, 'ib_read')
    print('CLEAN ZOMBIE PROCESSES')

if __name__ == '__main__':

#    if len(sys.argv) <= 0:
#        print('Need more argument!')
#        exit(-1)

    Iam = SERVER if vc.get_self_ip() == server else CLIENT

    # Variables
    # MSG_SIZE, TEST_TYPE when POST_CNT = 8
    vc.replace_line('vws_main', base_path + '/libvws/libvws.h', 54, '#define MAX_POST_CNT 8')
    vc.build_libvws()

    default_opt = '-S 3 -Q 1'
    test_list = ['sb', 'rb', 'wb']
    target = 'vws_node1'


    while(MSG_SIZE <= 4194304): # 4MB
        for test_t in test_list:
            TEST_TYPE = test_t

            # Initialize
            initialize(target)

            # Naming
            f = name_generator()
    
            # Option
            opt = default_opt            
            repeat = 100000 if MSG_SIZE < 65536 else int(2147483648 / MSG_SIZE)
            opt += ' -n ' + str(repeat)
            opt += ' -s ' + str(MSG_SIZE)
            opt += ' -q 4'
            if Iam == CLIENT:
                opt += ' 10.32.0.5' # it might be a good idea to map all the pairs
                opt += ' > {}/{}'.format(save_path, f)

            # 4. Run test
            print(opt)
            if Iam == CLIENT:
                print('Sleep for sync')
                time.sleep(1)

            vc.perf_test(target, test_t, opt, 0, False)

        MSG_SIZE *= 4



