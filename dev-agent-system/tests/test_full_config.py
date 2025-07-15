"""
Full configuration integration test for ADOS
Tests that all configuration files load and integrate properly
"""

import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.config_loader import ConfigLoader, load_config, validate_ados_config


def test_full_configuration():
    """Test loading and validating all configuration files"""
    
    print("🔧 Testing ADOS Configuration System")
    print("=" * 50)
    
    # Load configuration
    loader = load_config()
    
    # Test 1: Load crews configuration
    print("\n1. Loading crews configuration...")
    crews = loader.load_crews_config()
    print(f"   ✓ Loaded {len(crews)} crews")
    for crew_name in crews:
        print(f"   - {crew_name}")
    
    # Test 2: Load agents configuration
    print("\n2. Loading agents configuration...")
    agents = loader.load_agents_config()
    total_agents = sum(len(crew_agents) for crew_agents in agents.values())
    print(f"   ✓ Loaded {total_agents} agents across {len(agents)} crews")
    for crew_name, crew_agents in agents.items():
        print(f"   - {crew_name}: {len(crew_agents)} agents")
        for agent in crew_agents:
            print(f"     • {agent.role}")
    
    # Test 3: Load tech stack
    print("\n3. Loading technology stack...")
    tech_stack = loader.load_tech_stack()
    print(f"   ✓ Loaded tech stack with {len(tech_stack)} categories")
    for category in tech_stack:
        print(f"   - {category}")
    
    # Test 4: Load system settings
    print("\n4. Loading system settings...")
    settings = loader.load_system_settings()
    print(f"   ✓ Loaded system settings with {len(settings)} sections")
    for section in settings:
        print(f"   - {section}")
    
    # Test 5: Validate configuration integrity
    print("\n5. Validating configuration integrity...")
    validation = loader.validate_config_integrity()
    print(f"   ✓ Configuration valid: {validation['valid']}")
    if validation['errors']:
        print(f"   ❌ Errors: {len(validation['errors'])}")
        for error in validation['errors']:
            print(f"      - {error}")
    if validation['warnings']:
        print(f"   ⚠️  Warnings: {len(validation['warnings'])}")
        for warning in validation['warnings']:
            print(f"      - {warning}")
    
    # Test 6: Crew-agent alignment
    print("\n6. Checking crew-agent alignment...")
    all_aligned = True
    for crew_name in crews:
        if crew_name not in agents:
            print(f"   ❌ Crew '{crew_name}' has no agents defined")
            all_aligned = False
        else:
            agent_count = len(agents[crew_name])
            print(f"   ✓ {crew_name}: {agent_count} agents")
    
    # Test 7: Tool references validation
    print("\n7. Validating tool references...")
    all_tools = set()
    for crew_config in crews.values():
        all_tools.update(crew_config.tools)
    for crew_agents in agents.values():
        for agent in crew_agents:
            all_tools.update(agent.tools)
    
    print(f"   ✓ Found {len(all_tools)} unique tools referenced")
    tool_categories = {}
    for tool in all_tools:
        if '.' in tool:
            category = tool.split('.')[0]
            tool_categories[category] = tool_categories.get(category, 0) + 1
    
    print("   Tool categories:")
    for category, count in tool_categories.items():
        print(f"   - {category}: {count} tools")
    
    # Test 8: LLM configuration
    print("\n8. Checking LLM configuration...")
    llm_models = set()
    for crew_agents in agents.values():
        for agent in crew_agents:
            llm_models.add(agent.llm)
    print(f"   ✓ LLM models in use: {', '.join(llm_models)}")
    
    # Test 9: Memory configuration
    print("\n9. Validating memory configuration...")
    memory_config = settings.get('memory', {})
    if memory_config:
        print(f"   ✓ Vector DB: {memory_config.get('vector_db', {}).get('provider', 'Not configured')}")
        print(f"   ✓ Crew memory: {memory_config.get('crew_memory', {}).get('type', 'Not configured')}")
    
    # Test 10: Output configuration
    print("\n10. Checking output configuration...")
    output_config = settings.get('output', {})
    if output_config:
        print(f"   ✓ Base directory: {output_config.get('base_directory', 'Not configured')}")
        print(f"   ✓ Logging level: {output_config.get('logging', {}).get('level', 'Not configured')}")
    
    print("\n" + "=" * 50)
    print("✅ Configuration system test complete!")
    
    # Return summary
    return {
        "crews": len(crews),
        "agents": total_agents,
        "tools": len(all_tools),
        "valid": validation['valid'],
        "errors": len(validation.get('errors', [])),
        "warnings": len(validation.get('warnings', []))
    }


if __name__ == "__main__":
    try:
        summary = test_full_configuration()
        
        print("\n📊 Summary:")
        print(f"   - Crews configured: {summary['crews']}")
        print(f"   - Agents configured: {summary['agents']}")
        print(f"   - Tools referenced: {summary['tools']}")
        print(f"   - Configuration valid: {summary['valid']}")
        print(f"   - Errors: {summary['errors']}")
        print(f"   - Warnings: {summary['warnings']}")
        
        if summary['valid'] and summary['errors'] == 0:
            print("\n✅ All configuration tests passed!")
            exit(0)
        else:
            print("\n❌ Configuration has errors!")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)