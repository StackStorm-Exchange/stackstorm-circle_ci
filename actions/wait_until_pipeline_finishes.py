try:  # Python 3
    from http import HTTPStatus as http_status
except ImportError:  # Python 2
    import httplib as http_status
import time

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

        if response.status_code != http_status.OK:
            raise Exception("Failed to retrieve pipelines: %s" % (str(response.content)))

        data = response.json()

        if data["state"] in PIPELINE_DONE_STATES:
            print('Pipeline has finished.')
            return {"status": "failure"}

        pipeline_id = data["id"]

        start_time = time.time()
        done = False

        # Find all the pipeline workflows and wait for them to finish
        while not done:
            path = 'pipeline/%s/workflow' % (pipeline_id)
            response = self._perform_request(
                path, method='GET', api_version='v2'
            )

            all_workflows = response.json()["items"]
            finished_workflows = [w for w in all_workflows if w["status"] in WORKFLOW_DONE_STATES]

            workflow_names = [w["name"] for w in finished_workflows]

            if len(finished_workflows) >= len(all_workflows):
                print('All pipeline workflows (%s) have finished' % ', '.join(workflow_names))
                # On success, we also return overall pipeline status

                succeeded_workflows = [w for w in all_workflows if w["status"] in ["success"]]

                if len(succeeded_workflows) >= len(all_workflows):
                    status = "success"
                else:
                    status = "failure"

                return {"status": status}

            print("%s/%s workflows (%s) finished" % (len(finished_workflows), len(all_workflows),
                                                     ', '.join(workflow_names)))

            time.sleep(sleep_interval)
            done = (time.time() - start_time) > wait_timeout

        raise Exception('Pipeline did not complete within %s seconds.' %
                        wait_timeout)
