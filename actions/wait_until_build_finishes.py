try:  # Python 3
    from http import HTTPStatus as http_status
except ImportError:  # Python 2
    import httplib as http_status
import time

from lib.action import CircleCI


class WaitUntilBuildFinishes(CircleCI):

    def run(self, project, vcs_type, username, build_num, wait_timeout=600):
        """
        Get build number for a SHA in project.
        """
        path = 'project/%s/%s/%s/%s' % (vcs_type, username, project, build_num)

        start_time = time.time()
        done = False
        while not done:
            response = self._perform_request(
                path, method='GET',
            )

            if response.status_code != http_status.OK:
                msg = ('Build number %s for project ' % build_num +
                       '%s not found.' % project)
                raise Exception(msg)

            response = response.json()

            if response['lifecycle'] == 'finished':
                return True

            time.sleep(10)
            done = (time.time() - start_time) > wait_timeout

        raise Exception('Build did not complete within %s seconds.' %
                        wait_timeout)
