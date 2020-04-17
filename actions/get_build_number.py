import six.moves.http_client as http_status

from lib.action import CircleCI


class GetBuildNumberAction(CircleCI):

    def run(self, project, vcs_type, username, vcs_revision, search_limit=10):
        """
        Get build number for a SHA in project.
        """
        path = 'project/%s/%s/%s' % (vcs_type, username, project)

        response = self._perform_request(
            path, method='GET',
            extra_headers={'limit': str(search_limit)}
        )

        if response.status_code != http_status.OK:  # pylint: disable=no-member
            raise Exception('Project %s not found. Response: %s' % (project, response.text))

        for build in response.json():
            if build['vcs_revision'] == vcs_revision:
                build_num = build.get('build_num', None)
                if not build_num:
                    raise Exception(
                        'API must have changed. build_num not found.')
                return build_num
