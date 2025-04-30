import os
import httpx
from typing import Dict, List, Any
from fastapi import HTTPException

class DuneClient:
    def __init__(self):
        self.api_key = os.getenv("DUNE_API_KEY")
        self.base_url = "https://api.dune.com/api/v1"
        self.client = httpx.AsyncClient()
    
    async def query(self, query_path: str, params: Dict[str, Any] = None) -> List[Dict]:
        """Execute a Dune Analytics query"""
        try:
            # First get query ID from path
            query_id = await self._get_query_id(query_path)
            
            # Execute query with parameters
            exec_response = await self.client.post(
                f"{self.base_url}/query/{query_id}/execute",
                headers={"X-Dune-API-Key": self.api_key},
                json={"query_parameters": params or {}}
            )
            exec_response.raise_for_status()
            execution_id = exec_response.json()["execution_id"]
            
            # Wait for results
            results = await self._wait_for_results(execution_id)
            return results
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Dune API error: {e.response.text}"
            )
    
    async def _get_query_id(self, query_path: str) -> str:
        """Map query path to Dune query ID (would maintain a mapping)"""
        # In a real implementation, this would map paths to query IDs
        query_mapping = {
            "token_analysis/launches": "123456",
            "token_analysis/liquidity": "789012",
            # ... other query mappings
        }
        return query_mapping.get(query_path)
    
    async def _wait_for_results(self, execution_id: str, timeout: int = 60) -> List[Dict]:
        """Wait for query execution to complete"""
        status = "QUERY_STATE_PENDING"
        attempts = 0
        
        while status != "QUERY_STATE_COMPLETED" and attempts < timeout:
            status_response = await self.client.get(
                f"{self.base_url}/execution/{execution_id}/status",
                headers={"X-Dune-API-Key": self.api_key}
            )
            status = status_response.json()["state"]
            
            if status == "QUERY_STATE_FAILED":
                raise HTTPException(
                    status_code=500,
                    detail="Dune query execution failed"
                )
            
            attempts += 1
            await asyncio.sleep(1)
        
        # Get results
        results_response = await self.client.get(
            f"{self.base_url}/execution/{execution_id}/results",
            headers={"X-Dune-API-Key": self.api_key}
        )
        return results_response.json()["result"]["rows"]