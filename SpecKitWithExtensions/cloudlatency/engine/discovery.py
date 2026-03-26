"""Region discovery for AWS, Azure, and GCP cloud providers."""

import logging

import aiohttp

from cloudlatency.engine.models import CloudRegion

logger = logging.getLogger("cloudlatency.engine.discovery")

# Provider display names
PROVIDER_NAMES = {"aws": "AWS", "azure": "Azure", "gcp": "GCP"}

# AWS region name mappings (subset — unknown regions use region code as name)
AWS_REGION_NAMES = {
    "us-east-1": "US East (N. Virginia)",
    "us-east-2": "US East (Ohio)",
    "us-west-1": "US West (N. California)",
    "us-west-2": "US West (Oregon)",
    "af-south-1": "Africa (Cape Town)",
    "ap-east-1": "Asia Pacific (Hong Kong)",
    "ap-south-1": "Asia Pacific (Mumbai)",
    "ap-south-2": "Asia Pacific (Hyderabad)",
    "ap-southeast-1": "Asia Pacific (Singapore)",
    "ap-southeast-2": "Asia Pacific (Sydney)",
    "ap-southeast-3": "Asia Pacific (Jakarta)",
    "ap-northeast-1": "Asia Pacific (Tokyo)",
    "ap-northeast-2": "Asia Pacific (Seoul)",
    "ap-northeast-3": "Asia Pacific (Osaka)",
    "ca-central-1": "Canada (Central)",
    "eu-central-1": "Europe (Frankfurt)",
    "eu-west-1": "Europe (Ireland)",
    "eu-west-2": "Europe (London)",
    "eu-west-3": "Europe (Paris)",
    "eu-south-1": "Europe (Milan)",
    "eu-south-2": "Europe (Spain)",
    "eu-north-1": "Europe (Stockholm)",
    "me-south-1": "Middle East (Bahrain)",
    "me-central-1": "Middle East (UAE)",
    "sa-east-1": "South America (São Paulo)",
    "il-central-1": "Israel (Tel Aviv)",
}


async def discover_aws_regions() -> list[CloudRegion]:
    """Discover AWS regions from ip-ranges.amazonaws.com."""
    url = "https://ip-ranges.amazonaws.com/ip-ranges.json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    logger.warning("AWS IP ranges API returned status %d", resp.status)
                    return []
                data = await resp.json()
    except Exception as e:
        logger.error("Failed to fetch AWS regions: %s", e)
        return []

    seen: set[str] = set()
    regions: list[CloudRegion] = []
    for prefix in data.get("prefixes", []):
        if prefix.get("service") != "EC2":
            continue
        code = prefix.get("region", "")
        if not code or code in seen:
            continue
        seen.add(code)
        regions.append(
            CloudRegion(
                provider_id="aws",
                region_code=code,
                region_name=AWS_REGION_NAMES.get(code, code),
                endpoint_url=f"https://ec2.{code}.amazonaws.com",
            )
        )

    logger.info("Discovered %d AWS regions", len(regions))
    return regions


