import sys
import os

# Add the workspace to python path so we can import config
sys.path.append(os.getcwd())

from config.app_config.app_config_manager import AppConfigManager

def test_config():
    print("Testing AppConfigManager Dynamic Selection...")
    
    # 1. Singleton & Initial Load (Should load ferrari based on settings.env default)
    c1 = AppConfigManager()
    
    print(f"Available Projects: {c1.get_available_projects()}")
    
    try:
        val = c1.ProjectConfiguration.EXECUTE_GROUP
        print(f"[PASS] Initial Load (ferrari): EXECUTE_GROUP={val}")
    except Exception as e:
        print(f"[FAIL] Initial Load failed: {e}")

    # 2. Dynamic Switching
    # Let's create a dummy project 'audi.env' first to test switching
    audi_path = os.path.join(c1.projects_dir, "audi.env")
    with open(audi_path, 'w') as f:
        f.write("# Project Configuration\nEXECUTE_GROUP=AUDI_PCTS\n")
    
    try:
        print("Switching to 'audi'...")
        c1.set_default_project("audi")
        
        # Verify persistence file
        with open(c1.settings_file, 'r') as f:
            content = f.read().strip()
        print(f"Settings file content: {content}")
        if "DEFAULT_PROJECT=audi" in content:
            print("[PASS] Persistence file updated")
        else:
            print("[FAIL] Persistence file not updated")

        # Verify value change
        val = c1.ProjectConfiguration.EXECUTE_GROUP
        if val == "AUDI_PCTS":
            print(f"[PASS] Switched to Audi: EXECUTE_GROUP={val}")
        else:
             print(f"[FAIL] Switch failed, val={val}")
             
    except Exception as e:
        print(f"[FAIL] Switching failed: {e}")

    # 3. Persistence Check (New Instance)
    # Since it's a singleton, we can't easily kill the instance in the same process
    # But we can verify that if we were to re-init (logic-wise), it reads the file.
    # We effectively tested this via _get_persistent_default() implicitly, 
    # but let's verify the method explicitly returns 'audi' now.
    
    default = c1._get_persistent_default()
    if default == "audi":
        print("[PASS] _get_persistent_default returns 'audi'")
    else:
        print(f"[FAIL] _get_persistent_default returned {default}")

    # Cleanup: Switch back to ferrari and delete audi
    c1.set_default_project("ferrari")
    if os.path.exists(audi_path):
        os.remove(audi_path)
    print("Restored to ferrari and cleaned up.")

if __name__ == "__main__":
    test_config()
