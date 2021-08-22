echo comnet02 | sudo kill -9 $(top | pgrep ib_send)
echo comnet02 | sudo kill -9 $(top | pgrep ib_read)
echo comnet02 | sudo kill -9 $(top | pgrep ib_write)
