import argparse
import sys
import os
from dotenv import load_dotenv
from src.utils.logger import log_experiment
//pour importer les agents 
from src.agents.auditor import audit
from src.agents.fixer import fix
from src.agents.judge import judge 

load_dotenv()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()
  
    
    if not os.path.exists(args.target_dir):
        print(f" Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f" DEMARRAGE SUR : {args.target_dir}")
    logs = []

    for it in range(1,5):
        audit_res=audit()
        logs.append(log("auditor","audit",audit_res))

    if(audit_res["status"]!="tobefixed"):
        break
        fix_res=fix(audit_result["plan"])
        logs.append(log("fixer","fix",fix_res))

    test_res = judge()
    logs.append(log("judge", "test", test_res))

     if test_res["success"]:
            print("Correct normally")
            break
    else:
        print("termine avec failure")
    
    if test_res["success"]:
            print("Correct normally")
            break
    else:
        print("termine avec failure")
    
    log_experiment("System", "STARTUP", f"Target: {args.target_dir}", "INFO")
    print(" MISSION_COMPLETE")
os.makedirs("logs", exist_ok=True) with open(LOG_FILE, "w", encoding="utf-8") as f: json.dump({"events": logs}, f, indent=2)

if __name__ == "__main__":
    main()
