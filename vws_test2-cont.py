from pybash import bash, bash_return
import sys
import time
import vws_common as vc

################################
## Fill basic info below
## (MUST CHECK BEFORE EXECUTE)
################################
server = '10.0.31.2'
base_path = '/freeflow/vws_freeflow'
save_path = '/freeflow/test_result/test2/lat'

SCENARIO_NUM = 2
TEST_NUM = 1        # just in case
SUB_TASK_NUM = 1    # just in case
TESTNAME = 'MicroBW'
CONT_NAME = ''
TEST_TYPE = ''
MSG_SIZE = 0
QPNUM = 4
STD_QPNUM = 1

################################
## Global Variables
################################
SERVER = 0
CLIENT = 1

"""
ipmap = dict(
        '1' = '10.32.0.2',
        '2' = '10.32.0.3',
        '3' = '10.32.0.4',
        '4' = '10.32.0.5',
        '5' = '10.32.0.6',
        '6' = '10.32.0.7',
        '7' = '10.32.0.8',
        '8' = '10.32.0.9',
        '9' = '10.32.0.10',
        '10' = '10.32.0.11'
        )
"""

def name_generator():
    return '{}-{}-{}_{}_{}_{}_{}_{}'.format(
            SCENARIO_NUM, TEST_NUM, SUB_TASK_NUM, TESTNAME, CONT_NAME,
            TEST_TYPE, MSG_SIZE, QPNUM
            )

def get_host():
   ip_list = bash_return('hostname -I').decode('utf-8').split(' ')
   
   for ip in ip_list:
       if ip[0:3] == '10.':
           return ip
   

def get_cont_name():
    return bash_return('hostname').decode('utf-8').strip()

def get_cont_id():
    name = get_cont_name().split('e')   # ff_node / vws_node
    return name[1].strip()

    

# TEST_TYPE, MSG_SIZE    

if __name__ == '__main__':
#    if len(sys.argv) <= 0:
#        print('Need more argument!')
#        exit(-1)

    TEST_TYPE = sys.argv[1]
    MSG_SIZE = sys.argv[2]


    Iam = SERVER if get_host()[3:5] == '32' else CLIENT
    
    CONT_NAME = get_cont_name()  # vws_node1
    cont_id = get_cont_id() # 1
    
    # option
    if TEST_TYPE[1] == 'b':
        default_opt = '-S 3 -Q 1 -D 5 -q ' + str(QPNUM)
    else:
        default_opt = '-S 3 -n 1000000'
        if TEST_TYPE[0] == 's' or TEST_TYPE[0] == 'w':
            default_opt += ' -I 0'
    
    opt = default_opt
    opt += ' -s ' + MSG_SIZE
    f = name_generator()

    if Iam == CLIENT:
        opt += ' 10.32.0.' + str(int(cont_id) + 4)
        if TEST_TYPE[1] == 'b':
            opt += ' > {}/{}'.format(save_path, f)
        time.sleep(1)
 
    print('{} {}'.format(vc.test_t_translate(TEST_TYPE), opt))
    bash('{} {}'.format(vc.test_t_translate(TEST_TYPE), opt))

    if Iam == CLIENT and '>' in opt:
        res_path = opt.split('> ')[1]
        bash('cat {}'.format(res_path))
    
