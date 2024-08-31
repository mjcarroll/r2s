import os

import rclpy
from rclpy.parameter import Parameter

DEFAULT_TIMEOUT = 0.5
NODE_NAME_PREFIX = "r2s"


def get_node(*args, node_name=None):
    rclpy.init()
    node_name_suffix = getattr(args, "node_name_suffix", "_%d" % os.getpid())
    start_parameter_services = getattr(args, "start_parameter_services", False)
    use_sim_time = getattr(args, "use_sim_time", False)
    start_type_description_service = getattr(
        args, "start_type_description_service", True
    )

    if node_name is None:
        node_name = NODE_NAME_PREFIX + node_name_suffix

    node = rclpy.create_node(
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

    timeout_reached = False

    def timer_callback():
        nonlocal timeout_reached
        timeout_reached = True

    timeout = getattr(args, "spin_time", DEFAULT_TIMEOUT)
    timer = node.create_timer(timeout, timer_callback)

    while not timeout_reached:
        rclpy.spin_once(node)

    node.destroy_timer(timer)
    return node
