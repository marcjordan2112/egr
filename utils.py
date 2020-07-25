import queue
import sys
import threading
import time
import traceback


################################################################################
if 'linux' == sys.platform or 'linux2' == sys.platform:
    _PLATFORM = 'linux'
elif 'win32' == sys.platform:
    _PLATFORM = 'windows'
else:
    raise OSError('%s platform not supported' % sys.platform)


################################################################################
def fore_fromhex(text, hexcode):
    """print in a hex defined color"""
    if isinstance(hexcode, int):
        red = 0xFF & (hexcode >> 16)
        green = 0xFF & (hexcode >> 8)
        blue = 0xFF & hexcode
    else:
        red = int(hexcode[0:2], 16)
        green = int(hexcode[2:4], 16)
        blue = int(hexcode[4:6], 16)

    s = "\x1B[38;2;{};{};{}m{}\x1B[0m".format(red, green, blue, text)
    return s


################################################################################
class MyThreadError(Exception):
    pass


class MyThreadStopError(MyThreadError):
    pass


class MyThreadStartError(MyThreadError):
    pass


################################################################################
class ThreadSafePrint(object):
    ############################################################################
    def __init__(
            self,
            prefix='',
            debug=False,
            fore_print_debug_hex=0x1E90FF,
            fore_print_error_hex=0xDC143C,
            get_block_timeout=2.0,
            put_block_timeout=None):
        self._prefix = prefix
        self._debug = debug
        self._fore_print_debug_hex = fore_print_debug_hex
        self._fore_print_error_hex = fore_print_error_hex
        self._get_block_timeout = get_block_timeout
        self._put_block_timeout = put_block_timeout
        self._thread = threading.Thread(target=self._dequeue_thread_method, daemon=True)
        self._lock = threading.Lock()
        self._q = queue.Queue()

        self._thread.start()
        # self._thread.join()

    ############################################################################
    def _dequeue_thread_method(self):
        while True:
            s = None
            try:
                s = self._q.get(block=True, timeout=self._get_block_timeout)
            except queue.Empty:
                pass

            if s is not None:
                print(s)

    ############################################################################
    def debug_enable(self, enable=False):
        self._lock.acquire()
        self._debug = enable
        self._lock.release()

    ############################################################################
    def print(self, s, prefix=''):
        self._lock.acquire()
        # sys.stdout.write(prefix+self._prefix+str(s)+self._lf)
        s = prefix+self._prefix+str(s)
        if self._put_block_timeout is not None:
            self._q.put(s, block=True, timeout=self._put_block_timeout)
        else:
            self._q.put(s, block=False)
        self._lock.release()

    ############################################################################
    def print_debug(self, s, prefix=''):
        if self._debug:
            self._lock.acquire()
            # sys.stdout.write(fore_fromhex(prefix+self._prefix+str(s)+self._lf, self._fore_print_debug_hex))
            s = fore_fromhex(prefix+self._prefix+str(s), self._fore_print_debug_hex)
            if self._put_block_timeout is not None:
                self._q.put(s, block=True, timeout=self._put_block_timeout)
            else:
                self._q.put(s, block=False)
            self._lock.release()

    ############################################################################
    def print_error(self, s, prefix=''):
        self._lock.acquire()
        # sys.stdout.write(fore_fromhex(prefix+self._prefix+str(s)+self._lf, self._fore_print_error_hex))
        s = fore_fromhex(prefix+self._prefix+str(s), self._fore_print_error_hex)
        if self._put_block_timeout is not None:
            self._q.put(s, block=True, timeout=self._put_block_timeout)
        else:
            self._q.put(s, block=False)
        self._lock.release()


################################################################################
#:todo: take tsp out of MyThread params and subclass MyThread to MyThreadTsp or something. Use that for the tsp above.
class MyThread(object):
    _START_SLEEP_TIME = 0.3
    _STOP_SLEEP_TIME = 0.3

    ############################################################################
    def __init__(self, tsp=ThreadSafePrint(debug=False)):
        self._tsp = tsp
        self._started = False
        self._stop = False
        self._stopped = False
        self._thread = None

    ############################################################################
    def _thread_method(self):
        self._started = True
        self._tsp.print_debug('Thread started')
        while True:
            if self._stop:
                break

            try:
                self.thread_method()
            except Exception as exc:
                # There's got to be a better way...
                self._tsp.print_error(traceback.format_exc())
                break

        self._stopped = True
        self._tsp.print_debug('Thread stopped')

    ############################################################################
    def is_stopped(self):
        return self._stopped

    ############################################################################
    def start(self, timeout=None):
        if self._started:
            if self._stopped:
                self._started = False
            else:
                raise MyThreadStartError('Already started.')

        self._thread = threading.Thread(target=self._thread_method, daemon=True)
        self._thread.start()
        if timeout is None:
            return
        timeout_time = time.time() + timeout
        while True:
            if self._started:
                break
            if time.time() > timeout_time:
                raise MyThreadStopError('Timeout starting thread')
            time.sleep(self._START_SLEEP_TIME)

    ############################################################################
    def stop(self, timeout=5.0):
        if not self._started:
            raise MyThreadStopError('Not started')
        self._stop = True
        timeout_time = time.time() + timeout
        while True:
            if self._stopped:
                break
            if time.time() > timeout_time:
                self._thread = None
                raise MyThreadStopError('Timeout stopping thread')
            time.sleep(self._STOP_SLEEP_TIME)
        self._thread = None

    ############################################################################
    def thread_method(self):
        """
        Overload this method.
        :return: None
        """
        pass

