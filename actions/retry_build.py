import six.moves.http_client as http_status

from lib.action import CircleCI


class RetryBuild(CircleCI):

    def run(self, project, vcs_type, username, build_num):
        """
        ReRun a specific build in project.
        """
        path = 'project/%s/%s/%s/%s/retry' % (vcs_type, username, project, build_num)

        response = self._perform_request(
            path, method='POST'
        )

        if response.status_code != http_status.CREATED:  # pylint: disable=no-member
            raise Exception('Project %s not found.' % project)

        return response.json()
