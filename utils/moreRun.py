import queue
import threading
from loguru import logger
from types import MethodType, FunctionType
from concurrent.futures import ThreadPoolExecutor


class MoreRuns:

    def __init__(
        self,
        task_data: list,
        method,
        callback=None,
        max_worker=2,
        log=False,
        ignore_false: bool = False,
    ):
        """
            多线程运行
        :param task_data: 任务数据列表
        :param method: 任务处理方法
        :param callback: 任务完成回调
        :param max_worker: 线程数
        :param log: 是否显示日志
        :param ignore_false: 忽略False返回
        :return:
        """

        self.ignore_false = ignore_false
        self.started_count = 0
        self.finished_count = 0
        assert isinstance(task_data, list)
        assert isinstance(method, MethodType) or isinstance(method, FunctionType)
        assert (
            isinstance(callback, MethodType)
            or isinstance(callback, FunctionType)
            or callback is None
        )
        self.task_data = task_data
        self.tasks_count = len(task_data)
        self.method = method
        self.callback = callback
        self.log = log
        self.tp = ThreadPoolExecutor(max_workers=max_worker)
        self.result_tp = ThreadPoolExecutor(max_workers=1)
        self.run_status = True
        self.exec_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.task_list = []

    def run(self):
        self.task_list = [
            self.tp.submit(self._run_method, task) for task in self.task_data
        ]
        while True:
            try:
                future = self.result_queue.get(timeout=1)
            except queue.Empty:
                pass
            else:
                self._get_result(future)
                if self.finished_count >= self.tasks_count:
                    break
                if not self.exec_queue.empty() and self.result_queue.empty():
                    break

    def stop(self):
        self.exec_queue.put("Termination")
        for task in reversed(self.task_list):
            task.cancel()

    def _get_result(self, future):
        self.finished_count += 1
        if self.log:
            logger.debug(f"结束运行: [{self.finished_count}/{self.tasks_count}]")
        items = future.result()
        if self.callback:
            if self.ignore_false and items is False:
                return
            self.callback(items)

    def _run_method(self, run_data):
        if not self.exec_queue.empty():
            return
        self.started_count += 1
        if self.log:
            logger.debug(
                f"开始运行: [{self.started_count}/{self.tasks_count}]-{threading.current_thread().name}"
            )
            logger.debug(f"运行参数: {run_data}")
        try:
            items = self.method(run_data)
        except Exception as e:
            items = e
        self.result_queue.put(self.result_tp.submit(lambda: items))
