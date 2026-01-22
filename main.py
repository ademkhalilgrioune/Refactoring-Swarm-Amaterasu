import argparse
import sys
import os
import json
from dotenv import load_dotenv
from src.utils.logger import log_experiment
from src.agents.auditor import audit
from src.agents.fixer import fix
from src.agents.judge import judge

load_dotenv()

LOG_FILE = "logs/experiment_log.json"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target_dir", type=str, required=True)
    args = parser.parse_args()
    
    if not os.path.exists(args.target_dir):
        print(f" Dossier {args.target_dir} introuvable.")
        sys.exit(1)

    print(f" DEMARRAGE SUR : {args.target_dir}")

    log_experiment("System", "STARTUP", f"Target: {args.target_dir}", "INFO")
    
    logs = []


    for iteration in range(1, 5):
    
        audit_res = audit()
        logs.append({
            "agent": "auditor",
            "action": "audit",
            "result": audit_res,
            "iteration": iteration
        })
        

        if audit_res.get("status") != "tobefixed":
            break
            

        fix_res = fix(audit_res.get("plan", {}))
        logs.append({
            "agent": "fixer",
            "action": "fix",
            "result": fix_res,
            "iteration": iteration
        })
    
        test_res = judge()
        logs.append({
            "agent": "judge",
            "action": "test",
            "result": test_res,
            "iteration": iteration
        })

        if test_res.get("success"):
            print("Correct normally")
            break
        elif iteration == 4:
            print("Terminé avec échec (max iterations atteint)")
    
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump({"events": logs}, f, indent=2)
    
    print(" MISSION_COMPLETE")

if __name__ == "__main__":
    main()
