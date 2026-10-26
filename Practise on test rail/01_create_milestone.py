"""
Step 1 – Create milestone "AuomationPractiseQA" in Ultriva project (ID 15).
Run: python "Practise on test rail/01_create_milestone.py"  (from qa_automation/)
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.config import TESTRAIL_PROJECT_ID, TESTRAIL_API_KEY
from utils.testrail_client import TestRailClient

NAME = "AuomationPractiseQA"

if not TESTRAIL_API_KEY:
    print("[ERROR] TESTRAIL_API_KEY not set."); sys.exit(1)

tr = TestRailClient()

# Create milestone
ms = tr._client.milestones.add_milestone(project_id=TESTRAIL_PROJECT_ID, name=NAME)
print(f"[OK] Milestone created: M{ms['id']}  '{ms['name']}'")

# Step 1
# python "Practise on test rail/UltrivaQAMilestone/create_milestone.py"
# → copy the printed M<id>

# Step 2 — paste the id as MILESTONE_ID at the top of create_plan.py, then:
# python "Practise on test rail/UltrivaQAMilestone/create_plan.py"
