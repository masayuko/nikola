# -*- coding: utf-8 -*-

# Copyright © 2012-2015 Roberto Alsina and others.

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Generate a robots.txt file."""

from __future__ import print_function, absolute_import, unicode_literals
import io
import os
try:
    from urlparse import urljoin
except ImportError:
    from urllib.parse import urljoin  # NOQA
import robotstxt

from nikola.plugin_categories import LateTask
from nikola import utils


class RobotsFile(LateTask):
    """Generate a robots.txt file."""

    name = "robots_file"

    def gen_tasks(self):
        """Generate a robots.txt file."""
        kw = {
            "base_url": self.site.config["BASE_URL"],
            "site_url": self.site.config["SITE_URL"],
            "output_folder": self.site.config["OUTPUT_FOLDER"],
            "files_folders": self.site.config['FILES_FOLDERS'],
            "robots_exclusions": self.site.config["ROBOTS_EXCLUSIONS"],
            "filters": self.site.config["FILTERS"],
        }

        sitemapindex_url = urljoin(kw["base_url"], "sitemapindex.xml")
        robots_path = os.path.join(kw['output_folder'], "robots.txt")

        def write_robots():
            if kw["site_url"] != urljoin(kw["site_url"], "/"):
                utils.LOGGER.warn('robots.txt not ending up in server root, will be useless')

            with io.open(robots_path, 'w+', encoding='utf8') as outf:
                lines = ['User-agent: *']
                if kw["robots_exclusions"]:
                    for loc in kw["robots_exclusions"]:
                        lines.append('Disallow: {0}'.format(loc))
                else:
                    lines.append('Allow: /')
                lines.append('Sitemap: {0}'.format(sitemapindex_url))
                robotstxt.dump(outf, robotstxt.parse(lines), ordered=True)
        yield self.group_task()

        if not utils.get_asset_path("robots.txt", [], files_folders=kw["files_folders"], output_dir=False):
            yield utils.apply_filters({
                "basename": self.name,
                "name": robots_path,
                "targets": [robots_path],
                "actions": [(write_robots)],
                "uptodate": [utils.config_changed(kw, 'nikola.plugins.task.robots')],
                "clean": True,
                "task_dep": ["sitemap"]
            }, kw["filters"])
        elif kw["robots_exclusions"]:
            utils.LOGGER.warn('Did not generate robots.txt as one already exists in FILES_FOLDERS. ROBOTS_EXCLUSIONS will not have any affect on the copied file.')
        else:
            utils.LOGGER.debug('Did not generate robots.txt as one already exists in FILES_FOLDERS.')
