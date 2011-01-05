# Copyright 2008 VMware, Inc.  All rights reserved. -- VMware Confidential
"""
Zimbra Collaboration Suite virtual appliance gobuild target.
"""

import os
import re
import helpers.env
import helpers.target
import helpers.make
import specs.zimbra

ALLOW_OFFICIAL_KEY='allow.elfofficialkey'

class ZimbraVA(helpers.target.Target, helpers.make.MakeHelper):
   """
   Zimbra Collaboration Suite virtual appliance
   """

   def GetBuildProductNames(self):
      return { 'name':      'zimbra_va',
               'longname' : 'Zimbra Collaboration Suite virtual appliance' }

   def GetClusterRequirements(self):
      return ['linux']

   def GetOptions(self):
      """
      Return a list of flags this target supports.
      """
      return [
         (ALLOW_OFFICIAL_KEY, False,
          'Whether or not allow official key to be turned on. This flag is controlled by gobuildharness'),
      ]

   def GetRepositories(self, hosttype):
      repos = [
            helpers.target.PerforceRepo(
               '%(branch)/ZimbraBuild',
               'ZimbraBuild'),
            helpers.target.PerforceRepo(
               '%(branch)/ZimbraAppliance',
               'ZimbraAppliance'),
            helpers.target.PerforceRepo(
               '%(branch)/ZimbraNetwork',
               'ZimbraNetwork'),
         ]
      return repos

   def GetComponentDependencies(self):
      comps = {}
      comps['csc-ubuntu804'] = {
         'branch': specs.zimbra.CSC_UBUNTU804_BRANCH,
         'change': specs.zimbra.CSC_UBUNTU804_CLN,
         'buildtype': specs.zimbra.CSC_UBUNTU804_BUILDTYPE,
      }
      comps['tools'] = {
         'branch': specs.zimbra.TOOLS_BRANCH,
         'change': specs.zimbra.TOOLS_CLN,
         'buildtype': specs.zimbra.TOOLS_BUILDTYPE,
      }
      comps['va_build'] = {
         'branch': specs.zimbra.VA_BUILD_BRANCH,
         'change': specs.zimbra.VA_BUILD_CLN,
         'buildtype': specs.zimbra.VA_BUILD_BUILDTYPE,
      }
      return comps

   def GetCommands(self, hosttype):
      target = 'all'
      flags = {}
      flags['--makefile'] = 'Makefile.vai'
      return [ { 'desc'    : 'Running Zimbra VA build',
                 'root'    : 'ZimbraAppliance',
                 'log'     : 'zimbra-va-%s.log' % target,
                 'command' : self._Command(hosttype,
                                           target,
                                           **flags),
                 'env'     : self._GetEnvironment(hosttype),
               } ]

   def GetStorageInfo(self, hosttype):
      storages = []
      if hosttype == 'linux':
         storages += [{'type': 'source', 'src': 'ZimbraAppliance/'}]
         storages += [{'type': 'source', 'src': 'ZimbraBuild/'}]
         storages += [{'type': 'source', 'src': 'ZimbraNetwork/'}]
      storages += [{'type': 'build',
                     'src': 'ZimbraAppliance/build/'}]
      return storages

   def GetBuildProductVersion(self, hosttype):
      if hosttype.startswith('linux'):
         vfile = "%s/ZimbraAppliance/defs.mk" % self.options.get('buildroot')
         vregexp = re.compile(r'^VA_PRODUCT_VERSION\s*:=\s*(.*)')
         try:
            for line in file(vfile):
               m = vregexp.search(line)
               if m:
                  return m.group(1)
         except IOError, e:
            return ''
      return ''

   def _GetEnvironment(self, hosttype):
      env = helpers.env.SafeEnvironment(hosttype)

      path = []
      if hosttype.startswith('windows'):
         tcroot = os.environ.get('TCROOT', 'C:/TCROOT-not-set')
         path += [
            r'%s\win32\coreutils-5.3.0\bin' % tcroot,
         ]
      elif hosttype.startswith('linux'):
         pkgs = [
            'coreutils-5.97',
            'grep-2.5.1a',
            'gzip-1.3.5',
            'cdrtools-2.01',
            'perl-5.8.8',
         ]
         path = ['/build/toolchain/lin32/%s/bin' % p for p in pkgs]
      path += [env['PATH']]
      env['PATH'] = os.pathsep.join(path)

      OVF_OFFICIAL_KEY = 1
      if self.options.get(ALLOW_OFFICIAL_KEY) and OVF_OFFICIAL_KEY:
         self.log.debug('Turning on official OVF signing.')
         env['OVF_OFFICIAL_KEY'] = '1'

      env['CREATE_OSS_TGZ'] = '1'

      return env

