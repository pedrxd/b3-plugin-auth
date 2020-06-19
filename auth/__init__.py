"""
    This plugin for bigbrotherbot is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This plugin is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = 1.1
__author__ = 'pedrxd';

import b3
import b3.events
import b3.plugin
import os
from b3.querybuilder import QueryBuilder

class AuthPlugin(b3.plugin.Plugin):
    requiresConfigFile = False

    def onStartup(self):
        self._adminPlugin = self.console.getPlugin('admin')

        if not self._adminPlugin:
            self.error('Could not find admin plugin')
            return

        if 'authmod' not in self.console.storage.getTables():
            external_dir = self.console.config.get_external_plugins_dir()
            sql_path = os.path.join(external_dir, 'auth', 'sql', 'authmod.sql')
            self.console.storage.queryFromFile(sql_path)

        self._adminPlugin.registerCommand(self, 'auth', 80, self.cmd_auth)
        self._adminPlugin.registerCommand(self, 'setauth', 100, self.cmd_setAuth)
        self._adminPlugin.registerCommand(self, 'delauth', 100, self.cmd_delAuth)

        self.registerEvent(b3.events.EVT_CLIENT_JOIN, self.onChange)


    def onChange(self, event):
        client = event.client
        self.updateGameAuth(client)


    def updateGameAuth(self, client, auth=None):
        if (auth is None):
            auth = self.db_getauth(client)

        if(auth is not None):
            self.console.write('changeauth {} {}'.format(client.cid, auth))


    def cmd_auth(self, data, client, cmd=None):
        """
        <player> <auth> - Set a temporal auth
        """
        if not data:
            client.message('Correct usage: !auth <client> <auth>')
            return

        argv = self._adminPlugin.parseUserCmd(data)
        if (len(argv) <= 1):
            client.message('Correct usage: !setauth <client> <auth>')
            return

        sclient = self._adminPlugin.findClientPrompt(argv[0], client)
        if not sclient:
            return

        self.updateGameAuth(sclient, argv[1])
        client.message('The auth has been changed correctly')

    def cmd_setAuth(self, data, client, cmd=None):
        """
        <player> <auth> - Set a persistent auth
        """
        if not data:
            client.message('Correct usage: !setauth <client> <auth>')
            return

        argv = self._adminPlugin.parseUserCmd(data)
        if (len(argv) <= 1):
            client.message('Correct usage: !setauth <client> <auth>')
            return

        sclient = self._adminPlugin.findClientPrompt(argv[0], client)
        if not sclient:
            return

        self.db_putauth(sclient, argv[1])
        self.updateGameAuth(sclient)
        client.message('The auth has been changed permantly')


    def cmd_delAuth(self, data, client, cmd=None):
        """
        <player> - Remove persistent auth
        """
        if not data:
            client.message('Correct usage: !setauth <client>')
            return

        sclient = self._adminPlugin.findClientPrompt(data, client)
        if not sclient:
            return

        self.db_delauth(sclient)
        self.updateGameAuth(sclient)
        client.message('The auth has been removed')


    def db_putauth(self, client, auth):
        if self.db_getauth(client) is None:
            q = QueryBuilder(self.console.storage.db).InsertQuery({'clientid':client.id,'auth':auth},'authmod')
        else:
            q = QueryBuilder(self.console.storage.db).UpdateQuery({'auth':auth}, 'authmod', {'clientid':client.id})

        self.console.storage.query(q)

    def db_delauth(self, client):
        q = "DELETE FROM authmod WHERE clientid = {0}".format(client.id)
        self.console.storage.query(q)

    def db_getauth(self, client):
        q = QueryBuilder(self.console.storage.db).SelectQuery(('auth'), 'authmod', {'clientid':client.id})
        s = self.console.storage.query(q)
        if s and not s.EOF:
            return s.getRow()['auth']
        return None
