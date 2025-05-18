import os
from dotenv import load_dotenv
from loguru import logger
from sentinelhub import SHConfig

# Load environment variables
load_dotenv()

class SentinelConfig:
    """Configuration for Sentinel Hub credentials and settings."""
    
    def __init__(self):
        """Initialize Sentinel Hub configuration using SHConfig."""
        self.config = SHConfig()
        self.config.sh_client_id = '6fc4acf0-cd2e-4097-b61d-5582083e0ab4'
        self.config.sh_client_secret = 'B1d0KSm6A4VdD7WdDFb6B88y2TGpkPVv'
        
        # Validate credentials
        self._validate_credentials()
        
    def _validate_credentials(self):
        """Validate that all required credentials are present."""
        missing = []
        if not self.config.sh_client_id:
            missing.append('client_id')
        if not self.config.sh_client_secret:
            missing.append('client_secret')
            
        if missing:
            error_msg = f"Missing Sentinel Hub credentials: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
    def get_credentials(self):
        """Return SHConfig object with credentials."""
        return self.config

# Create template .env file if it doesn't exist
env_template = """# Sentinel Hub Credentials
SENTINEL_CLIENT_ID=your_client_id_here
SENTINEL_CLIENT_SECRET=your_client_secret_here
SENTINEL_INSTANCE_ID=your_instance_id_here
"""

if not os.path.exists('.env'):
    with open('.env', 'w') as f:
        f.write(env_template)
    logger.info("Created template .env file. Please fill in your Sentinel Hub credentials.") 