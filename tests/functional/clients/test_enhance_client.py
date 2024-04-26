import logging
import time

import pytest
from aiohttp import ClientResponseError
from diffbot_kg.clients.enhance import DiffbotEnhanceClient

from tests.functional.conftest import (
    ORG2_ENTITY_ID,
    ORG2_NAME,
    ORG2_URL,
    ORG_ENTITY_ID,
    ORG_NAME,
    ORG_URL,
    Secret,
)

log = logging.getLogger(__name__)


def _get_job_id(request):
    job_id = request.config.cache.get("enhanceBulkJobId", None)
    if job_id is None:
        pytest.fail("Enhance bulk job ID not found in cache")

    return job_id


@pytest.mark.vcr(record_mode="new_episodes")
@pytest.mark.usefixtures("suppress_aiohttp_output")
class TestDiffbotEnhanceClient:
    @pytest.mark.asyncio
    async def test_enhance(self, token: Secret):
        # ARRANGE
        client = DiffbotEnhanceClient(token=token.value)

        # ACT
        response = await client.enhance({"type": "Organization", "name": ORG_NAME})

        # ASSERT
        assert response.status == 200
        assert response.content["hits"] == 1
        assert response.entities[0]["id"] == ORG_ENTITY_ID

    @pytest.mark.asyncio
    async def test_create_bulkjob(self, request, token: Secret):
        # ARRANGE
        client = DiffbotEnhanceClient(token=token.value)
        params = {"size": 1}

        # ACT
        response = await client.create_bulkjob(
            [
                {"type": "Organization", "name": ORG_NAME, "url": ORG_URL},
                {"type": "Organization", "name": ORG2_NAME, "url": ORG2_URL},
            ],
            params,
        )

        # ASSERT
        assert response.status == 202
        assert "job_id" in response.content

        # TEARDOWN
        request.config.cache.set("enhanceBulkJobId", response.jobId)
        await client.close()

    @pytest.mark.asyncio
    async def test_list_bulkjobs(self, request, token: Secret):
        # ARRANGE
        client = DiffbotEnhanceClient(token=token.value)

        job_id = _get_job_id(request)

        # ACT
        response = await client.list_bulkjobs()

        # ASSERT
        assert response.status == 200
        assert any(x["job_id"] == job_id for x in response.content)

        # TEARDOWN
        await client.close()

    @pytest.mark.asyncio
    async def test_bulkjob_status(self, request, token: Secret):
        # ARRANGE
        client = DiffbotEnhanceClient(token=token.value)

        job_id = _get_job_id(request)

        TIMEOUT = 60
        BACKOFF_FACTOR = 1.5
        backoff = 1
        start = time.time()

        # ACT
        while True:
            response = await client.bulkjob_status(job_id)
            if response.complete:
                break
            elif time.time() - start > TIMEOUT:
                pytest.fail("Bulk job status check did not complete in time")

            time.sleep(backoff)
            backoff *= BACKOFF_FACTOR

        # ASSERT
        assert response.status == 200
        assert response.jobId == job_id
        assert response.complete

        if len(response.reports) > 1:
            log.warning(
                "More than one report found for bulk job. Investigate: %s",
                response.reports,
            )

        # TEARDOWN
        request.config.cache.set(
            "enhanceBulkJobCoverageReportId", response.reports[0]["reportId"]
        )
        await client.close()

    @pytest.mark.asyncio
    async def test_bulkjob_results(self, request, token: Secret):
        # ARRANGE
        client = DiffbotEnhanceClient(token=token.value)

        job_id = _get_job_id(request)

        # ACT
        response = await client.bulkjob_results(job_id)

        # ASSERT
        assert response.status == 200
        assert len(response.content) == 2
        assert response.content[0]["hits"] == 1
        assert len(response.content[0]["data"]) == 1
        assert response.entities[0]["id"] == ORG_ENTITY_ID
        assert response.content[1]["hits"] == 1
        assert len(response.content[1]["data"]) == 1
        assert response.entities[1]["id"] == ORG2_ENTITY_ID

        # TEARDOWN
        await client.close()

    @pytest.mark.asyncio
    async def test_single_bulkjob_result(self, request, token: Secret):
        # ARRANGE
        client = DiffbotEnhanceClient(token=token.value)

        job_id = _get_job_id(request)

        # ACT
        response = await client.single_bulkjob_result(job_id, 0)

        # ASSERT
        assert response.status == 200
        assert response.content["hits"] == 1
        assert len(response.data) == 1
        assert response.entities[0]["id"] == ORG_ENTITY_ID

        # TEARDOWN
        await client.close()

    @pytest.mark.asyncio
    async def test_bulkjob_coverage_report(self, request, token: Secret):
        # ARRANGE
        client = DiffbotEnhanceClient(token=token.value)

        job_id = _get_job_id(request)
        report_id = request.config.cache.get("enhanceBulkJobCoverageReportId", None)
        if report_id is None:
            pytest.fail("Enhance bulk job coverage report ID not found in cache")


        TIMEOUT = 60
        BACKOFF_FACTOR = 1.5
        backoff = 1
        start = time.time()

        # ACT
        while True:
            try:
                response = await client.bulkjob_coverage_report(job_id, report_id)
            except ClientResponseError as e:
                if e.status == 400:
                    time.sleep(backoff)
                    backoff *= BACKOFF_FACTOR
            else:
                if response.status == 200:
                    break
                elif time.time() - start > TIMEOUT:
                    pytest.fail("Bulk job coverage report did not generate in time")

        # ASSERT
        assert response.status == 200
        assert len(response.content.strip().split("\n")) == 4


    @pytest.mark.asyncio
    async def test_bulkjob_stop(self, request, token: Secret):
        # ARRANGE
        client = DiffbotEnhanceClient(token=token.value)

        job_id = _get_job_id(request)

        # ACT
        response = await client.stop_bulkjob(job_id)

        # ASSERT
        assert response.status == 200
        assert response.content["status"] == "COMPLETE"
        assert response.content["message"] == f"Bulkjob [{job_id}] is completed"

        # TEARDOWN
        await client.close()
