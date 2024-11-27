from odin_python.main_model import TestReader

from new_configs.defs import MINIMAL_CONFIG


def test_basic_parse():
    model = TestReader.from_yaml(MINIMAL_CONFIG)
    print(model.dump_json())
    print(model.dump_summary())


if __name__ == "__main__":
    test_basic_parse()
