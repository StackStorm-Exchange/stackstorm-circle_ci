import time

import six.moves.http_client as http_status

from lib.action import CircleCI

PIPELINE_DONE_STATES = [
    "errored",
]

# https://circleci.com/docs/api/v2/#get-a-pipeline-39-s-workflows
WORKFLOW_DONE_STATES = [
    "success",
    "failed",
    "error",
    "failing",
    "canceled",
    "unauthorized"
]


class WaitUntilPipelineWorkflowsFinish(CircleCI):

    def run(self, project, vcs_type, username, pipeline_num, wait_timeout=600,
            sleep_interval=10):
        # Check if pipeline itself has finished (aka there was an error)
        path = 'project/%s/%s/%s/pipeline/%s' % (vcs_type, username, project, pipeline_num)
        response = self._perform_request(
            path, method='GET', api_version='v2'
        )

        if response.status_code != http_status.OK:  # pylint: disable=no-member
            raise Exception("Failed to list pipelines: %s" % (str(response.content)))

        data = response.json()

        if data["state"] in PIPELINE_DONE_STATES:
            self.logger.info('Pipeline has finished')
            return {"status": "failure"}

        pipeline_id = data["id"]

        start_time = time.time()
        timeout_time = (start_time) + wait_timeout

        # Find all the pipeline workflows and wait for them to finish
        while time.time() < timeout_time:
            path = 'pipeline/%s/workflow' % (pipeline_id)
            response = self._perform_request(
                path, method='GET', api_version='v2'
            )

            if response.status_code != http_status.OK:  # pylint: disable=no-member
                # Assume a temporary hiccup
                self.logger.warning('Received non-200 when listening pipeline workflows ('
                                    'status=%s). Response: %s' % (response.status_code,
                                                                  response.text))
                time.sleep(sleep_interval)
                continue

            all_workflows = response.json()["items"]
            finished_workflows = [w for w in all_workflows if w["status"] in WORKFLOW_DONE_STATES]
            workflow_names = [w["name"] for w in finished_workflows]

            if len(finished_workflows) >= len(all_workflows):
                self.logger.info('All pipeline workflows (%s) have finished' %
                                 ', '.join(workflow_names))
                # On success, we also return overall pipeline status
                succeeded_workflows = [w for w in all_workflows if w["status"] in ["success"]]

                if len(succeeded_workflows) >= len(all_workflows):
                    status = "success"
                else:
                    status = "failure"

                return {"status": status}

            self.logger.info("%s/%s workflows (%s) finished" % (len(finished_workflows),
                                                                len(all_workflows),
                                                                ', '.join(workflow_names)))

            time.sleep(sleep_interval)

        raise Exception('Pipeline did not complete within %s seconds.' %
                        wait_timeout)
