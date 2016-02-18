# Copyright (c) 2014-2016 Frank Yang
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#

from datetime import datetime

from plugins.plugin import Plugin


class CookieJar(Plugin):
    name       = "CookieJar"
    optname    = "cookiejar"
    desc       = "Extract cookie from requests"
    version    = "0.1"
    
    @staticmethod
    def get_dict_data(dictionary, req_key):
        req_key = req_key.lower()
        for key in dictionary:
            if key.lower() == req_key:
                return dictionary[key]
    
    def directlogger(self, request):
        cookie = self.get_dict_data(request.headers, 'Cookie')
        if cookie is not None:
            self.clientlog.info(cookie, extra=request.clientInfo)
        
    def filelogger(self, request):
        cookie = self.get_dict_data(request.headers, 'Cookie')
        if cookie is not None:
            host = self.get_dict_data(request.headers, 'Host')
            time = datetime.now().strftime('%z %Y-%m-%d %H:%M:%S')

            self.clientlog.info(cookie, extra=request.clientInfo)
            cookie = cookie.replace('; ','\n')
            self.logfile.write("{time} [{from_}->{to}]\n['User-Agent':{clientinfo}]\n{cookie}\n\n".format(
                time=time, from_=request.clientInfo['clientip'], to=host, cookie=cookie,
                clientinfo=self.get_dict_data(request.headers, 'User-Agent')))

    def initialize(self, options):
        '''Called if plugin is enabled, passed the options namespace'''
        if options.cookie_logfile is not None:
            self.logfile = open(options.cookie_logfile, 'a')
            self.logger = self.filelogger
        else:
            self.logger = self.directlogger

    def request(self, request):
        self.logger(request)
    
    def options(self, options):
        options.add_argument("--cookie-logfile", type=str, help="Log file to store cookies")

    def on_shutdown(self):
        self.logfile.close()
