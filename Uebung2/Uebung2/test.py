import time

wait_time = time.time() + 5 

print(time.time())

last_time = time.time() +1 
while wait_time > time.time():
    
    if last_time < time.time():
        print(time.time())
        last_time = time.time() +1