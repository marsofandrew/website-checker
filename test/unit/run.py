#!/usr/bin/python
import os
import shutil
from pathlib import Path

TARGET_DIR = "target"
TARGET_TEST_DIR = "test"


def create_env(root_path, target_dir_path, target_test_dir):
    if os.path.exists(target_dir_path):
        shutil.rmtree(target_dir_path, ignore_errors=True)

    target_test_dir_path = f"{target_dir_path}/{target_test_dir}"

    shutil.copytree(f"{root_path}/src", target_dir_path)
    shutil.copytree(f"{root_path}/test/unit", target_test_dir_path)
    return target_test_dir_path


if __name__ == '__main__':
    root_path = Path(__file__).parent.parent.parent.absolute()

    target_dir_path = f"{root_path}/{TARGET_DIR}"

    create_env(root_path, target_dir_path, TARGET_TEST_DIR)
    print(f"cd {target_dir_path} && python -m unittest discover")
    os.system(f"cd {target_dir_path} && python -m unittest discover test")
