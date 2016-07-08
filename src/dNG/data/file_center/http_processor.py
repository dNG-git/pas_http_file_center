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
59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;gpl
----------------------------------------------------------------------------
#echo(pasHttpFileCenterVersion)#
#echo(__FILEPATH__)#
"""

from os import path

from dNG.data.mime_type import MimeType
from dNG.data.text.input_filter import InputFilter

from .entry import Entry

class HttpProcessor(object):
#
	"""
"HttpProcessor" provides HTTP specifc methods for file center entries.

:author:     direct Netware Group et al.
:copyright:  direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: file_center
:since:      v0.1.00
:license:    https://www.direct-netware.de/redirect?licenses;gpl
             GNU General Public License 2
	"""

	@staticmethod
	def new_from_uploaded_file(uploaded_file, timeout = None):
	#
		"""
Creates a new Entry instance for an uploaded file backed by an StoredFile
instance.

:param uploaded_file: Uploaded file instance
:param timeout: Timeout for copying data

:return: (object) Entry instance on success
:since:  v0.1.00
		"""

		_return = Entry.new_stored_file()
		entry_data = { "size": uploaded_file.get_size() }

		file_name = InputFilter.filter_file_path(uploaded_file.get_client_file_name())
		if (file_name != ""): entry_data['title'] = file_name

		file_content_type = uploaded_file.get_client_content_type()
		mimetype_definition = MimeType.get_instance().get(mimetype = file_content_type)

		if (mimetype_definition is None and file_name != ""):
		#
			file_name_ext = path.splitext(file_name)[1]
			mimetype_definition = MimeType.get_instance().get(file_name_ext[1:])
		#

		if (mimetype_definition is not None):
		#
			entry_data['mimeclass'] = mimetype_definition['class']
			entry_data['mimetype'] = mimetype_definition['type']
		#
		elif (file_content_type is not None and "/" in file_content_type):
		#
			file_content_type_data = file_content_type.split("/", 1)

			entry_data['mimeclass'] = file_content_type_data[0]
			entry_data['mimetype'] = file_content_type_data[1]
		#

		_return.set_data_attributes(**entry_data)
		uploaded_file.copy_data(_return, timeout)

		return _return
	#
#

##j## EOF