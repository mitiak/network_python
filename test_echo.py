#!/usr/bin/env python3

import os
import time

t1 = time.time()
for i in range(3):
    cmd = 'python3 echo_client.py ' + str(i)
    os.system(cmd)

t2 = time.time()

print('----------------------------------')
print('Time Executed[sec]: ' + str(t2-t1))

