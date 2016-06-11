import errno
import logging
import time
import datetime
import os.path
import shutil
from bs4 import BeautifulSoup
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


logger = logging.getLogger("root")
logging.basicConfig(
    format="\033[1;36m%(levelname)s: %(filename)s (def %(funcName)s %(lineno)s): \033[1;37m %(message)s",
    level=logging.DEBUG
)


class GrabWebSite(object):
    """
    """
    # https://stackoverflow.com/questions/19120489/compare-two-files-report-difference-in-python

    data_directory = os.path.join(os.getcwd(), "diffs")

    sites = [
        {"dir": "loretta_sanchez", "pages": [
            "http://www.loretta.org", "http://www.loretta.org/issues/"]},
        {"dir": "kamala_harris", "pages": [
            "http://www.kamalaharris.org", "http://www.kamalaharris.org/issues/"]},
        {"dir": "laura_friedman", "pages": [
            "https://votelaurafriedman.com/", "https://votelaurafriedman.com/bio/", "https://votelaurafriedman.com/news/"]},
        {"dir": "ardy_kassakhian", "pages": [
            "http://www.ardyforassembly.com/", "http://www.ardyforassembly.com/issues", "http://www.ardyforassembly.com/news"]},
    ]

    date_object = datetime.datetime.now()

    date_string = date_object.strftime("%Y_%m_%d")

    def _init(self, *args, **kwargs):
        """
        """
        self.make_a_dir(self.data_directory)
        for site in self.sites:
            this_dir = os.path.join(self.data_directory, site["dir"])
            self.make_a_dir(this_dir)
            self._request_results_and_save(site, this_dir)

    def _request_results_and_save(self, site, data_directory):
        """
        """
        for page in site["pages"]:
            file_raw = "_tracked_%s.html" % (page.replace(
                "http://www.", "").replace("/", ""))
            that_file = os.path.join(data_directory, file_raw)
            file_name = "_%s_%s.html" % (self.date_string, page.replace(
                "http://www.", "").replace("/", ""))
            this_file = os.path.join(data_directory, file_name)
            session = requests.Session()
            retries = Retry(
                total=5,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504]
            )
            session.mount("http://", HTTPAdapter(max_retries=retries))
            response = session.get(
                page,
                timeout=10,
                allow_redirects=False
            )
            try:
                response.raise_for_status()
                logger.debug("Success! %s responded with a file\n" % (page))
                with open(that_file, "wb") as output:
                    output.write(response.content)
                with open(this_file, "wb") as output:
                    output.write(response.content)
            except requests.exceptions.ReadTimeout as exception:
                # maybe set up for a retry, or continue in a retry loop
                logger.error("%s: %s" % (exception, page))
                logger.error(
                    "will need to setup retry and then access archived file")
                raise
            except requests.exceptions.ConnectionError as exception:
                # incorrect domain
                logger.error(
                    "will need to raise message that we can't connect")
                logger.error("%s: %s" % (exception, page))
                raise
            except requests.exceptions.HTTPError as exception:
                # http error occurred
                logger.error("%s: %s" % (exception, page))
                logger.error("trying to access archived file via failsafe")
                raise
            except requests.exceptions.URLRequired as exception:
                # valid URL is required to make a request
                logger.error("%s: %s" % (exception, page))
                logger.error("will need to raise message that URL is broken")
                failsafe = self._return_archived_file(src, data_directory)
                raise
            except requests.exceptions.TooManyRedirects as exception:
                # tell the user their url was bad and try a different one
                logger.error("%s: %s" % (exception, page))
                logger.error("will need to raise message that URL is broken")
                failsafe = self._return_archived_file(src, data_directory)
                raise
            except requests.exceptions.RequestException as exception:
                # ambiguous exception
                logger.error("%s: %s" % (exception, page))
                logger.error("trying to access archived file via failsafe")
                failsafe = self._return_archived_file(src, data_directory)
                raise
            file_exists = os.path.isfile(this_file)
            file_has_size = os.path.getsize(this_file)
            if file_exists == True:
                logger.debug("\t* Success! %s downloaded\n" % (this_file))
            else:
                logger.error("Failure! %s doesn't exist" % (this_file))
                raise Exception

    def make_a_dir(self, path):
        dir_exists = os.path.isdir(path)
        if dir_exists == True:
            pass
        else:
            try:
                os.makedirs(path)
                logger.debug("* Created %s\n" % (path))
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

if __name__ == "__main__":
    task_run = GrabWebSite()
    task_run._init()
    print "\nTask finished at %s\n" % str(datetime.datetime.now())
