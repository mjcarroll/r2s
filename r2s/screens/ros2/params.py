from dataclasses import dataclass
import itertools
import time
from typing import List

from textual import log
from textual.app import ComposeResult
from textual.screen import Screen
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable, Footer

from r2s.watcher import WatcherBase
from r2s.widgets import DataGrid, Header

from ros2param import api as r2ParamApi

from rcl_interfaces.msg import ParameterType


@dataclass(frozen=True, eq=False)
class Parameter:
    full_name: str
    param_type: str
    parameter: str
    param_value: str


class ParametersFetched(Message):
    def __init__(self, parameters_list: List[Parameter]) -> None:
        self.parameters_list = parameters_list
        super().__init__()


class ParametersListWatcher(WatcherBase):
    target: Widget
    responses = {}

    def __init__(self, node):
        self.node = node
        super().__init__()

    def run(self) -> None:
        while not self._exit_event.is_set():
            parameters: List[Parameter] = []

            node_names_and_namespaces = self.node.node.get_node_names_and_namespaces()

            for n in node_names_and_namespaces:
                # TODO need to update periodically call and update
                if n[1] in self.responses.keys():
                    continue
                full_name = n[1] + ("" if n[1].endswith("/") else "/") + n[0]
                self.responses[full_name] = r2ParamApi.call_list_parameters(
                    node=self.node.node, node_name=full_name
                )

            time.sleep(0.5)

            for full_name in self.responses.keys():
                response = self.responses[full_name]
                if response is None:
                    continue

                param_names = response.result().result.names
                param_response = r2ParamApi.call_get_parameters(
                    node=self.node.node,
                    node_name=full_name,
                    parameter_names=param_names,
                )

                if not param_response.values:
                    log("Paremeters not set")

                for param_name, pvalue in zip(param_names, param_response.values):
                    if pvalue.type == ParameterType.PARAMETER_BOOL:
                        value = pvalue.bool_value
                    elif pvalue.type == ParameterType.PARAMETER_INTEGER:
                        value = pvalue.integer_value
                    elif pvalue.type == ParameterType.PARAMETER_DOUBLE:
                        value = pvalue.double_value
                    elif pvalue.type == ParameterType.PARAMETER_STRING:
                        value = pvalue.string_value
                    elif pvalue.type == ParameterType.PARAMETER_BYTE_ARRAY:
                        value = pvalue.byte_array_value
                    elif pvalue.type == ParameterType.PARAMETER_BOOL_ARRAY:
                        value = pvalue.bool_array_value
                    elif pvalue.type == ParameterType.PARAMETER_INTEGER_ARRAY:
                        value = pvalue.integer_array_value.tolist()
                    elif pvalue.type == ParameterType.PARAMETER_DOUBLE_ARRAY:
                        value = pvalue.double_array_value.tolist()
                    elif pvalue.type == ParameterType.PARAMETER_STRING_ARRAY:
                        value = pvalue.string_array_value
                    elif pvalue.type == ParameterType.PARAMETER_NOT_SET:
                        value = None
                    else:
                        log(f"Unknown parameter type '{pvalue.type}'")
                        continue

                    param_type = r2ParamApi.get_parameter_type_string(pvalue.type)
                    parameters.append(
                        Parameter(
                            full_name=full_name,
                            param_type=param_type,
                            parameter=param_name,
                            param_value=value,
                        )
                    )

            if len(parameters) > 0:
                self.target.post_message(ParametersFetched(parameters))
            time.sleep(0.2)


class ParametersListGrid(DataGrid):
    id = "parameters_list_table"

    def __init__(self):
        super().__init__(id=self.id)

    def columns(self):
        return ["Node full name", "Type", "Params", "Values"]

    def on_parameters_fetched(self, message: ParametersFetched) -> None:
        message.stop()
        table = self.query_one("#" + self.id, DataTable)
        for param in message.parameters_list:
            row_key = param.full_name + "/" + param.parameter
            if row_key not in table.rows:
                table.add_row(
                    param.full_name,
                    param.param_type,
                    param.parameter,
                    param.param_value,
                    key=row_key,
                )

                # TODO add update to parameter values


class ParametersListScreen(Screen):
    CSS = """
    PackageListScreen {}
    """

    def __init__(self, node):
        self.watcher = ParametersListWatcher(node)
        super().__init__()

    async def on_mount(self) -> None:
        self.watcher.target = self.query_one(ParametersListGrid)
        self.watcher.start()

    def on_unmount(self) -> None:
        self.watcher.close()

    def compose(self) -> ComposeResult:
        yield Header()
        yield ParametersListGrid()
        yield Footer()
