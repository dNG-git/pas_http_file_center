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

from dNG.controller.predefined_http_request import PredefinedHttpRequest
from dNG.data.file_center.entry import Entry
from dNG.data.http.streaming import Streaming
from dNG.data.http.translatable_error import TranslatableError
from dNG.data.http.translatable_exception import TranslatableException
from dNG.data.hookable_settings import HookableSettings
from dNG.data.ownable_mixin import OwnableMixin as OwnableInstance
from dNG.data.settings import Settings
from dNG.data.streamer.file_like import FileLike
from dNG.data.text.input_filter import InputFilter
from dNG.data.text.l10n import L10n
from dNG.data.xhtml.form.info_field import InfoField
from dNG.data.xhtml.form.view import View as FormView
from dNG.data.xhtml.link import Link
from dNG.database.nothing_matched_exception import NothingMatchedException
from dNG.runtime.io_exception import IOException
from dNG.vfs.implementation import Implementation

from .module import Module

class Index(Module):
#
	"""
Service for "m=file_center"

:author:     direct Netware Group et al.
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: file_center
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	MIMECLASS_ICONS = [ "application", "archive", "audio", "directory", "document", "image", "unknown", "video" ]
	"""
Known mime class icons supported by the file_center CSS sprite.
	"""

	def execute_index(self):
	#
		"""
Action for "index"

:since: v0.1.00
		"""

		if (self.request.is_dsd_set("feid")): self.execute_view()
		else:
		#
			session = (self.request.get_session() if (self.request.is_supported("session")) else None)

			if (session is not None
			    and session.get_user_profile() is not None
			   ): self.execute_root_directory_view()
		#
	#

	def execute_download(self):
	#
		"""
Action for "download"

:since: v0.1.00
		"""

		eid = InputFilter.filter_file_path(self.request.get_dsd("feid", ""))

		L10n.init("pas_http_datalinker")
		L10n.init("pas_http_file_center")

		try: entry = Entry.load_id(eid)
		except NothingMatchedException as handled_exception: raise TranslatableError("pas_http_file_center_eid_invalid", 404, _exception = handled_exception)

		session = (self.request.get_session() if (self.request.is_supported("session")) else None)
		if (session is not None): entry.set_permission_session(session)

		if (not entry.is_readable()):
		#
			if (session is None or session.get_user_profile() is None): raise TranslatableError("pas_http_file_center_eid_invalid", 404)
			else: raise TranslatableError("core_access_denied", 403)
		#

		entry_data = entry.get_data_attributes("title", "vfs_url", "mimetype", "size")
		if (entry_data['vfs_url'] is None): raise TranslatableError("pas_http_file_center_eid_invalid", 404)

		try: vfs_object = Implementation.load_vfs_url(entry_data['vfs_url'], True)
		except IOException as handled_exception: raise TranslatableException("core_unknown_error", _exception = handled_exception)

		download_file_name = InputFilter.filter_file_path(entry_data['title'])

		streamer = FileLike()
		streamer.set_file(vfs_object)

		self.response.set_header("Content-Disposition", "attachment; filename=\"{0}\"".format(download_file_name))
		self.response.set_header("Content-Type", entry_data['mimetype'])
		Streaming.handle(self.request, streamer, self.response)
	#

	def execute_root_directory_view(self):
	#
		"""
Action for "root_directory_view"

:since: v0.1.00
		"""

		session = (self.request.get_session() if (self.request.is_supported("session")) else None)
		user_profile = (None if (session is None) else session.get_user_profile())

		if (user_profile is None): raise TranslatableError("core_access_denied", 403)

		root_directory = Entry.load_or_create_owner_root_directory(user_profile.get_id())
		eid = root_directory.get_id()

		redirect_request = PredefinedHttpRequest()
		redirect_request.set_module("file_center")
		redirect_request.set_action("view")

		redirect_request.set_dsd_dict(self.request.get_dsd_dict())
		redirect_request.set_dsd("feid", eid)

		self.request.redirect(redirect_request)
	#

	def execute_view(self):
	#
		"""
Action for "view"

:since: v0.1.00
		"""

		eid = InputFilter.filter_file_path(self.request.get_dsd("feid", ""))
		page = InputFilter.filter_int(self.request.get_dsd("fpage", 1))
		sort_value = InputFilter.filter_control_chars(self.request.get_dsd("fsort", ""))

		if (eid == ""): eid = Settings.get("pas_http_file_center_view_default", "")

		L10n.init("pas_http_datalinker")
		L10n.init("pas_http_file_center")

		try: entry = Entry.load_id(eid)
		except NothingMatchedException as handled_exception: raise TranslatableError("pas_http_file_center_eid_invalid", 404, _exception = handled_exception)

		session = (self.request.get_session() if (self.request.is_supported("session")) else None)
		if (session is not None): entry.set_permission_session(session)

		if (not entry.is_readable()):
		#
			if (session is None or session.get_user_profile() is None): raise TranslatableError("pas_http_file_center_eid_invalid", 404)
			else: raise TranslatableError("core_access_denied", 403)
		#

		if (self.response.is_supported("html_css_files")):
		#
			self.response.add_theme_css_file("medium_file_center_sprite.min.css")
			self.response.add_theme_css_file("mini_default_sprite.min.css")
		#

		"""
