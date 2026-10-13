"""Einmalige tatsächliche Cleanupuhr; kein SQL oder Prozessstart beim Import."""
import math,time

SECONDS=60
REAP_SECONDS=2

def guard_constants():
    if type(SECONDS)is not int or SECONDS!=60 or type(REAP_SECONDS)is not int or REAP_SECONDS!=2:
        raise ValueError('CLEANUP_FIXED_CONSTANTS')

class SharedCleanupWindow:
    __slots__=('_started','_end')
    def __init__(self):
        guard_constants()
        if hasattr(self,'_started')or hasattr(self,'_end'):raise ValueError('CLEANUP_ALREADY_INITIALIZED')
        object.__setattr__(self,'_started',None);object.__setattr__(self,'_end',None)
    def __setattr__(self,name,value):
        raise AttributeError('CLEANUP_WINDOW_READ_ONLY')
    def snapshot(self):
        guard_constants()
        start,end=self._started,self._end
        if start is None and end is None:
            return {'Status':'NOT_STARTED','StartedMonotonic':None,'DeadlineMonotonic':None,'Seconds':SECONDS}
        if type(start)is not float or type(end)is not float or not math.isfinite(start)or not math.isfinite(end)or end!=start+SECONDS:
            raise ValueError('CLEANUP_WINDOW_STATE')
        return {'Status':'ACTUAL_STARTED','StartedMonotonic':start,'DeadlineMonotonic':end,'Seconds':SECONDS}
    def begin(self):
        state=self.snapshot()
        if state['Status']=='NOT_STARTED':
            now=time.monotonic()
            if type(now)is not float or not math.isfinite(now):raise ValueError('CLEANUP_CLOCK')
            object.__setattr__(self,'_started',now);object.__setattr__(self,'_end',now+SECONDS)
        return self.snapshot()
    def remaining(self,cap):
        number(cap,'CLEANUP_CAP')
        state=self.snapshot()
        if state['Status']!='ACTUAL_STARTED':raise ValueError('CLEANUP_NOT_STARTED')
        remaining=min(cap,state['DeadlineMonotonic']-time.monotonic())
        if remaining<=0:raise TimeoutError('CLEANUP_EXPIRED')
        return remaining
    @property
    def deadline(self):
        state=self.snapshot()
        if state['Status']!='ACTUAL_STARTED':raise ValueError('CLEANUP_NOT_STARTED')
        return state['DeadlineMonotonic']

def number(value,code):
    guard_constants()
    if type(value)not in (int,float)or not math.isfinite(value)or not 0<value<=SECONDS:raise ValueError(code)

def validate_window(window):
    guard_constants()
    if type(window)is not SharedCleanupWindow or window.snapshot()['Status']!='NOT_STARTED':raise ValueError('FIXED_NEW_CLEANUP_WINDOW')

def validate_call(deadline,timeout_seconds):
    number(timeout_seconds,'FIXED_ROLE_TIMEOUT')
    now=time.monotonic()
    if type(deadline)not in (int,float)or not math.isfinite(deadline)or deadline>now+timeout_seconds:raise ValueError('FIXED_ROLE_ABSOLUTE_DEADLINE')
    if deadline-now<=REAP_SECONDS:raise TimeoutError('ROLE_PRIMARY_WINDOW_EXHAUSTED')
    return deadline
