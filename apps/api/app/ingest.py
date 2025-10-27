"""Ingestion service for fetching and parsing SPL XML from DailyMed."""

import re
from typing import cast

import httpx
from lxml import etree
from rag_health_core import ChunkMetadata, DrugDocument, Settings
from rag_health_retrieval import EmbeddingService, RedisClient, chunk_text

# SPL section code -> normalized name mapping
SECTION_MAPPING = {
    "34067-9": "INDICATIONS_AND_USAGE",
    "34068-7": "DOSAGE_AND_ADMINISTRATION",
    "34070-3": "CONTRAINDICATIONS",
    "43685-7": "WARNINGS_AND_PRECAUTIONS",
    "34084-4": "ADVERSE_REACTIONS",
    "43684-0": "USE_IN_SPECIFIC_POPULATIONS",
    "34069-5": "HOW_SUPPLIED_STORAGE_AND_HANDLING",
    "34076-0": "PATIENT_COUNSELING_INFORMATION",
    "34090-1": "CLINICAL_PHARMACOLOGY",
}


class IngestionService:
    """Service for ingesting drug labels from DailyMed."""

    def __init__(self, settings: Settings) -> None:
        """Initialize ingestion service."""
        self.settings = settings
        self.redis_client = RedisClient(settings)
        self.embedding_service = EmbeddingService(settings)
        self.client = httpx.AsyncClient(timeout=30.0)

    async def ingest_drug(self, drug_name: str) -> int:
        """Fetch, parse, chunk, embed, and index a drug label.

        Returns the number of chunks ingested.
        """
        # Search DailyMed for the drug
        setid = await self._search_dailymed(drug_name)
        if not setid:
            raise ValueError(f"Drug not found: {drug_name}")

        # Fetch SPL XML
        xml_content = await self._fetch_spl_xml(setid)

        # Parse document
        doc = self._parse_spl(xml_content, setid, drug_name)

        # Chunk and embed
        chunks = self._chunk_document(doc)

        # Batch embed
        texts = [chunk.text for chunk in chunks]
        embeddings = self.embedding_service.embed_batch(texts)

        # Upsert to Redis
        for chunk, emb in zip(chunks, embeddings, strict=False):
            self.redis_client.upsert_chunk(chunk, emb)

        return len(chunks)

    async def _search_dailymed(self, drug_name: str) -> str | None:
        """Search DailyMed API for drug setid."""
        url = "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json"
        params = {"drug_name": drug_name}

        response = await self.client.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        spls = data.get("data", [])

        if not spls:
            return None

        # Return first result's setid
        setid = spls[0].get("setid")
        return str(setid) if setid is not None else None

    async def _fetch_spl_xml(self, setid: str) -> bytes:
        """Fetch SPL XML for a given setid."""
        url = f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{setid}.xml"
        response = await self.client.get(url)
        response.raise_for_status()
        return response.content

    def _parse_spl(self, xml_content: bytes, setid: str, drug_name: str) -> DrugDocument:
        """Parse SPL XML into DrugDocument."""
        tree = etree.fromstring(xml_content)

        # Define namespace
        nsmap = {"hl7": "urn:hl7-org:v3"}

        # Extract NDC codes (if present)
        ndc_codes = self._extract_ndc(tree, nsmap)

        # Extract sections
        sections = self._extract_sections(tree, nsmap)

        url = f"https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid={setid}"

        return DrugDocument(
            drug_name=drug_name,
            setid=setid,
            ndc=ndc_codes,
            version=1,
            url=url,
            sections=sections,
        )

    def _extract_ndc(self, tree: etree._Element, nsmap: dict[str, str]) -> list[str]:
        """Extract NDC codes from SPL XML."""
        ndc_codes = []
        # xpath returns a list of _Element objects
        code_elements: list[etree._Element] = cast(
            list[etree._Element],
            tree.xpath("//hl7:code[@codeSystem='2.16.840.1.113883.6.69']", namespaces=nsmap),
        )
        for code_element in code_elements:
            if code_val := code_element.get("code"):
                ndc_codes.append(code_val)
        return ndc_codes

    def _extract_sections(self, tree: etree._Element, nsmap: dict[str, str]) -> dict[str, str]:
        """Extract sections from SPL XML."""
        sections = {}

        # Find all section elements
        section_elements: list[etree._Element] = cast(
            list[etree._Element], tree.xpath("//hl7:section", namespaces=nsmap)
        )
        for section_element in section_elements:
            # Get section code
            code_elem = section_element.find(
                ".//hl7:code[@codeSystem='2.16.840.1.113883.6.1']", namespaces=nsmap
            )
            if code_elem is None:
                continue

            section_code = code_elem.get("code")
            if section_code not in SECTION_MAPPING:
                continue

            section_id = section_code

            # Extract text content
            text_parts = []
            # xpath with text() returns text nodes (strings)
            text_nodes: list[str] = cast(
                list[str], section_element.xpath(".//hl7:text//text()", namespaces=nsmap)
            )
            for text_node in text_nodes:
                text_parts.append(str(text_node).strip())

            text = " ".join(text_parts).strip()
            text = re.sub(r"\s+", " ", text)  # Normalize whitespace

            if text:
                sections[section_id] = text

        return sections

    def _chunk_document(self, doc: DrugDocument) -> list[ChunkMetadata]:
        """Chunk document sections into embeddable chunks."""
        chunks = []

        for section_id, text in doc.sections.items():
            # Map section_id to normalized name
            section_name = SECTION_MAPPING.get(section_id, "OTHER")

            # Chunk text
            text_chunks = chunk_text(
                text,
                chunk_size=self.settings.chunk_size,
                overlap=self.settings.chunk_overlap,
            )

            # Create chunk metadata
            for idx, chunk_content in enumerate(text_chunks):
                chunks.append(
                    ChunkMetadata(
                        drug_name=doc.drug_name,
                        setid=doc.setid,
                        ndc=doc.ndc,
                        version=doc.version,
                        section=section_name,
                        section_id=section_id,
                        url=doc.url,
                        text=chunk_content,
                        chunk_index=idx,
                    )
                )

        return chunks
