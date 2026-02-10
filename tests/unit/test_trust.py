import time
import pytest
from ateam.security.trust import TrustManager

def test_trust_manager_basic():
    tm = TrustManager()
    assert tm.is_agent_trusted("Coder") is False
    
    # Trust for 2 seconds
    tm.trust_agent("Coder", 2)
    assert tm.is_agent_trusted("Coder") is True
    assert tm.get_remaining_time("Coder") >= 1
    
    # Revoke
    tm.revoke_trust("Coder")
    assert tm.is_agent_trusted("Coder") is False

def test_trust_expiry():
    tm = TrustManager()
    # Trust for 1 second
    tm.trust_agent("Architect", 1)
    assert tm.is_agent_trusted("Architect") is True
    
    # Wait for expiry
    time.sleep(1.1)
    assert tm.is_agent_trusted("Architect") is False
    assert tm.get_remaining_time("Architect") == 0
