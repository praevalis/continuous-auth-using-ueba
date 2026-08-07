import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from api.main import create_application

REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = REPO_ROOT / 'apps' / 'dashboard'
OUTPUT_PATH = DASHBOARD_DIR / 'src' / 'api' / 'generated' / 'types.ts'


def _resolve_npm_command() -> str:
	for candidate in ('npm.cmd', 'npm'):
		executable = shutil.which(candidate)
		if executable is not None:
			return executable
	raise RuntimeError('Unable to locate npm in PATH.')


def main() -> int:
	app = create_application()
	openapi_schema = app.openapi()

	OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

	with tempfile.TemporaryDirectory() as temp_dir:
		schema_path = Path(temp_dir) / 'openapi.json'
		schema_path.write_text(
			json.dumps(openapi_schema, indent=2),
			encoding='utf-8',
		)

		command = [
			_resolve_npm_command(),
			'exec',
			'--prefix',
			str(DASHBOARD_DIR),
			'openapi-typescript',
			'--',
			str(schema_path),
			'-o',
			str(OUTPUT_PATH),
		]
		result = subprocess.run(command, check=False, cwd=REPO_ROOT)
		return result.returncode


if __name__ == '__main__':
	raise SystemExit(main())
