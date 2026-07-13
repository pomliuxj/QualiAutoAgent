# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from .loader import load_yaml_config, get_config_file_path
from .tools import SELECTED_SEARCH_ENGINE, SearchEngine
from .questions import BUILT_IN_QUESTIONS, BUILT_IN_QUESTIONS_ZH_CN
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load YAML configuration (LLM models, etc.)
YAML_CONFIG = load_yaml_config(get_config_file_path())

__all__ = [
    "YAML_CONFIG",
    "SELECTED_SEARCH_ENGINE",
    "SearchEngine",
    "BUILT_IN_QUESTIONS",
    "BUILT_IN_QUESTIONS_ZH_CN",
]
