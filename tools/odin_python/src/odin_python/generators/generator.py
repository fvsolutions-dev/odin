from pydantic import Field
from .abstract_generator import ModelContext
from .c.generator import CGenerator
from .db.generator import ODIN_DB_generator
from .py.generator import PYGenerator
from .pdf.generator import DocGenerator
from .abstract_generator import BaseModel
import os


class GeneratorConfigurations(BaseModel):
    class Config:
        extra = "forbid"

    c_generator: CGenerator.Config = Field(
        default_factory=CGenerator.Config,
        description="C generator configuration",
    )
    python_generator: PYGenerator.Config = Field(
        default_factory=PYGenerator.Config,
        description="Python generator configuration",
    )
    doc_generator: DocGenerator.Config = Field(
        default_factory=DocGenerator.Config,
        description="Doc generator configuration",
    )
    db_generator: ODIN_DB_generator.Config = Field(
        default_factory=ODIN_DB_generator.Config,
        description="DB generator configuration",
    )

def default_generator(
    name: str,
    model_context: ModelContext,
    output_dir: str,
    doc: bool,
    db: bool,
    py: bool,
    c: bool,
    generator_config: GeneratorConfigurations,
):
    # Generate C code
    if c:
        c_generator = CGenerator(generator_config.c_generator)
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
        py_generator = PYGenerator(generator_config.python_generator)
        py_generator.generate(
            model_context=model_context,
            output_path=os.path.join(output_dir, f"{name}.py"),
        )

    if db:
        db_generator = ODIN_DB_generator(generator_config.db_generator)
        db_generator.generate(
            model_context=model_context,
            output_path=os.path.join(output_dir, f"{name}.odin"),
        )

    if doc:
        doc_generator = DocGenerator(generator_config.doc_generator)
        doc_generator.generate(
            model_context=model_context,
            output_path=os.path.join(output_dir, f"{name}.pdf"),
        )
