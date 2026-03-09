"""Base POS Connector Interface"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, List

class BasePOSConnector(ABC):
    """Abstract base class for all POS system connectors"""
    
    def __init__(self, config: Dict):
        """
        Initialize connector with configuration
        
        Args:
            config: Dictionary containing connection parameters
                   e.g. {"host": "...", "api_key": "...", "merchant_id": "..."}
        """
        self.config = config
        self.vendor_name = self.__class__.__name__.replace('Connector', '')
    
    @abstractmethod
    async def test_connection(self) -> Dict:
        """
        Test connection to POS system
        
        Returns:
            Dict with keys:
                - success: bool
                - message: str
                - details: Optional[Dict]
        """
        pass
    
    @abstractmethod
    async def push_order(self, order_data: Dict) -> Dict:
        """
        Send order to POS system
        
        Args:
            order_data: Order information including items, customer, etc.
        
        Returns:
            Dict with keys:
                - success: bool
                - pos_order_id: Optional[str]
                - message: str
                - error: Optional[str]
        """
        pass
    
    async def sync_menu(self) -> Dict:
        """
        Sync menu from POS to local database (optional)
        
        Returns:
            Dict with keys:
                - success: bool
                - items_synced: int
                - message: str
        """
        return {
            "success": False,
            "items_synced": 0,
            "message": "Menu sync not implemented for this POS system"
        }
    
    async def get_order_status(self, pos_order_id: str) -> Dict:
        """
        Get order status from POS system (optional)
        
        Args:
            pos_order_id: POS system's order identifier
        
        Returns:
            Dict with keys:
                - success: bool
                - status: Optional[str]
                - message: str
        """
        return {
            "success": False,
            "status": None,
            "message": "Order status check not implemented for this POS system"
        }
    
    def get_vendor_name(self) -> str:
        """Get the vendor name of this connector"""
        return self.vendor_name
