"""
快速验证脚本 - 检查所有依赖是否正确安装
"""
import sys


def check_import(module_name, display_name=None):
    """检查模块是否可以导入"""
    if display_name is None:
        display_name = module_name

    try:
        __import__(module_name)
        print(f"[OK] {display_name}")
        return True
    except ImportError as e:
        print(f"[FAIL] {display_name} - {str(e)}")
        return False


def check_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 11:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[FAIL] Python {version.major}.{version.minor}.{version.micro} (需要 3.11+)")
        return False


def main():
    print("=" * 50)
    print("依赖检查")
    print("=" * 50)

    checks = [
        (lambda: check_version(), "Python 版本"),
        (lambda: check_import("fastapi", "FastAPI"), "FastAPI"),
        (lambda: check_import("uvicorn", "Uvicorn"), "Uvicorn"),
        (lambda: check_import("yt_dlp", "yt-dlp"), "yt-dlp"),
        (lambda: check_import("websockets", "WebSockets"), "WebSockets"),
        (lambda: check_import("pydantic", "Pydantic"), "Pydantic"),
    ]

    results = []
    for check, name in checks:
        print(f"\n检查 {name}...")
        result = check()
        results.append((name, result))

    # 导入服务测试
    print("\n检查应用模块...")
    try:
        from app.services.ytdlp_service import ytdlp_service
        print("[OK] YTDLPService")
        results.append(("YTDLPService", True))
    except Exception as e:
        print(f"[FAIL] YTDLPService - {str(e)}")
        results.append(("YTDLPService", False))

    print("\n" + "=" * 50)
    print("检查结果汇总")
    print("=" * 50)

    all_passed = True
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{name}: {status}")
        if not result:
            all_passed = False

    print("\n" + "=" * 50)
    if all_passed:
        print("[SUCCESS] 所有检查通过！可以启动服务了。")
    else:
        print("[WARNING] 部分检查失败，请检查依赖安装。")
    print("=" * 50)

    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
