# Сравнение производительности

## Выводы команд

### Статика через nginx
ab -n 1000 -c 100 http://localhost/static/test.html
This is ApacheBench, Version 2.3 <$Revision: 1903618 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
Completed 800 requests
Completed 900 requests
Completed 1000 requests
Finished 1000 requests


Server Software:        nginx/1.31.1
Server Hostname:        localhost
Server Port:            80

Document Path:          /static/test.html
Document Length:        80 bytes

Concurrency Level:      100
Time taken for tests:   1.558 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      453000 bytes
HTML transferred:       80000 bytes
Requests per second:    641.68 [#/sec] (mean)
Time per request:       155.842 [ms] (mean)
Time per request:       1.558 [ms] (mean, across all concurrent requests)
Transfer rate:          283.87 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.6      0       3
Processing:     2  149  30.2    152     185
Waiting:        2  149  30.2    152     185
Total:          5  149  29.8    153     185

Percentage of the requests served within a certain time (ms)
  50%    153
  66%    156
  75%    166
  80%    174
  90%    182
  95%    184
  98%    185
  99%    185
 100%    185 (longest request)

### Статика через gunicorn

his is ApacheBench, Version 2.3 <$Revision: 1903618 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
Completed 800 requests
Completed 900 requests
Completed 1000 requests
Finished 1000 requests


Server Software:        WSGIServer/0.2
Server Hostname:        localhost
Server Port:            8000

Document Path:          /static/test.html
Document Length:        80 bytes

Concurrency Level:      100
Time taken for tests:   68.451 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      318000 bytes
HTML transferred:       80000 bytes
Requests per second:    14.61 [#/sec] (mean)
Time per request:       6845.078 [ms] (mean)
Time per request:       68.451 [ms] (mean, across all concurrent requests)
Transfer rate:          4.54 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.9      0       5
Processing:    11 6486 1410.4   7170    7329
Waiting:        6 6481 1410.0   7164    7323
Total:         11 6486 1409.6   7170    7329

Percentage of the requests served within a certain time (ms)
  50%   7170
  66%   7273
  75%   7276
  80%   7277
  90%   7280
  95%   7284
  98%   7288
  99%   7291
 100%   7329 (longest request)

### Динамика через gunicorn

 ab -n 1000 -c 100 http://localhost:8000/dyn-test/
This is ApacheBench, Version 2.3 <$Revision: 1903618 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
Completed 800 requests
Completed 900 requests
Completed 1000 requests
Finished 1000 requests


Server Software:        gunicorn
Server Hostname:        localhost
Server Port:            8000

Document Path:          /dyn-test/
Document Length:        80 bytes

Concurrency Level:      100
Time taken for tests:   1.236 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      360000 bytes
HTML transferred:       80000 bytes
Requests per second:    808.99 [#/sec] (mean)
Time per request:       123.610 [ms] (mean)
Time per request:       1.236 [ms] (mean, across all concurrent requests)
Transfer rate:          284.41 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.6      0       3
Processing:     4  117  21.6    118     144
Waiting:        4  116  21.6    118     144
Total:          7  117  21.1    118     144

Percentage of the requests served within a certain time (ms)
  50%    118
  66%    125
  75%    130
  80%    131
  90%    136
  95%    140
  98%    142
  99%    143
 100%    144 (longest request)

### Отдача динамического документа через проксирование без кэша:

  ab -n 1000 -c 100 -H "Cache-Control: no-cache" http://localhost/dyn-test/
This is ApacheBench, Version 2.3 <$Revision: 1903618 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
Completed 800 requests
Completed 900 requests
Completed 1000 requests
Finished 1000 requests


Server Software:        nginx/1.31.1
Server Hostname:        localhost
Server Port:            80

Document Path:          /dyn-test/
Document Length:        80 bytes

Concurrency Level:      100
Time taken for tests:   1.116 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      364000 bytes
HTML transferred:       80000 bytes
Requests per second:    896.30 [#/sec] (mean)
Time per request:       111.569 [ms] (mean)
Time per request:       1.116 [ms] (mean, across all concurrent requests)
Transfer rate:          318.61 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.6      0       3
Processing:     4  106  19.3    104     125
Waiting:        4  106  19.3    104     125
Total:          7  106  18.8    104     127

Percentage of the requests served within a certain time (ms)
  50%    104
  66%    117
  75%    120
  80%    121
  90%    123
  95%    123
  98%    124
  99%    124
 100%    127 (longest request)

### Отдача динамического документа через проксирование c кэшем

ab -n 1000 -c 100 http://localhost/cache-dyn/
This is ApacheBench, Version 2.3 <$Revision: 1903618 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)
Completed 100 requests
Completed 200 requests
Completed 300 requests
Completed 400 requests
Completed 500 requests
Completed 600 requests
Completed 700 requests
Completed 800 requests
Completed 900 requests
Completed 1000 requests
Finished 1000 requests


Server Software:        nginx/1.31.1
Server Hostname:        localhost
Server Port:            80

Document Path:          /cache-dyn/
Document Length:        80 bytes

Concurrency Level:      100
Time taken for tests:   0.176 seconds
Complete requests:      1000
Failed requests:        0
Total transferred:      364000 bytes
HTML transferred:       80000 bytes
Requests per second:    5672.76 [#/sec] (mean)
Time per request:       17.628 [ms] (mean)
Time per request:       0.176 [ms] (mean, across all concurrent requests)
Transfer rate:          2016.49 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.7      0       3
Processing:     1   16   3.2     16      19
Waiting:        1   16   3.3     16      19
Total:          4   16   2.6     16      19

Percentage of the requests served within a certain time (ms)
  50%     16
  66%     17
  75%     17
  80%     17
  90%     18
  95%     19
  98%     19
  99%     19
 100%     19 (longest request)

## Ответы на вопросы

### Насколько быстрее отдается статика по сравнению с WSGI?

- 641 / 14 ~ 45.79 

### Во сколько раз ускоряет работу proxy_cache?

- 5672 / 896 ~ 6.3