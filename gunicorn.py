PIDDIR = '/var/run/switchbot_meter_exporter/'
LOGDIR = '/var/log/switchbot_meter_exporter/'

raw_env = [
    'APPENV=production'
]

bind = '127.0.0.1:9234'
backlog = 2048
workers = 2
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2
threads = 2
spew = False
pidfile = PIDDIR + 'gunicorn.pid'
umask = 0
user = 'root'
group = 'root'
tmp_upload_dir = None
accesslog = LOGDIR + 'access.log'
errorlog = LOGDIR + 'error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)ss'
proc_name = 'switchbot_meter_exporter'

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    pass

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")
    # get traceback info
    import sys
    import threading
    import traceback
    id2name = dict([(th.ident, th.name) for th in threading.enumerate()])
    code = []
    for threadId, stack in list(sys._current_frames().items()):
        code.append("\n# Thread: %s(%d)" % (id2name.get(threadId, ""), threadId))
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    worker.log.debug("\n".join(code))

def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")
