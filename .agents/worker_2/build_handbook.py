import os
import sys

# Add sections directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sections"))

import sec_header_exec
import sec_part1_phase1
import sec_part2_phase2
import sec_part3_phase3
import sec_part4_phase4
import sec_part5_wins_losses
import sec_part6_toolkits
import sec_part7_post_sih
import sec_part8_checklists

TARGET_PATH = r"c:\Users\mujaw\Downloads\SIH\SIH_GROUND_REALITY_HANDBOOK.md"

def build_handbook():
    print("Assembling Hardened SIH Ground Reality Handbook from modular sections...")
    
    sections = [
        sec_header_exec.CONTENT.strip(),
        sec_part1_phase1.CONTENT.strip(),
        sec_part2_phase2.CONTENT.strip(),
        sec_part3_phase3.CONTENT.strip(),
        sec_part4_phase4.CONTENT.strip(),
        sec_part5_wins_losses.CONTENT.strip(),
        sec_part6_toolkits.CONTENT.strip(),
        sec_part7_post_sih.CONTENT.strip(),
        sec_part8_checklists.CONTENT.strip()
    ]
    
    full_content = "\n\n---\n\n".join(sections) + "\n"
    
    # Write to target file with explicit UTF-8 encoding
    with open(TARGET_PATH, "w", encoding="utf-8") as f:
        f.write(full_content)
        
    print(f"Successfully generated {TARGET_PATH}")
    print(f"Total Characters: {len(full_content)}")
    print(f"Total Lines: {len(full_content.splitlines())}")

if __name__ == "__main__":
    build_handbook()
