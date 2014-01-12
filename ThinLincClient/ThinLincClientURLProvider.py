#!/usr/bin/env python
#
# Copyright 2014 Greg Neagle
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import urllib2

from autopkglib import Processor, ProcessorError


__all__ = ["ThinLincClientURLProvider"]


BASE_URL = "http://www.cendio.com/downloads/clients/"

# example download link: http://www.cendio.com/downloads/clients/tl-4.1.1_4137-client-osx.iso
# but in HTML source it's:
# <a xmlns="http://www.w3.org/1999/xhtml" href="tl-4.1.1_4137-client-osx.iso">ThinLinc 4.1.1 Client for Mac OS X</a>
re_dmg_link = re.compile(r'href="(?P<url>tl-[._0-9]*-client-osx\.iso)"')


class ThinLincClientURLProvider(Processor):
    """Provides a download URL for ThinLinc OS X client."""
    input_variables = {
        "base_url": {
            "required": False,
            "description": (
                "Default is %s. Make sure it ends with the trailing slash."
                % BASE_URL),
        },
    }
    output_variables = {
        "url": {
            "description": "URL to ThinLinc OS X client download.",
        },
    }
    description = __doc__

    def get_thinlinc_iso_url(self, base_url):
        # Read HTML index.
        try:
            f = urllib2.urlopen(base_url)
            html = f.read()
            f.close()
        except BaseException as err:
            raise ProcessorError("Can't download %s: %s" % (base_url, err))
        
        m = re_dmg_link.search(html)
        
        if not m:
            raise ProcessorError(
                "Couldn't find ThinLinc Client download URL in %s" % base_url)
        
        link = urllib2.quote(m.group("url"), safe=":/%")
        if link:
            # link better end with '/'
            link = base_url.rstrip('/') + '/' + link
        return link
        

    def main(self):
        """Find and return a download URL"""
        base_url = self.env.get("base_url", BASE_URL)
        self.env["url"] = self.get_thinlinc_iso_url(base_url)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = ThinLincClientURLProvider()
    processor.execute_shell()
