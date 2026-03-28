"""Tests for cloud region endpoint definitions."""

from cloudlatency.regions import (
    PROVIDER_AWS,
    PROVIDER_AZURE,
    PROVIDER_GCP,
    PROVIDERS,
    Region,
    get_all_regions,
    get_regions_by_provider,
)


class TestRegionDataStructure:
    """Tests for the Region NamedTuple and constants."""

    def test_region_has_required_fields(self):
        """Region NamedTuple has provider, region_name, endpoint_url fields."""
        r = Region(provider="aws", region_name="us-east-1", endpoint_url="https://example.com/")
        assert r.provider == "aws"
        assert r.region_name == "us-east-1"
        assert r.endpoint_url == "https://example.com/"

    def test_provider_constants_defined(self):
        """Provider constants are defined as expected strings."""
        assert PROVIDER_AWS == "aws"
        assert PROVIDER_AZURE == "azure"
        assert PROVIDER_GCP == "gcp"

    def test_providers_list_contains_all(self):
        """PROVIDERS list contains all three providers."""
        assert PROVIDER_AWS in PROVIDERS
        assert PROVIDER_AZURE in PROVIDERS
        assert PROVIDER_GCP in PROVIDERS
        assert len(PROVIDERS) == 3


class TestRegionCoverage:
    """Tests that each provider has sufficient region entries."""

    def test_aws_has_at_least_5_regions(self):
        """AWS has at least 5 regions defined."""
        regions = get_regions_by_provider(PROVIDER_AWS)
        assert len(regions) >= 5

    def test_azure_has_at_least_5_regions(self):
        """Azure has at least 5 regions defined."""
        regions = get_regions_by_provider(PROVIDER_AZURE)
        assert len(regions) >= 5

    def test_gcp_has_at_least_5_regions(self):
        """GCP has at least 5 regions defined."""
        regions = get_regions_by_provider(PROVIDER_GCP)
        assert len(regions) >= 5


class TestRegionDataQuality:
    """Tests that all region entries have valid data."""

    def test_all_regions_have_non_empty_provider(self):
        """Every region has a non-empty provider string."""
        for region in get_all_regions():
            assert region.provider, f"Empty provider in {region}"

    def test_all_regions_have_non_empty_region_name(self):
        """Every region has a non-empty region_name string."""
        for region in get_all_regions():
            assert region.region_name, f"Empty region_name in {region}"

    def test_all_regions_have_non_empty_endpoint_url(self):
        """Every region has a non-empty endpoint_url string."""
        for region in get_all_regions():
            assert region.endpoint_url, f"Empty endpoint_url in {region}"

    def test_all_endpoints_use_https(self):
        """Every endpoint URL starts with https://."""
        for region in get_all_regions():
            assert region.endpoint_url.startswith("https://"), (
                f"Non-HTTPS endpoint in {region.provider}/{region.region_name}: {region.endpoint_url}"
            )

    def test_all_providers_are_valid(self):
        """Every region uses a recognized provider constant."""
        for region in get_all_regions():
            assert region.provider in PROVIDERS, f"Unknown provider: {region.provider}"


class TestGetAllRegions:
    """Tests for get_all_regions()."""

    def test_returns_list(self):
        """get_all_regions returns a list."""
        result = get_all_regions()
        assert isinstance(result, list)

    def test_returns_combined_count(self):
        """get_all_regions returns all regions from all providers."""
        all_regions = get_all_regions()
        aws = get_regions_by_provider(PROVIDER_AWS)
        azure = get_regions_by_provider(PROVIDER_AZURE)
        gcp = get_regions_by_provider(PROVIDER_GCP)
        assert len(all_regions) == len(aws) + len(azure) + len(gcp)

    def test_returns_new_list(self):
        """get_all_regions returns a copy, not the internal list."""
        r1 = get_all_regions()
        r2 = get_all_regions()
        assert r1 is not r2


class TestGetRegionsByProvider:
    """Tests for get_regions_by_provider()."""

    def test_aws_returns_only_aws(self):
        """Filtering by AWS returns only AWS regions."""
        for region in get_regions_by_provider(PROVIDER_AWS):
            assert region.provider == PROVIDER_AWS

    def test_azure_returns_only_azure(self):
        """Filtering by Azure returns only Azure regions."""
        for region in get_regions_by_provider(PROVIDER_AZURE):
            assert region.provider == PROVIDER_AZURE

    def test_gcp_returns_only_gcp(self):
        """Filtering by GCP returns only GCP regions."""
        for region in get_regions_by_provider(PROVIDER_GCP):
            assert region.provider == PROVIDER_GCP

    def test_invalid_provider_returns_empty(self):
        """Unknown provider returns empty list."""
        assert get_regions_by_provider("invalid") == []

    def test_returns_new_list(self):
        """get_regions_by_provider returns a copy, not the internal list."""
        r1 = get_regions_by_provider(PROVIDER_AWS)
        r2 = get_regions_by_provider(PROVIDER_AWS)
        assert r1 is not r2
