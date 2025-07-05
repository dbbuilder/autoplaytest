# Fix imports in main_engine.py
# First, let's backup and fix the critical files one by one

import shutil
from pathlib import Path

# Create backup directory
backup_dir = Path("D:/Dev2/autoplaytest/src_backup")
backup_dir.mkdir(exist_ok=True)

# First, let's fix main_engine.py
main_engine_path = Path("D:/Dev2/autoplaytest/src/core/engine/main_engine.py")

# Read the file
with open(main_engine_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the problematic imports
content = content.replace('from ..script_generator.ai_script_generator import', 'from core.script_generator.ai_script_generator import')
content = content.replace('from ..executor.test_executor import', 'from core.executor.test_executor import')
content = content.replace('from ...ai.pattern_analyzer import', 'from ai.pattern_analyzer import')
content = content.replace('from ...monitoring.performance.performance_monitor import', 'from monitoring.performance.performance_monitor import')
content = content.replace('from ...monitoring.errors.error_detector import', 'from monitoring.errors.error_detector import')
content = content.replace('from ...reporting.generators.report_generator import', 'from reporting.generators.report_generator import')
content = content.replace('from ...utils.config_manager import', 'from utils.config_manager import')
content = content.replace('from ...utils.logger import', 'from utils.logger import')
content = content.replace('from ...utils.database import', 'from utils.database import')

# Write the fixed content
with open(main_engine_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed main_engine.py")

# Now fix test_executor.py
test_executor_path = Path("D:/Dev2/autoplaytest/src/core/executor/test_executor.py")

with open(test_executor_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the problematic imports
content = content.replace('from ...utils.logger import', 'from utils.logger import')
content = content.replace('from ...monitoring.performance.performance_monitor import', 'from monitoring.performance.performance_monitor import')
content = content.replace('from ...monitoring.errors.error_detector import', 'from monitoring.errors.error_detector import')

with open(test_executor_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed test_executor.py")

# Fix ai_script_generator.py if it exists
script_gen_path = Path("D:/Dev2/autoplaytest/src/core/script_generator/ai_script_generator.py")
if script_gen_path.exists():
    with open(script_gen_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix any relative imports
    content = content.replace('from ...', 'from ')
    content = content.replace('from ..', 'from core.')
    
    with open(script_gen_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed ai_script_generator.py")

print("\nImports fixed! Now you can run:")
print("python -m src.simple_runner --url http://localhost:5173 --username admin@faithvision.net --password admin123 --mode generate --output-dir ./generated_tests")
