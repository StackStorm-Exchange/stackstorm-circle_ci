try:  # Python 3
    from http import HTTPStatus as http_status
except ImportError:  # Python 2
    import httplib as http_status

from lib.action import CircleCI


class CancelBuild(CircleCI):

    def run(self, project, vcs_type, username, build_num):
        """
        ReRun a specific build in project.
        """
        path = 'project/%s/%s/%s/%s/cancel' % (vcs_type, username, project, build_num)

        response = self._perform_request(
            path, method='POST'
        )

        if response.status_code != http_status.CREATED:
            raise Exception('Project %s not found.' % project)

        return response.json()
