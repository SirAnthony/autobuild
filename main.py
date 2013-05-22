#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Load logging system
from builder import settings
from builder.config import run_commands, BaseConfig

# Create default config
default_config = BaseConfig()


# Check for home path existence or create it
if not os.path.isdir(settings.USER_PATH):
    os.mkdir(settings.USER_PATH)


logging.info("Processing commands.")
manager.process(run_commands, default_config)


default_config.save()
sys.exit(0)
