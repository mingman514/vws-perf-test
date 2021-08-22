echo comnet02 | sudo kill -9 $(docker top vws_main | pgrep vws)
echo comnet02 | sudo kill -9 $(docker top perf_router | pgrep router)