@TODO: Add file center entry functions
		if (entry.is_writable()):
		#
			Link.set_store("servicemenu",
			               (Link.TYPE_RELATIVE_URL | Link.TYPE_JS_REQUIRED),
			               L10n.get("pas_http_file_center_entry_edit"),
			               { "m": "file_center", "s": "entry", "a": "edit", "dsd": { "feid": eid } },
			               icon = "mini-default-option",
			               priority = 3
			              )

			Link.set_store("servicemenu",
			               (Link.TYPE_RELATIVE_URL | Link.TYPE_JS_REQUIRED),
			               L10n.get("pas_http_file_center_entry_delete"),
			               { "m": "file_center", "s": "entry", "a": "delete", "dsd": { "feid": eid } },
			               icon = "mini-default-option",
			               priority = 3
			              )

			if (entry.is_vfs_type(Entry.VFS_TYPE_DIRECTORY)):
			#
				Link.set_store("servicemenu",
				               (Link.TYPE_RELATIVE_URL | Link.TYPE_JS_REQUIRED),
				               L10n.get("pas_http_file_center_entry_new"),
				               { "m": "file_center", "s": "entry", "a": "new", "dsd": { "feid": eid } },
				               icon = "mini-default-option",
				               priority = 3
				              )
			#
		#
		"""

		entry_data = entry.get_data_attributes("id",
		                                       "id_main",
		                                       "title",
		                                       "time_sortable",
		                                       "sub_entries",
		                                       "vfs_url",
		                                       "owner_id",
		                                       "owner_ip",
		                                       "mimeclass",
		                                       "mimetype",
		                                       "size"
		                                      )

		mimeclass_icon = (entry_data['mimeclass']
		                  if (entry_data['mimeclass'] in self.__class__.MIMECLASS_ICONS) else
		                  "unknown"
		                 )

		content = { "id": entry_data['id'],
		            "title": entry_data['title'],
		            "time": entry_data['time_sortable'],
		            "sub_entries_count": entry_data['sub_entries'],
		            "owner": { "id": entry_data['owner_id'], "ip": entry_data['owner_ip'] },
		            "icon_class": "medium-file-center-{0}-icon".format(mimeclass_icon),
		            "mimetype": entry_data['mimetype']
		          }

		if ((not entry.is_vfs_type(Entry.VFS_TYPE_DIRECTORY)) and entry_data['vfs_url'] is not None):
		#
			download_link_params = { "m": "file_center", "a": "download", "dsd": { "feid": eid } }

			Link.set_store("servicemenu",
			               Link.TYPE_RELATIVE_URL,
			               L10n.get("pas_http_file_center_entry_download"),
			               download_link_params,
			               icon = "mini-default-option",
			               priority = 6
			              )

			content['download_link_url'] = Link().build_url(Link.TYPE_RELATIVE_URL, download_link_params)
		#

		form = FormView()

		field = InfoField("fmimetype")
		field.set_title(L10n.get("pas_http_file_center_entry_mime_type"))
		field.set_value(entry_data['mimetype'])

		form.add(field)

		if (entry_data['size'] > 0):
		#
			field = InfoField("fsize")
			field.set_title(L10n.get("pas_http_file_center_entry_size"))
			field.set_value(entry_data['size'])

			form.add(field)
		#

		content['details_form_view'] = { "object": form }

		if (entry_data['sub_entries'] > 0):
		#
			hookable_settings = HookableSettings("dNG.pas.http.file_center.Entry.getListLimit",
			                                     id = entry_data['id']
			                                    )

			limit = hookable_settings.get("pas_http_file_center_entry_list_limit", 20)

			content['sub_entries'] = { "eid": entry_data['id'],
			                           "dsd_page_key": "fpage",
			                           "page": page,
			                           "limit": limit,
			                           "dsd_sort_key": "fsort",
			                           "sort_value": sort_value
			                         }
		#

		entry_parent = entry.load_parent()

		if (entry_parent is not None
		    and ((not isinstance(entry_parent, OwnableInstance))
		         or entry_parent.is_readable_for_session_user(session)
		        )
		   ):
		#
			entry_parent_data = entry_parent.get_data_attributes("id", "id_main", "title")

			if (entry_parent_data['id'] != eid):
			#
				content['parent'] = { "id": entry_parent_data['id'],
				                      "main_id": entry_parent_data['id_main'],
				                      "title": entry_parent_data['title']
				                    }
			#
		#

		self.response.init(True)
		self.response.set_expires_relative(+15)
		self.response.set_title(entry_data['title'])

		self.response.add_oset_content("file_center.entry", content)

		if (self.response.is_supported("html_canonical_url")):
		#
			link_parameters = { "__virtual__": "/file_center/view",
			                    "dsd": { "feid": eid, "fpage": page, "fsort": sort_value }
			                  }

			self.response.set_html_canonical_url(Link().build_url(Link.TYPE_VIRTUAL_PATH, link_parameters))
		#
	#
#

##j## EOF