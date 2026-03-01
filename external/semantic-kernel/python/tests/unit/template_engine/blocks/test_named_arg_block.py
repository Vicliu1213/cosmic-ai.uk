# Copyright (c) Microsoft. All rights reserved.

import logging

from pytest import mark, raises

from semantic_kernel.exceptions import NamedArgBlockSyntaxError
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.kernel import Kernel
from semantic_kernel.template_engine.blocks.block_types import BlockTypes
from semantic_kernel.template_engine.blocks.named_arg_block import NamedArgBlock
from semantic_kernel.template_engine.blocks.val_block import ValBlock
from semantic_kernel.template_engine.blocks.var_block import VarBlock

logger = logging.getLogger(__name__)

def test_init_with_var() -> Any:
    named_arg_block = NamedArgBlock(content="test=$test_var")
    assert named_arg_block.content == "test=$test_var"
    assert named_arg_block.name == "test"
    assert named_arg_block.variable.name == "test_var"
    assert isinstance(named_arg_block.variable, VarBlock)

def test_init_with_val() -> Any:
    named_arg_block = NamedArgBlock(content="test='test_val'")
    assert named_arg_block.content == "test='test_val'"
    assert named_arg_block.name == "test"
    assert named_arg_block.value.value == "test_val"
    assert isinstance(named_arg_block.value, ValBlock)

def test_type_property() -> Any:
    named_arg_block = NamedArgBlock(content="test=$test_var")
    assert named_arg_block.type == BlockTypes.NAMED_ARG

@mark.parametrize(
    "content",
    [
        "=$test_var",
        "test=$test-var",
        "test='test_val\"",
        "test=''",
        "test=$",
    ],
    ids=["no_name", "invalid_var", "invalid_val", "empty_val", "empty_var"],
)
def test_syntax_error(content) -> Any:
    match = content.replace("$", "\\$") if "$" in content else content
    with raises(NamedArgBlockSyntaxError, match=rf".*{match}.*"):
        NamedArgBlock(content=content)

def test_render() -> Any:
    named_arg_block = NamedArgBlock(content="test=$test_var")
    rendered_value = named_arg_block.render(Kernel(), KernelArguments(test_var="test_value"))
    assert rendered_value == "test_value"

def test_render_variable_not_found() -> Any:
    named_arg_block = NamedArgBlock(content="test=$test_var")
    rendered_value = named_arg_block.render(Kernel(), KernelArguments())
    assert rendered_value == ""

def test_init_minimal_var() -> Any:
    block = NamedArgBlock(content="a=$a")
    assert block.name == "a"
    assert block.variable.name == "a"

def test_init_minimal_val() -> Any:
    block = NamedArgBlock(content="a='a'")
    assert block.name == "a"
    assert block.value.value == "a"

def test_init_empty() -> Any:
    with raises(NamedArgBlockSyntaxError, match=r".*"):
        NamedArgBlock(content="")

def test_it_trims_spaces() -> Any:
    assert NamedArgBlock(content="  a=$x  ").content == "a=$x"

def test_it_ignores_spaces_around() -> Any:
    target = NamedArgBlock(content="  a=$var \n ")
    assert target.content == "a=$var"

def test_it_renders_to_empty_string_without_variables() -> Any:
    target = NamedArgBlock(content="  a=$var \n ")
    result = target.render(Kernel(), None)
    assert result == ""

def test_it_renders_to_empty_string_if_variable_is_missing() -> Any:
    target = NamedArgBlock(content="  a=$var \n ")
    result = target.render(Kernel(), KernelArguments(foo="bar"))
    assert result == ""

def test_it_renders_to_variable_value_when_available() -> Any:
    target = NamedArgBlock(content="  a=$var \n ")
    result = target.render(Kernel(), KernelArguments(foo="bar", var="able"))
    assert result == "able"

def test_it_renders_to_value() -> Any:
    target = NamedArgBlock(content="  a='var' \n ")
    result = target.render(Kernel(), None)
    assert result == "var"
