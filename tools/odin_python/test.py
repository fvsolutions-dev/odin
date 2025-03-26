from odin_python.py_generator.entry import BaseRootModel, ODINBaseEntry, ODINEntry, OdinBool, OdinF32, OdinI32

class RootModel(BaseRootModel):
    def __init__(self, interface):
        self.test_float = ODINEntry[OdinF32.BASE_TYPE](0x01000000, cls=OdinF32)
        self.test_int = ODINEntry[OdinI32.BASE_TYPE](0x02000000, cls=OdinI32)
        self.test_bool = ODINEntry[OdinBool.BASE_TYPE](0x03000000, cls=OdinBool)

        class TestGroup(BaseRootModel):
            def __init__(self, interface):
                self.test_float = ODINEntry[OdinF32.BASE_TYPE](0x0A010000, cls=OdinF32)
                self.test_int = ODINEntry[OdinI32.BASE_TYPE](0x0A020000, cls=OdinI32)
                self.test_bool = ODINEntry[OdinBool.BASE_TYPE](0x0A030000, cls=OdinBool)

                class TestSubgroup(BaseRootModel):
                    def __init__(self, interface):
                        self.test_float = ODINEntry[OdinF32.BASE_TYPE](0x0A040100, cls=OdinF32)
                        self.test_int = ODINEntry[OdinI32.BASE_TYPE](0x0A040200, cls=OdinI32)
                        self.test_bool = ODINEntry[OdinBool.BASE_TYPE](0x0A040300, cls=OdinBool)
                        self._children = {
                            'test_float': self.test_float,
                            'test_int': self.test_int,
                            'test_bool': self.test_bool,
                        }
                        super().__init__(interface)
                self.test_subgroup = TestSubgroup(interface)
                self._children = {
                    'test_float': self.test_float,
                    'test_int': self.test_int,
                    'test_bool': self.test_bool,
                    'test_subgroup': self.test_subgroup,
                }
                super().__init__(interface)
        self.test_group = TestGroup(interface)
        self._children = {
            'test_float': self.test_float,
            'test_int': self.test_int,
            'test_bool': self.test_bool,
            'test_group': self.test_group,
        }
        super().__init__(interface)
