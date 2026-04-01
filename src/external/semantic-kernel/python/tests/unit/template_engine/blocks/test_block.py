# Copyright (c) Microsoft. All rights reserved.

from pydantic import ValidationError
from pytest import raises

from semantic_kernel.template_engine.blocks.block import Block

def test_init() -> Any:
    block = Block(content="test content")
    assert block.content == "test content"

def test_content_strip() -> Any:
    block = Block(content=" test content ")
    assert block.content == "test content"

def test_no_content() -> Any:
    with raises(ValidationError):
        Block()
