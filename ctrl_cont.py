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
save_path = '/freeflow/test_result/test1'

SCENARIO_NUM = 1
TEST_NUM = 1        # just in case
SUB_TASK_NUM = 1    # just in case
TESTNAME = 'PostCnt'
CONT_NAME = 'vws_node1'
TEST_TYPE = ''
MSG_SIZE = 1    # No use because of -a option
QPNUM = 4       # default 4
MAX_POST_CNT = 1


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
    return '{}-{}-{}_{}_{}_{}_{}_{}_{}'.format(
            SCENARIO_NUM, TEST_NUM, SUB_TASK_NUM, TESTNAME, CONT_NAME,
            TEST_TYPE, MSG_SIZE, QPNUM, MAX_POST_CNT
            )

def clean_process(cont):
    vc.kill_cont_process(cont, 'ib_send')
    vc.kill_cont_process(cont, 'ib_write')
    vc.kill_cont_process(cont, 'ib_read')
    print('CLEAN ZOMBIE PROCESSES')

if __name__ == '__main__':

    # Create cont
    """ 
    node_type = 'vws'
    cmd = ''
    i=3
    while i <= 17:
        if node_type == 'vws':
            cmd = 'sudo docker run --name vws_node{} -h vws_node{} --net weave -e "FFR_NAME=perf_router" -e "FFR_ID={}" -e "TENANT_ID={}" -e "LD_LIBRARY_PATH=/usr/lib" -e --ipc=container:perf_router -v /sys/class/:/sys/class/ -v /freeflow:/freeflow -v /dev/:/dev/ --privileged --device=/dev/infiniband/uverbs0 --device=/dev/infiniband/rdma_cm -it -d vws_node:fifth /bin/bash'.format(i, i, i, i)
        else:
            cmd = 'sudo docker run --name ff_node{} -h ff_node{} --net weave -e "FFR_NAME=perf_router" -e "FFR_ID={}" -e "LD_LIBRARY_PATH=/usr/lib" -e --ipc=container:perf_router -v /sys/class/:/sys/class/ -v /freeflow:/freeflow -v /dev/:/dev/ --privileged --device=/dev/infiniband/uverbs0 --device=/dev/infiniband/rdma_cm -it -d ff_node:third /bin/bash'.format(i, i, i)
        print(cmd)
        bash(cmd)
        i += 1
    """
    # Update cont
#    """
    i=3
    while i <= 17:
        bash('docker exec vws_node{} sh -c "cd /freeflow/vws_freeflow ; ./build-service.sh"'.format(i))
        i+=1
#    """

    # Remove cont
    """
    i=2
    while i <= 17:
        print('docker rm -f vws_node{}'.format(i))
        bash('docker rm -f vws_node{}'.format(i))
        i+=1
    """
   
    # Run test
    """
    i = 1
    while i <= 3: # 1 vs 2~3
        print('docker exec -d vws_node{} sh -lc "python3 /freeflow/scripts/vws_test3-cont.py sb 2"'.format(i))
        bash('docker exec -d vws_node{} sh -lc "python3 /freeflow/scripts/vws_test3-cont.py sb 2"'.format(i))

        i += 1
    """
    
