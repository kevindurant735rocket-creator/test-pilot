import sys, argparse
from .generator import generate_tests

def main():
    p = argparse.ArgumentParser(prog="test-pilot")
    p.add_argument("file", help="源文件路径 (.py)")
    p.add_argument("-o", "--output", help="输出文件 (默认: test_<filename>)")
    args = p.parse_args()
    if not args.file.endswith(".py"):
        print("只支持 .py 文件"); sys.exit(1)
    output = args.output or f"test_{Path(args.file).name}"
    from pathlib import Path
    result = generate_tests(args.file, output)
    print(f"✓ 生成了 {len([l for l in result.split(chr(10)) if 'def test_' in l])} 个测试")
    print(f"   输出: {output}")

if __name__ == "__main__": main()
