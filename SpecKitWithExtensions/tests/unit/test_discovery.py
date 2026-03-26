"""Unit tests for region discovery. @req FR-001"""

import pytest
from aioresponses import aioresponses

from cloudlatency.engine.discovery import discover_aws_regions, discover_azure_regions, discover_gcp_regions, discover_all_regions
from cloudlatency.engine.models import CloudRegion


# Sample API responses
AWS_IP_RANGES_RESPONSE = {
    "prefixes": [
        {"region": "us-east-1", "service": "EC2", "ip_prefix": "3.5.140.0/22"},
        {"region": "eu-west-1", "service": "EC2", "ip_prefix": "52.95.245.0/24"},
        {"region": "us-east-1", "service": "EC2", "ip_prefix": "3.5.141.0/22"},  # duplicate region
        {"region": "ap-southeast-1", "service": "S3", "ip_prefix": "52.219.0.0/20"},  # non-EC2
    ]
}

GCP_CLOUD_JSON_RESPONSE = {
    "prefixes": [
        {"scope": "us-central1", "ipv4Prefix": "34.0.0.0/15"},
        {"scope": "europe-west1", "ipv4Prefix": "34.76.0.0/14"},
        {"scope": "us-central1", "ipv4Prefix": "34.2.0.0/16"},  # duplicate
        {"scope": "global", "ipv4Prefix": "35.190.0.0/16"},  # global, not a region
    ]
}

class TestDiscoverAWSRegions:
    """Test AWS region discovery from ip-ranges.amazonaws.com."""

    @pytest.mark.asyncio
    async def test_discovers_unique_regions(self) -> None:
        with aioresponses() as mocked:
            mocked.get("https://ip-ranges.amazonaws.com/ip-ranges.json", payload=AWS_IP_RANGES_RESPONSE)
            regions = await discover_aws_regions()
        assert len(regions) == 2
        codes = {r.region_code for r in regions}
        assert "us-east-1" in codes
        assert "eu-west-1" in codes

    @pytest.mark.asyncio
    async def test_regions_have_correct_provider(self) -> None:
        with aioresponses() as mocked:
            mocked.get("https://ip-ranges.amazonaws.com/ip-ranges.json", payload=AWS_IP_RANGES_RESPONSE)
            regions = await discover_aws_regions()
        for r in regions:
            assert r.provider_id == "aws"

    @pytest.mark.asyncio
    async def test_regions_have_endpoint_urls(self) -> None:
        with aioresponses() as mocked:
            mocked.get("https://ip-ranges.amazonaws.com/ip-ranges.json", payload=AWS_IP_RANGES_RESPONSE)
            regions = await discover_aws_regions()
        for r in regions:
            assert r.endpoint_url.startswith("https://")
            assert r.region_code in r.endpoint_url

    @pytest.mark.asyncio
    async def test_handles_api_failure(self) -> None:
        with aioresponses() as mocked:
            mocked.get("https://ip-ranges.amazonaws.com/ip-ranges.json", status=500)
            regions = await discover_aws_regions()
        assert regions == []


class TestDiscoverGCPRegions:
    """Test GCP region discovery from gstatic.com."""

    @pytest.mark.asyncio
    async def test_discovers_unique_regions(self) -> None:
        with aioresponses() as mocked:
            mocked.get("https://www.gstatic.com/ipranges/cloud.json", payload=GCP_CLOUD_JSON_RESPONSE)
            regions = await discover_gcp_regions()
        assert len(regions) == 2
        codes = {r.region_code for r in regions}
        assert "us-central1" in codes
        assert "europe-west1" in codes

    @pytest.mark.asyncio
    async def test_filters_global_scope(self) -> None:
        with aioresponses() as mocked:
            mocked.get("https://www.gstatic.com/ipranges/cloud.json", payload=GCP_CLOUD_JSON_RESPONSE)
            regions = await discover_gcp_regions()
        codes = {r.region_code for r in regions}
        assert "global" not in codes

    @pytest.mark.asyncio
    async def test_handles_api_failure(self) -> None:
        with aioresponses() as mocked:
            mocked.get("https://www.gstatic.com/ipranges/cloud.json", status=500)
            regions = await discover_gcp_regions()
        assert regions == []


class TestDiscoverAzureRegions:
    """Test Azure region discovery from hardcoded registry."""

    @pytest.mark.asyncio
    async def test_discovers_at_least_50_regions(self) -> None:
        regions = await discover_azure_regions()
        assert len(regions) >= 50

    @pytest.mark.asyncio
    async def test_regions_have_correct_provider(self) -> None:
        regions = await discover_azure_regions()
        for r in regions:
            assert r.provider_id == "azure"

    @pytest.mark.asyncio
    async def test_regions_have_blob_storage_endpoints(self) -> None:
        regions = await discover_azure_regions()
        for r in regions:
            assert r.endpoint_url.startswith("https://")
            assert "blob.core.windows.net" in r.endpoint_url

    @pytest.mark.asyncio
    async def test_regions_have_display_names(self) -> None:
        regions = await discover_azure_regions()
        for r in regions:
            assert r.region_name != ""
            assert r.region_code != ""

    @pytest.mark.asyncio
    async def test_known_regions_present(self) -> None:
        regions = await discover_azure_regions()
        codes = {r.region_code for r in regions}
        assert "eastus" in codes
        assert "westeurope" in codes
        assert "southeastasia" in codes

    @pytest.mark.asyncio
    async def test_no_duplicate_region_codes(self) -> None:
        regions = await discover_azure_regions()
        codes = [r.region_code for r in regions]
        assert len(codes) == len(set(codes))


class TestDiscoverAllRegions:
    """Test combined region discovery."""

    @pytest.mark.asyncio
    async def test_combines_all_providers(self) -> None:
        with aioresponses() as mocked:
            mocked.get("https://ip-ranges.amazonaws.com/ip-ranges.json", payload=AWS_IP_RANGES_RESPONSE)
            mocked.get("https://www.gstatic.com/ipranges/cloud.json", payload=GCP_CLOUD_JSON_RESPONSE)
            regions = await discover_all_regions()
        providers = {r.provider_id for r in regions}
        assert "aws" in providers
        assert "gcp" in providers
        assert "azure" in providers  # hardcoded, always present

    @pytest.mark.asyncio
    async def test_partial_failure_still_includes_azure(self) -> None:
        with aioresponses() as mocked:
            mocked.get("https://ip-ranges.amazonaws.com/ip-ranges.json", status=500)
            mocked.get("https://www.gstatic.com/ipranges/cloud.json", status=500)
            regions = await discover_all_regions()
        # Azure is hardcoded, so it's always available even when AWS/GCP fail
        assert len(regions) >= 50
        azure_regions = [r for r in regions if r.provider_id == "azure"]
        assert len(azure_regions) >= 50
