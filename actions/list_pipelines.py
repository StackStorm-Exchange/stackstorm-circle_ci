try:  # Python 3
    from http import HTTPStatus as http_status
except ImportError:  # Python 2
    import httplib as http_status

from lib.action import CircleCI


class ListPipelinesAction(CircleCI):

    def run(self, project, vcs_type, username, branch=None):
        path = 'project/%s/%s/%s/pipeline' % (vcs_type, username, project)

        if branch:
            path += '?branch=%s' % (branch)

        response = self._perform_request(
            path, method='GET', api_version='v2'
        )

        if response.status_code != http_status.OK:
            raise Exception("Failed to list pipelines: %s" % (str(response.content)))

        return response.json()
