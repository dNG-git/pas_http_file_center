# -*- coding: utf-8 -*-
##j## BOF

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

from dNG.data.file_center.entry import Entry
from dNG.data.hookable_settings import HookableSettings
from dNG.data.http.translatable_exception import TranslatableException
from dNG.data.rfc.basics import Basics as RfcBasics
from dNG.data.text.date_time import DateTime
from dNG.data.text.l10n import L10n
from dNG.data.xhtml.formatting import Formatting as XHtmlFormatting
from dNG.data.xhtml.link import Link
from dNG.data.xhtml.table.data_linker import DataLinker as DataLinkerTable
from dNG.data.xml_parser import XmlParser
from dNG.module.controller.output.table_mixin import TableMixin

from .module import Module

class EntryList(Module, TableMixin):
#
	"""
"EntryList" creates a list of entries.

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: file_center
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	def __init__(self):
	#
		"""
Constructor __init__(EntryList)

:since: v0.1.00
		"""

		Module.__init__(self)
		TableMixin.__init__(self)
	#

	def execute_render(self):
	#
		"""
Action for "render"

:since: v0.1.00
		"""

		if ("id" not in self.context): raise TranslatableException("core_unknown_error", "Missing file center entry ID to render")

		L10n.init("pas_http_datalinker")
		L10n.init("pas_http_file_center")

		self._render(self.context['id'])
	#

	def _get_entry_cell_content(self, content, column_definition):
	#
		"""
Returns content used for entry cell rendering.

:param content: Content already defined
:param column_definition: Column definition for the cell

:return: (dict) Content used for rendering
:since:  v1.0.00
		"""

		_return = content

		link = { "m": "file_center", "dsd": { "feid": content['id'] } }
		_return['link'] = Link().build_url(Link.TYPE_RELATIVE_URL, link)

		_return['owner'] = { "id": content['owner_id'], "ip": content['owner_ip'] }

		return _return
	#

	def _get_size_cell_content(self, content, column_definition):
	#
		"""
Returns content used for size cell rendering.

:param content: Content already defined
:param column_definition: Column definition for the cell

:return: (dict) Content used for rendering
:since:  v0.2.00
		"""

		_return = L10n.get("core_unknown_entity")

		if (content['size'] is not None):
		#
			_return = "{0}{1:d}{2}".format(L10n.get("pas_http_file_center_entry_size_bytes_1"),
			                               content['size'],
			                               L10n.get("pas_http_file_center_entry_size_bytes_2")
			                              )
		#

		return XHtmlFormatting.escape(_return)
	#

	def _get_time_sortable_cell_content(self, content, column_definition):
	#
		"""
Returns content used for "time_sortable" cell rendering.

:param content: Content already defined
:param column_definition: Column definition for the cell

:return: (dict) Content used for rendering
:since:  v0.2.00
		"""

		time_attributes = { "tag": "time", "attributes": { "datetime": "{0}+00:00".format(RfcBasics.get_iso8601_datetime(content['time_sortable'])) } }

		return "{0}{1}</time>".format(XmlParser().dict_to_xml_item_encoder(time_attributes, False),
			                          DateTime.format_l10n(DateTime.TYPE_FUZZY_MONTH, content['time_sortable'])
			                         )
	#

	def _render(self, _id):
	#
		"""
List renderer

:since: v0.1.00
		"""

		entry = Entry.load_id(_id)

		entry_renderer_attributes = { "type": DataLinkerTable.COLUMN_RENDERER_CALLBACK_OSET,
		                              "callback": self._get_entry_cell_content,
		                              "oset_template_name": "file_center.entry_column",
		                              "oset_row_attributes": [ "id",
		                                                       "title",
		                                                       "sub_entries",
		                                                       "sub_entries_type",
		                                                       "vfs_url",
		                                                       "vfs_type",
		                                                       "owner_id",
		                                                       "owner_ip",
		                                                       "mimetype"
		                                                     ]
		                          }

		self.table = DataLinkerTable(entry)

		self.table.add_column("entry",
		                      L10n.get("pas_http_file_center_entry"),
		                      55,
		                      sort_key = "title",
		                      renderer = entry_renderer_attributes
		                     )

		self.table.add_column("time_sortable",
		                      L10n.get("pas_http_datalinker_entry_updated"),
		                      25,
		                      renderer = { "type": DataLinkerTable.COLUMN_RENDERER_CALLBACK,
		                                   "callback": self._get_time_sortable_cell_content
		                                 }
		                     )

		self.table.add_column("size",
		                      L10n.get("pas_http_file_center_entry_size"),
		                      20,
		                      renderer = { "type": DataLinkerTable.COLUMN_RENDERER_CALLBACK,
		                                   "callback": self._get_size_cell_content
		                                 }
		                     )

		hookable_settings = HookableSettings("dNG.pas.http.file_center.EntryList.getLimit",
		                                     id = _id
		                                    )

		limit = hookable_settings.get("pas_http_file_center_entry_list_limit", 25)

		self.table.set_limit(limit)

		self.dsd_page_key = "fpage"
		self.page = self.context.get("page", 1)

		self.dsd_sort_key = "fsort"
		sort_value = self.context.get("sort_value", "")

		if (sort_value != ""):
		#
			self.sort_direction = sort_value[-1:]
			self.sort_column_key = sort_value[:-1]
		#

		self.set_action_result(self._render_table())
	#
#

##j## EOF