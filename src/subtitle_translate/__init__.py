"""Subtitle Translate Module."""

# Programmed by CoolCat467

from __future__ import annotations

# Subtitle Translate Module
# Copyright (C) 2024  CoolCat467
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__title__ = "Subtitle Translator"
__author__ = "CoolCat467"
__license__ = "GNU General Public License Version 3"

from subtitle_translate.main import (
    __version__ as __version__,
    cli_run,
)

if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.\n")
    cli_run()