# Hardcoded Azure region registry — Management API requires OAuth2 auth.
# Using Blob Storage endpoints (https://<account>.blob.core.windows.net) for probing.
# // DRIFT: Azure discovery changed from dynamic API to hardcoded list (API requires auth)
AZURE_REGIONS: list[tuple[str, str]] = [
    ("eastus", "East US"),
    ("eastus2", "East US 2"),
    ("southcentralus", "South Central US"),
    ("westus2", "West US 2"),
    ("westus3", "West US 3"),
    ("australiaeast", "Australia East"),
    ("southeastasia", "Southeast Asia"),
    ("northeurope", "North Europe"),
    ("swedencentral", "Sweden Central"),
    ("uksouth", "UK South"),
    ("westeurope", "West Europe"),
    ("centralus", "Central US"),
    ("southafricanorth", "South Africa North"),
    ("centralindia", "Central India"),
    ("eastasia", "East Asia"),
    ("japaneast", "Japan East"),
    ("koreacentral", "Korea Central"),
    ("canadacentral", "Canada Central"),
    ("francecentral", "France Central"),
    ("germanywestcentral", "Germany West Central"),
    ("italynorth", "Italy North"),
    ("norwayeast", "Norway East"),
    ("polandcentral", "Poland Central"),
    ("spaincentral", "Spain Central"),
    ("switzerlandnorth", "Switzerland North"),
    ("mexicocentral", "Mexico Central"),
    ("uaenorth", "UAE North"),
    ("brazilsouth", "Brazil South"),
    ("israelcentral", "Israel Central"),
    ("qatarcentral", "Qatar Central"),
    ("centraluseuap", "Central US EUAP"),
    ("eastus2euap", "East US 2 EUAP"),
    ("westus", "West US"),
    ("northcentralus", "North Central US"),
    ("westcentralus", "West Central US"),
    ("australiasoutheast", "Australia Southeast"),
    ("japanwest", "Japan West"),
    ("koreasouth", "Korea South"),
    ("southindia", "South India"),
    ("westindia", "West India"),
    ("canadaeast", "Canada East"),
    ("ukwest", "UK West"),
    ("francesouth", "France South"),
    ("germanynorth", "Germany North"),
    ("norwaywest", "Norway West"),
    ("switzerlandwest", "Switzerland West"),
    ("australiacentral", "Australia Central"),
    ("australiacentral2", "Australia Central 2"),
    ("southafricawest", "South Africa West"),
    ("uaecentral", "UAE Central"),
    ("brazilsoutheast", "Brazil Southeast"),
    ("jioindiawest", "Jio India West"),
    ("jioindiacentral", "Jio India Central"),
    ("swedensouth", "Sweden South"),
    ("taiwannorth", "Taiwan North"),
    ("newzealandnorth", "New Zealand North"),
    ("indonesiacentral", "Indonesia Central"),
    ("malaysiawest", "Malaysia West"),
    ("chileancentral", "Chilean Central"),
]


async def discover_azure_regions() -> list[CloudRegion]:
    """Return Azure regions from hardcoded registry with Blob Storage probe endpoints."""
    regions: list[CloudRegion] = [
        CloudRegion(
            provider_id="azure",
            region_code=code,
            region_name=name,
            endpoint_url=f"https://{code}.blob.core.windows.net",
        )
        for code, name in AZURE_REGIONS
    ]
    logger.info("Loaded %d Azure regions from registry", len(regions))
    return regions


async def discover_gcp_regions() -> list[CloudRegion]:
    """Discover GCP regions from gstatic.com cloud.json."""
    url = "https://www.gstatic.com/ipranges/cloud.json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    logger.warning("GCP IP ranges API returned status %d", resp.status)
                    return []
                data = await resp.json()
    except Exception as e:
        logger.error("Failed to fetch GCP regions: %s", e)
        return []

    seen: set[str] = set()
    regions: list[CloudRegion] = []
    for prefix in data.get("prefixes", []):
        scope = prefix.get("scope", "")
        if not scope or scope in seen or scope == "global":
            continue
        # Filter out non-region scopes (zones like us-central1-a)
        if scope.count("-") > 1 and scope[-1].isalpha() and scope[-2] == "-":
            continue
        seen.add(scope)
        regions.append(
            CloudRegion(
                provider_id="gcp",
                region_code=scope,
                region_name=scope.replace("-", " ").title(),
                endpoint_url=f"https://{scope}-run.googleapis.com",
            )
        )

    logger.info("Discovered %d GCP regions", len(regions))
    return regions


async def discover_all_regions() -> list[CloudRegion]:
    """Discover regions from all cloud providers concurrently."""
    import asyncio

    results = await asyncio.gather(
        discover_aws_regions(),
        discover_azure_regions(),
        discover_gcp_regions(),
        return_exceptions=True,
    )

    all_regions: list[CloudRegion] = []
    for result in results:
        if isinstance(result, list):
            all_regions.extend(result)
        elif isinstance(result, Exception):
            logger.error("Provider discovery failed: %s", result)

    logger.info("Total regions discovered: %d", len(all_regions))
    return all_regions
