"""Cloud region endpoint definitions for Azure, AWS, and GCP."""

from __future__ import annotations

from typing import NamedTuple

PROVIDER_AWS = "aws"
PROVIDER_AZURE = "azure"
PROVIDER_GCP = "gcp"
PROVIDERS = [PROVIDER_AWS, PROVIDER_AZURE, PROVIDER_GCP]


class Region(NamedTuple):
    """A cloud region with its health-check endpoint."""

    provider: str
    region_name: str
    endpoint_url: str


# ---------------------------------------------------------------------------
# AWS Regions — using DynamoDB regional endpoints (publicly accessible HTTPS)
# ---------------------------------------------------------------------------
_AWS_REGIONS: list[Region] = [
    Region(PROVIDER_AWS, "us-east-1", "https://dynamodb.us-east-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "us-east-2", "https://dynamodb.us-east-2.amazonaws.com/"),
    Region(PROVIDER_AWS, "us-west-1", "https://dynamodb.us-west-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "us-west-2", "https://dynamodb.us-west-2.amazonaws.com/"),
    Region(PROVIDER_AWS, "ca-central-1", "https://dynamodb.ca-central-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "ca-west-1", "https://dynamodb.ca-west-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "eu-west-1", "https://dynamodb.eu-west-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "eu-west-2", "https://dynamodb.eu-west-2.amazonaws.com/"),
    Region(PROVIDER_AWS, "eu-west-3", "https://dynamodb.eu-west-3.amazonaws.com/"),
    Region(PROVIDER_AWS, "eu-central-1", "https://dynamodb.eu-central-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "eu-central-2", "https://dynamodb.eu-central-2.amazonaws.com/"),
    Region(PROVIDER_AWS, "eu-north-1", "https://dynamodb.eu-north-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "eu-south-1", "https://dynamodb.eu-south-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "eu-south-2", "https://dynamodb.eu-south-2.amazonaws.com/"),
    Region(PROVIDER_AWS, "ap-southeast-1", "https://dynamodb.ap-southeast-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "ap-southeast-2", "https://dynamodb.ap-southeast-2.amazonaws.com/"),
    Region(PROVIDER_AWS, "ap-southeast-3", "https://dynamodb.ap-southeast-3.amazonaws.com/"),
    Region(PROVIDER_AWS, "ap-southeast-4", "https://dynamodb.ap-southeast-4.amazonaws.com/"),
    Region(PROVIDER_AWS, "ap-northeast-1", "https://dynamodb.ap-northeast-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "ap-northeast-2", "https://dynamodb.ap-northeast-2.amazonaws.com/"),
    Region(PROVIDER_AWS, "ap-northeast-3", "https://dynamodb.ap-northeast-3.amazonaws.com/"),
    Region(PROVIDER_AWS, "ap-south-1", "https://dynamodb.ap-south-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "ap-south-2", "https://dynamodb.ap-south-2.amazonaws.com/"),
    Region(PROVIDER_AWS, "ap-east-1", "https://dynamodb.ap-east-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "sa-east-1", "https://dynamodb.sa-east-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "me-south-1", "https://dynamodb.me-south-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "me-central-1", "https://dynamodb.me-central-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "af-south-1", "https://dynamodb.af-south-1.amazonaws.com/"),
    Region(PROVIDER_AWS, "il-central-1", "https://dynamodb.il-central-1.amazonaws.com/"),
]

# ---------------------------------------------------------------------------
# Azure Regions — using Azure Blob Storage regional endpoints
# ---------------------------------------------------------------------------
_AZURE_REGIONS: list[Region] = [
    Region(PROVIDER_AZURE, "eastus", "https://eastus.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "eastus2", "https://eastus2.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "westus", "https://westus.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "westus2", "https://westus2.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "westus3", "https://westus3.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "centralus", "https://centralus.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "northcentralus", "https://northcentralus.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "southcentralus", "https://southcentralus.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "canadacentral", "https://canadacentral.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "canadaeast", "https://canadaeast.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "brazilsouth", "https://brazilsouth.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "northeurope", "https://northeurope.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "westeurope", "https://westeurope.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "uksouth", "https://uksouth.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "ukwest", "https://ukwest.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "francecentral", "https://francecentral.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "francesouth", "https://francesouth.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "germanywestcentral", "https://germanywestcentral.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "norwayeast", "https://norwayeast.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "switzerlandnorth", "https://switzerlandnorth.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "swedencentral", "https://swedencentral.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "polandcentral", "https://polandcentral.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "italynorth", "https://italynorth.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "spaincentral", "https://spaincentral.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "eastasia", "https://eastasia.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "southeastasia", "https://southeastasia.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "japaneast", "https://japaneast.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "japanwest", "https://japanwest.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "australiaeast", "https://australiaeast.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "australiasoutheast", "https://australiasoutheast.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "centralindia", "https://centralindia.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "southindia", "https://southindia.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "koreacentral", "https://koreacentral.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "koreasouth", "https://koreasouth.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "southafricanorth", "https://southafricanorth.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "uaenorth", "https://uaenorth.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "qatarcentral", "https://qatarcentral.prod.warm.ingest.monitor.core.windows.net/"),
    Region(PROVIDER_AZURE, "israelcentral", "https://israelcentral.prod.warm.ingest.monitor.core.windows.net/"),
]

# ---------------------------------------------------------------------------
# GCP Regions — using Cloud Run regional endpoints
# ---------------------------------------------------------------------------
_GCP_REGIONS: list[Region] = [
    Region(PROVIDER_GCP, "us-central1", "https://us-central1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "us-east1", "https://us-east1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "us-east4", "https://us-east4-run.googleapis.com/"),
    Region(PROVIDER_GCP, "us-east5", "https://us-east5-run.googleapis.com/"),
    Region(PROVIDER_GCP, "us-west1", "https://us-west1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "us-west2", "https://us-west2-run.googleapis.com/"),
    Region(PROVIDER_GCP, "us-west3", "https://us-west3-run.googleapis.com/"),
    Region(PROVIDER_GCP, "us-west4", "https://us-west4-run.googleapis.com/"),
    Region(PROVIDER_GCP, "us-south1", "https://us-south1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "northamerica-northeast1", "https://northamerica-northeast1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "northamerica-northeast2", "https://northamerica-northeast2-run.googleapis.com/"),
    Region(PROVIDER_GCP, "southamerica-east1", "https://southamerica-east1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "southamerica-west1", "https://southamerica-west1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "europe-west1", "https://europe-west1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "europe-west2", "https://europe-west2-run.googleapis.com/"),
    Region(PROVIDER_GCP, "europe-west3", "https://europe-west3-run.googleapis.com/"),
    Region(PROVIDER_GCP, "europe-west4", "https://europe-west4-run.googleapis.com/"),
    Region(PROVIDER_GCP, "europe-west6", "https://europe-west6-run.googleapis.com/"),
    Region(PROVIDER_GCP, "europe-west8", "https://europe-west8-run.googleapis.com/"),
    Region(PROVIDER_GCP, "europe-west9", "https://europe-west9-run.googleapis.com/"),
    Region(PROVIDER_GCP, "europe-west10", "https://europe-west10-run.googleapis.com/"),
    Region(PROVIDER_GCP, "europe-west12", "https://europe-west12-run.googleapis.com/"),
    Region(PROVIDER_GCP, "europe-north1", "https://europe-north1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "europe-central2", "https://europe-central2-run.googleapis.com/"),
    Region(PROVIDER_GCP, "europe-southwest1", "https://europe-southwest1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "asia-east1", "https://asia-east1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "asia-east2", "https://asia-east2-run.googleapis.com/"),
    Region(PROVIDER_GCP, "asia-northeast1", "https://asia-northeast1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "asia-northeast2", "https://asia-northeast2-run.googleapis.com/"),
    Region(PROVIDER_GCP, "asia-northeast3", "https://asia-northeast3-run.googleapis.com/"),
    Region(PROVIDER_GCP, "asia-south1", "https://asia-south1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "asia-south2", "https://asia-south2-run.googleapis.com/"),
    Region(PROVIDER_GCP, "asia-southeast1", "https://asia-southeast1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "asia-southeast2", "https://asia-southeast2-run.googleapis.com/"),
    Region(PROVIDER_GCP, "australia-southeast1", "https://australia-southeast1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "australia-southeast2", "https://australia-southeast2-run.googleapis.com/"),
    Region(PROVIDER_GCP, "me-west1", "https://me-west1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "me-central1", "https://me-central1-run.googleapis.com/"),
    Region(PROVIDER_GCP, "africa-south1", "https://africa-south1-run.googleapis.com/"),
]

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
_ALL_REGIONS: list[Region] = _AWS_REGIONS + _AZURE_REGIONS + _GCP_REGIONS

_REGIONS_BY_PROVIDER: dict[str, list[Region]] = {
    PROVIDER_AWS: _AWS_REGIONS,
    PROVIDER_AZURE: _AZURE_REGIONS,
    PROVIDER_GCP: _GCP_REGIONS,
}


def get_all_regions() -> list[Region]:
    """Return a flat list of all cloud regions across all providers."""
    return list(_ALL_REGIONS)


def get_regions_by_provider(provider: str) -> list[Region]:
    """Return regions for a specific provider, or empty list if provider unknown."""
    return list(_REGIONS_BY_PROVIDER.get(provider, []))
