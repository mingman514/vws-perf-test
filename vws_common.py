from pybash import bash, bash_return
import time

PASSWD = 'comnet02'

############################################
# Basic
############################################
def get_self_ip():
    ip_list = bash_return('hostname -I').decode('utf-8')
    ip = ip_list.split(' ')

    ip10 = ''
    for _ip in ip:
        if _ip[0:3] == '10.':
            ip10 = _ip
            break

    return ip10

def restart_cont(cont):
    bash('docker restart ' + cont)

def async_wait(cont, job, TIME_LIMIT=0):
    limit = 0
    print('Waiting for [{}] to finish [{}]'.format(cont, job))
    FLAG = 1
    while(FLAG):
        try:
            processing = bash_return('docker top ' + cont + ' | pgrep ' + job)
#            print('processing: ', processing)
        except:
            FLAG = 0
        time.sleep(1)
        if TIME_LIMIT <= 0:
            limit += 1
            continue
        elif limit < TIME_LIMIT:
            limit += 1
            if limit % 5 == 0:
                print('Time waiting: {}s'.format(limit))
        else:
            return 1

    print('Finished [{}] of [{}] in {}s.'.format(cont, job, limit))
    return 0
        

def replace_line(cont, filepath, linenum, content):
    # Be cautious specify the text as unique as possible!
    # This might change unexpected tests
    line = bash_return('docker exec {} sh -c "sed -n \'{}p\' {}"'.format(cont, str(linenum), filepath)).decode('utf-8')
    line = line.strip()

    bash('docker exec {} sh -c "sed -i \'{}s/{}/{}/\' {}"'.format(cont, str(linenum), line, content, filepath))

    filename = filepath.split('/')[-1]
    print('File [{}] edited'.format(filename))
    print('[{}]  --> [{}]'.format(line, content))

def build_using_sh(cont, filepath):
    # Usage
    # build_using_sh('vws_node1', '/freeflow/vws_freeflow/libvws/build.sh')
    path = '/'.join(filepath.split('/')[:-1])
    filename = filepath.split('/')[-1]
    bash('docker exec {} sh -c "cd {}; ./{}"'.format(cont, path, filename))


def mkdir(path):
    bash('mkdir {}'.format(path))

def mkdir_in_cont(cont, path):
    bash('docker exec {} sh -c "mkdir {}"'.format(cont, path))

def test_t_translate(test):
    testname = ''
    if test == 'sb':
        testname = 'ib_send_bw'
    elif test == 'sl':
        testname = 'ib_send_lat'
    elif test == 'wb':
        testname = 'ib_write_bw'
    elif test == 'wl':
        testname = 'ib_write_lat'
    elif test == 'rb':
        testname = 'ib_read_bw'
    elif test == 'rl':
        testname = 'ib_read_lat'
    else:
        print('Invalid testing format. (Use one of sb/sl/wb/wl/rb/rl)')
        exit(-1)
    return testname

def kill_cont_process(cont, target):
    bash('echo {} | sudo -S kill -9 $(docker top {} | pgrep {})'.format(PASSWD, cont, target))

############################################
# Router
############################################
def open_router():
    # [Caution] prone to container settings
    host_ip = get_self_ip()

    bash('docker exec -e HOST_IP_PREFIX={}/24 -d perf_router /freeflow/vws_freeflow/ffrouter/router perf_router'.format(host_ip))


def close_router(cont_name='perf_router'):
    #restart_cont(cont_name)
    kill_cont_process(cont_name, 'router')
    

def restart_router():
    print('#### RESTART ROUTER ####')
    close_router()
    open_router()

############################################
# VWS-shm
############################################
def open_vwsshm():
    bash('docker exec -d vws_main sh -c "cd /freeflow/vws_freeflow/libvws ; ./run_vws.sh"')

def close_vwsshm(cont_name='vws_main'):
    #restart_cont(cont_name)
    kill_cont_process(cont_name, 'vws')
    
def restart_vwsshm():
    print('#### RESTART VWSSHM ####')
    close_vwsshm()
    open_vwsshm()

def build_libvws():
    bash('docker exec vws_main sh -c "cd /freeflow/vws_freeflow/libvws; gcc -o libmallochook.so -fPIC -shared malloc_hook.c -lrt"')
    build_using_sh('vws_main', '/freeflow/vws_freeflow/libvws/build.sh')
    build_using_sh('vws_node1', '/freeflow/vws_freeflow/libvws/build.sh')
      
def kill_ib():
    bash('echo comnet02 | sudo kill -9 $(top | pgrep ib_send)')
    bash('echo comnet02 | sudo kill -9 $(top | pgrep ib_read)')
    bash('echo comnet02 | sudo kill -9 $(top | pgrep ib_write)')

############################################
# Perf test
############################################
def perf_test(cont_name, test, option, timelimit, TESTING=False):
    """
    ex. ib_send_bw -S 3 -Q 1 -a
        -> perf_test('vws_node1', 'sb', '-S 3 -Q 1 -a')
    """
    testname = test_t_translate(test)
    if TESTING:
        print('[perf_test] {} {}'.format(testname, option))
        return;
    else:
        print('[perf_test] {} {}'.format(testname, option))
        bash('docker exec -d {} sh -c "stdbuf -o0 {} {};"'.format(cont_name, testname, option))
    status = async_wait(cont_name, testname, timelimit)
    if status > 0:
        print('Not responding... restart program')
        kill_ib()    
        restart_router()
        restart_vwsshm()

        time.sleep(5)
        perf_test(cont_name, test, option, timelimit)
    if '>' in option:
        res_path = option.split('> ')[1]
        bash('cat {}'.format(res_path))
    print('Wait for program ends')
    time.sleep(5)

def perf_test_gen_traffic(cont_name, test, option, timelimit, TESTING=False):
    """
    ex. ib_send_bw -S 3 -Q 1 -a
        -> perf_test('vws_node1', 'sb', '-S 3 -Q 1 -a')
    """
    testname = test_t_translate(test)
    if TESTING:
        print('[perf_test] {} {}'.format(testname, option))
        return;
    else:
        print('[perf_test] {} {}'.format(testname, option))
        bash('docker exec -d {} sh -c "stdbuf -o0 {} {};"'.format(cont_name, testname, option))

    # wait until lat program executed
    FLAG = 1
    while(FLAG):
        try:
            processing = bash_return('docker top ' + cont_name + ' | pgrep lat')
            print('lat program started')
            FLAG = 0
        except:
            FLAG = 1
        time.sleep(1)
    # wait until lat program terminated
    status = async_wait(cont_name, 'lat', timelimit)

    if '>' in option:
        res_path = option.split('> ')[1]
        bash('cat {}'.format(res_path))
    print('Wait for program ends')
    time.sleep(5)
           
# How to implement waiting until the 'exec' end?
# Or, I must always care about the runtime...

#    print(bash_return('docker wait {}'.format(cont_name)))
    
    

# To-Do
# - multi-threading for running multi-jobs at the same time
# - saving result file
# - create container

if __name__ == '__main__':
    replace_line('vws_node1', '/freeflow/vws_freeflow/libvws/libvws.h', 57, '#define TRMQ_POLL_TH 5')
#    restart_router()
#    restart_vwsshm()
#    time.sleep(10)
#    perf_test('vws_node1', 'sb', '-S 3 -Q 1 -a 10.32.0.2')
#    restart_router()
#    restart_vwsshm()

#    build_using_sh('vws_node1', '/freeflow/vws_freeflow/libvws/build.sh')
#    async_wait('vws_node1', 'build.sh')

