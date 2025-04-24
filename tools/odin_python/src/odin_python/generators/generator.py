from .abstract_generator import ModelContext
from .c.generator import CGenerator
from .db.generator import ODIN_DB_generator
from .py.generator import PYGenerator
from .pdf.generator import DocGenerator

import os


def default_generator(
    name: str,
    model_context: ModelContext,
    output_dir: str,
    doc: bool,
    db: bool,
    py: bool,
    c: bool,
):
    # Generate C code
    if c:
        c_generator = CGenerator(CGenerator.Config())
        c_generator.generate(
            model_context=model_context,
            output_path=os.path.join(output_dir, f"{name}.c"),
            type="source",
        )

        c_generator.generate(
            model_context=model_context,
            output_path=os.path.join(output_dir, f"{name}.h"),
            type="header",
        )

    if py:
        py_generator = PYGenerator(PYGenerator.Config())
        py_generator.generate(
            model_context=model_context,
            output_path=os.path.join(output_dir, f"{name}.py"),
        )

    if db:
        db_generator = ODIN_DB_generator(ODIN_DB_generator.Config())
        db_generator.generate(
            model_context=model_context,
            output_path=os.path.join(output_dir, f"{name}.db"),
        )

    if doc:
        doc_generator = DocGenerator(DocGenerator.Config())
        doc_generator.generate(
            model_context=model_context,
            output_path=os.path.join(output_dir, f"{name}.pdf"),
        )
