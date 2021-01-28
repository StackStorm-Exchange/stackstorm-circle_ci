import json

import six.moves.http_client as http_status

from lib.action import CircleCI


class RunBuild(CircleCI):

    def run(self, project, vcs_type, username, branch=None,
            tag=None, vcs_revision=None, build_parameters=None):
        """
        Run build for a SHA in project.
        """

        # Add some explicit mutually-exclusive checks.
        if not (branch or tag or vcs_revision):
            raise Exception('At least one of branch, tag or vcs_revision should be provided.')
        if (branch and (tag or vcs_revision)) or (tag and vcs_revision):
            raise Exception('Only one of branch, tag or vcs_revision should be provided.')

        data = None
        if branch:
            path = 'project/%s/%s/%s/tree/%s' % (vcs_type, username, project, branch)
        else:
            path = 'project/%s/%s/%s' % (vcs_type, username, project)
            data = {'tag': tag} if tag else {'revision': vcs_revision}

        # build parameters are pass-trhrough to circleci
        if build_parameters:
            if data is None:
                data = {}
            data['build_parameters'] = build_parameters

        if data:
            data = json.dumps(data)

        response = self._perform_request(path, method='POST', data=data)

        try:
            result = response.json()
        except ValueError:
            result = response.content

        if response.status_code != http_status.CREATED:  # pylint: disable=no-member
            raise Exception(
                'Failed to run build : %s' % (
                    result.get('message', str(result)) if isinstance(result, dict) else result
                )
            )

        return result
