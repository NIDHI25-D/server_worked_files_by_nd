WORKERS
--------


https://www.cybrosys.com/blog/how-to-optimize-an-odoo-server-postgresql
https://www.odoo.com/forum/help-1/confused-about-limit-memory-hard-and-soft-232694

free kilobyte
conf byte 
--limit-memory-soft <limit>
Maximum allowed virtual memory per worker. If the limit is exceeded, the worker is killed and recycled at the end of the current request.
Defaults to 2048MB.

--limit-memory-hard <limit>
Hard limit on virtual memory, any worker exceeding the limit will be immediately killed without waiting for the end of the current request processing.
Defaults to 2560MB.

cpu-core = 6
RAM = 20 GB
worker = (6 * 2 )+1 = 13
2 worker for internal process
1 worker for cron
10 to allocate
10  2048  1024 * 1024 = limit_memory_soft
10  2560  1024 * 1024 = limit_memory_hard

limit_time_cpu = 60000
limit_time_real = 60000

limit_memory_hard = 18790481920
limit_memory_soft = 15032385536
 
 
4006740096
3006740096
