import importlib


COLLECTOR_MODULES = [
    "etl.collectors.berth_facility",
    "etl.collectors.berth_status",
    "etl.collectors.route_gis",
    "etl.collectors.statistics",
    "etl.collectors.tank_terminal",
    "etl.collectors.vessel_event",
    "etl.collectors.vessel_position",
    "etl.collectors.weather",
]


def test_collector_modules_import_without_error() -> None:
    for module_name in COLLECTOR_MODULES:
        module = importlib.import_module(module_name)
        assert module is not None
