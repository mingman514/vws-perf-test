echo comnet02 | sudo kill -9 $(docker top vws_main | pgrep vws)
echo comnet02 | sudo kill -9 $(docker top perf_router | pgrep router)
#echo comnet02 | sudo kill -9 $(top | pgrep ib_send)
#echo comnet02 | sudo kill -9 $(top | pgrep ib_read)
#echo comnet02 | sudo kill -9 $(top | pgrep ib_write)

docker exec -d vws_main sh -c 'cd /freeflow/vws_freeflow/libvws ; ./run_vws.sh'
docker exec -e HOST_IP_PREFIX=10.0.31.2/24 -d perf_router sh -c "/freeflow/vws_freeflow/ffrouter/router  perf_router"
