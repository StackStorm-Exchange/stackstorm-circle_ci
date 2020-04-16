try:  # Python 3
    from http import HTTPStatus as http_status
except ImportError:  # Python 2
    import httplib as http_status
import json

from lib.action import CircleCI


class RunProjectBuild(CircleCI):

    def run(self, project, vcs_type, username, branch=None,
            tag=None, vcs_revision=None):
        """
        Run build for a SHA in project.
        """

        # Add some explicit mutually-exclusive checks.
        if not (branch or tag or vcs_revision):
            raise Exception('At least one of branch, tag or vcs_revision should be provided.')
        if (branch and (tag or vcs_revision)) or (tag and vcs_revision):
            raise Exception('Only one of branch, tag or vcs_revision should be provided.')

        data = {}
        if branch:
            data['branch'] = branch
        elif tag:
            data['tag'] = tag
        elif vcs_revision:
            data['vcs_revision'] = vcs_revision

        path = 'project/%s/%s/%s/build' % (vcs_type, username, project)

        if data:
            data = json.dumps(data)

        response = self._perform_request(path, method='POST', data=data)

        try:
            result = response.json()
        except ValueError:
            result = response.content

        if response.status_code not in [http_status.OK, http_status.CREATED]:
            raise Exception(
                'Failed to run build : %s' % (
                    result.get('message', result) if isinstance(result, dict) else result
                )
            )

        return result
