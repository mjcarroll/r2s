import os

import rclpy
from rclpy.parameter import Parameter

import threading
import time

from textual import log

DEFAULT_TIMEOUT = 0.5
NODE_NAME_PREFIX = "r2s"

RCLPY_INIT: bool = False
RCLPY_NODE = None


class NodeWrapper:

    nodes_and_namespaces = []
    topic_names_and_types = []

    def __init__(self, node_name, *args):
        node_name_suffix = getattr(args, "node_name_suffix", "_%d" % os.getpid())
        start_parameter_services = getattr(args, "start_parameter_services", False)
        use_sim_time = getattr(args, "use_sim_time", False)
        start_type_description_service = getattr(
            args, "start_type_description_service", True
        )

        if node_name is None:
            node_name = NODE_NAME_PREFIX + node_name_suffix

        self.node = rclpy.create_node(
            node_name,
            start_parameter_services=start_parameter_services,
            parameter_overrides=[
                Parameter("use_sim_time", value=use_sim_time),
                Parameter(
                    "start_type_description_service", value=start_type_description_service
                ),
            ],
            automatically_declare_parameters_from_overrides=True,
        )
        self.mutex = threading.Lock()
        self.spinning = True
        self.spinner = threading.Thread(target=self.spin)
        self.spinner.start()

    def stop(self):
        self.mutex.acquire()
        self.spinning = False
        self.spinner.join()
        self.mutex.release()

    def __del__(self):
        self.stop()

    def spin(self):
        log("start spinning")
        while self.spinning:
            log("spin")
            self.mutex.acquire()
            rclpy.spin_once(self.node, timeout_sec=0.1)
            self.nodes_and_namespaces = self.node.get_node_names_and_namespaces()
            self.topic_names_and_types = self.node.get_topic_names_and_types()
            self.mutex.release()

    def get_nodes_and_namespaces(self):
        return self.nodes_and_namespaces

    def get_topic_names_and_types(self):
        return self.topic_names_and_types

def get_node(*args, node_name=None):
    global RCLPY_INIT, RCLPY_NODE

    if not RCLPY_INIT:
        log("Creating context")
        rclpy.init()
        RCLPY_INIT = True

    if not RCLPY_NODE:
        log("Creating node")
        RCLPY_NODE = NodeWrapper(node_name, *args)

    return RCLPY_NODE
