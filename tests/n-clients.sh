# Create a client with both memcached,tcp and perform operations simultaneously
python3 ./clientTest.py $1 memcached &

python3 ./clientTest.py $1 tcp &

python3 ./clientTest.py $1 memcached &
 
python3 ./clientTest.py $1 tcp & 
 
python3 ./clientTest.py $1 memcached & 
 