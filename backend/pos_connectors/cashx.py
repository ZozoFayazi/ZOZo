"""Cash-X POS Connector (Skeleton for future implementation)"""
import logging
from typing import Dict
from .base import BasePOSConnector

logger = logging.getLogger(__name__)

class CashXConnector(BasePOSConnector):
    """
    Connector for Cash-X POS system
    
    This is a skeleton implementation prepared for future integration.
    All methods return not-implemented responses.
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = config.get('base_url', 'https://api.cash-x.com/v1')
        self.api_key = config.get('api_key')
        self.terminal_id = config.get('terminal_id')
        self.environment = config.get('environment', 'test')
    
    async def test_connection(self) -> Dict:
        """Test connection - Not yet implemented"""
        logger.info("Cash-X connector called but not yet implemented")
        return {
            "success": False,
            "message": "Cash-X Integration ist noch nicht verfügbar",
            "details": {
                "status": "not_implemented",
                "environment": self.environment
            }
        }
    
    async def push_order(self, order_data: Dict) -> Dict:
        """Push order - Not yet implemented"""
        logger.info("Cash-X push_order called but not yet implemented")
        return {
            "success": False,
            "pos_order_id": None,
            "message": "Cash-X Integration ist noch nicht verfügbar",
            "error": "not_implemented"
        }
    
    # Future methods when implementing Cash-X:
    # - _get_headers()
    # - _transform_order()
    # - async def sync_menu()
    # - async def get_order_status()
