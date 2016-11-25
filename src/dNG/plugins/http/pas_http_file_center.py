# -*- coding: utf-8 -*-

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;http;file_center

The following license agreement remains valid unless any additions or
changes are being made by direct Netware Group in a written form.

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the
Free Software Foundation; either version 2 of the License, or (at your
option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasHttpFileCenterVersion)#
#echo(__FILEPATH__)#
"""

# pylint: disable=unused-argument

from dNG.data.http.virtual_config import VirtualConfig
from dNG.plugins.hook import Hook

def register_plugin():
    """
Register plugin hooks.

:since: v0.2.00
    """

    Hook.register("dNG.pas.http.Server.onStartup", on_startup)
    Hook.register("dNG.pas.http.Wsgi.onStartup", on_startup)
#

def on_startup(params, last_return = None):
    """
Called for "dNG.pas.http.Server.onStartup" and "dNG.pas.http.Wsgi.onStartup"

:param params: Parameter specified
:param last_return: The return value from the last hook called.

:return: (mixed) Return value
:since:  v0.2.00
    """

    VirtualConfig.set_virtual_path("/file_center/view/", { "m": "file_center", "s": "index", "a": "view", "path_parameters": True })
    return last_return
#

def unregister_plugin():
    """
Unregister plugin hooks.

:since: v0.2.00
    """

    Hook.unregister("dNG.pas.http.Server.onStartup", on_startup)
    Hook.unregister("dNG.pas.http.Wsgi.onStartup", on_startup)
#
